import os
import math
from PIL import Image, ImageDraw
from style_utils import STYLES, apply_style, finalize_line, SINGLE_PAGE, TIGHT_PACK, CELL_PAD, CellPadDraw, WORK_DIR


def find_rom(path):
    if os.path.exists(path):
        return path
    d, name = os.path.dirname(path) or '.', os.path.basename(path)
    try:
        for n in os.listdir(d):
            if n.lower() == name.lower():
                return os.path.join(d, n)
    except OSError:
        pass
    return path


# 設定
FONT_ROM_PATH = find_rom('rom/fmt/FMT_FNT.ROM')
OUTPUT_PREFIX = 'jpn.fmt.exp0'

# FM-TOWNS FMT_FNT.ROM (0x40000 = 256KB) のレイアウト
# (TOWNSEMU physmem.h FontROMCode() より移植)
# - 0x00000-0x003FF: 非漢字ブロック (32x8 cells, 2ブロック)
# - 0x00400-:        漢字 16x16 (32×16 cells, BlkY*3+BlkX のブロック化)
# - 0x3D800-0x3FFFF: ANK 8x16 (256 chars × 16 bytes)
# 漢字グリフ32byteの内部配置: 各行L,Rが交互 [L0,R0,L1,R1,...L15,R15]
ANK16_BASE = 0x3D800

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
CHAR_H = 16
ROW_H  = CHAR_H + 2*CELL_PAD if TIGHT_PACK else CELL_H


def font_rom_code(jis1, jis2):
    """JISコード → fontRomインデックス。TOWNSEMU physmem.h FontROMCode() 移植。"""
    if jis1 < 0x28:
        # 非漢字ブロック (32×8)
        BLK = (jis2 - 0x20) >> 5
        x   = jis2 & 0x1F
        y   = jis1 & 7
        if BLK == 1:
            BLK = 2
        elif BLK == 2:
            BLK = 1
        return BLK * 32 * 8 + y * 32 + x
    else:
        # 漢字ブロック (32×16)
        BlkX = (jis2 - 0x20) >> 5
        BlkY = (jis1 - 0x30) >> 4
        BLK  = BlkY * 3 + BlkX
        x    = jis2 & 0x1F
        y    = jis1 & 0x0F
        return 0x400 + BLK * 32 * 16 + y * 32 + x


def kanji_addr(jis1, jis2):
    """JIS → ROM内アドレス (32バイト先頭)。"""
    code = font_rom_code(jis1, jis2) & 0x1FFF
    return 32 * code


def build_char_to_glyph(rom, include_pua: bool = False):
    """ROM 上の有効グリフを列挙し、char → {width, addr, size, fmt} の辞書を返す。

    fmt='ank'      : 8x16, 16byte, byte[i] = i行目, MSB=左
    fmt='lr_inter' : 16x16, 32byte, byte[i*2..i*2+1] = i行目L,R, MSB=左
    """
    char_to_glyph: dict[str, dict] = {}
    pua_chars: list[str] = []
    pua_count = 0
    pua_start = 0xE000

    def add_ank(ch, code):
        addr = ANK16_BASE + code * 16
        if addr + 16 > len(rom):
            return False
        data = rom[addr:addr+16]
        if all(b == 0 for b in data) or all(b == 0xFF for b in data):
            return False
        char_to_glyph[ch] = {'width': 8, 'addr': addr, 'size': 16, 'fmt': 'ank'}
        return True

    # ASCII 8x16 (0x20-0x7E)
    for c in range(0x20, 0x7F):
        add_ank(chr(c), c)

    # 半角カナ 8x16 (cp932 0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            ch = bytes([c]).decode('cp932')
        except Exception:
            continue
        add_ank(ch, c)

    # ANK の規格外領域 (0x00-0x1F, 0x80-0x9F, 0xE0-0xFF) は PUA 扱い
    if include_pua:
        for code in list(range(0x00, 0x20)) + list(range(0x80, 0xA0)) + list(range(0xE0, 0x100)):
            ch = chr(pua_start + pua_count)
            if add_ank(ch, code):
                pua_chars.append(ch)
                pua_count += 1

    # 漢字 16x16 (JIS X 0208: jis1=0x21-0x7E, jis2=0x21-0x7E)
    for jis1 in range(0x21, 0x7F):
        for jis2 in range(0x21, 0x7F):
            addr = kanji_addr(jis1, jis2)
            if addr + 32 > len(rom):
                continue
            data = rom[addr:addr+32]
            if all(b == 0 for b in data) or all(b == 0xFF for b in data):
                continue

            is_pua = False
            try:
                ch = bytes([jis1 + 0x80, jis2 + 0x80]).decode('euc_jp')
            except Exception:
                if not include_pua:
                    continue
                ch = chr(pua_start + pua_count)
                pua_count += 1
                is_pua = True

            if ch not in char_to_glyph:
                char_to_glyph[ch] = {'width': 16, 'addr': addr, 'size': 32, 'fmt': 'lr_inter'}
                if is_pua:
                    pua_chars.append(ch)

    return char_to_glyph, pua_chars


# ─────────────── 行ストリーム生成 ───────────────

def iter_lines_charlist(char_to_glyph: dict, limit_chars: int):
    items = sorted(char_to_glyph.items(), key=lambda kv: kv[1]['addr'])
    seq = [ch for ch, _ in items]
    if limit_chars > 0:
        seq = seq[:limit_chars]
    for i in range(0, len(seq), CHARS_PER_LINE):
        yield seq[i:i+CHARS_PER_LINE]


def iter_lines_corpus(corpus_path: str, char_to_glyph: dict, pua_chars: list,
                       max_lines: int):
    text = open(corpus_path, encoding='utf-8').read()
    renderable = set(char_to_glyph.keys())
    yielded = 0

    for raw_line in text.split('\n'):
        filtered = [c for c in raw_line if c in renderable]
        if not filtered:
            continue
        for i in range(0, len(filtered), CHARS_PER_LINE):
            chunk = filtered[i:i+CHARS_PER_LINE]
            yield chunk
            yielded += 1
            if max_lines > 0 and yielded >= max_lines:
                break
        if max_lines > 0 and yielded >= max_lines:
            break

    if pua_chars:
        for i in range(0, len(pua_chars), CHARS_PER_LINE):
            yield pua_chars[i:i+CHARS_PER_LINE]


def main():
    if not os.path.exists(FONT_ROM_PATH):
        print(f"Error: {FONT_ROM_PATH} not found.")
        return

    with open(FONT_ROM_PATH, 'rb') as f:
        rom = f.read()

    include_pua = os.environ.get('RETRO_INCLUDE_PUA', 'false').lower() == 'true'
    char_to_glyph, pua_chars = build_char_to_glyph(rom, include_pua=include_pua)
    print(f'描画可能文字: {len(char_to_glyph)} (うち PUA: {len(pua_chars)}, include_pua={include_pua})')

    corpus_path = os.environ.get('RETRO_CORPUS_PATH', '').strip()
    max_lines   = int(os.environ.get('RETRO_MAX_LINES', '10000'))
    limit_chars = int(os.environ.get('RETRO_LIMIT_CHARS', '0'))

    if corpus_path:
        if not os.path.exists(corpus_path):
            print(f'Error: corpus not found: {corpus_path}')
            return
        print(f'コーパスモード: {corpus_path}  (max_lines={max_lines})')
        line_iter = iter_lines_corpus(corpus_path, char_to_glyph, pua_chars, max_lines)
    else:
        print('レガシーモード: 辞書順char list')
        line_iter = iter_lines_charlist(char_to_glyph, limit_chars)

    lines = list(line_iter)
    total_chars = sum(len(l) for l in lines)
    print(f'生成行数: {len(lines)} / 総文字数: {total_chars}')

    print(f"Generating multipage TIF (FM-TOWNS) ({len(lines) * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

    for ext in [".tif", ".box", ".lstmf"]:
        fpath = WORK_DIR / f"{OUTPUT_PREFIX}{ext}"
        if os.path.exists(fpath):
            os.remove(fpath)

    all_images = []
    all_box_entries = []
    current_page = 0

    # スタイル横断インターリーブ: 各行を全style分連続生成し、ドメイン切替shockを回避
    for line_chars_src in lines:
        line_chars = [{'char': ch, **char_to_glyph[ch]} for ch in line_chars_src]
        if not line_chars:
            continue

        line_width = sum(item['width'] + 2*CELL_PAD for item in line_chars)

        for style_name, repeat in STYLES:
            for _ in range(repeat):
                img = Image.new('L', (line_width, ROW_H), color=0)
                draw = CellPadDraw(ImageDraw.Draw(img))

                x_pos = 0
                for item in line_chars:
                    addr = item['addr']
                    size = item['size']
                    data = rom[addr:addr+size]
                    y_off = 0 if TIGHT_PACK else PAD_V

                    if item['fmt'] == 'ank':
                        for row_idx in range(16):
                            byte = data[row_idx]
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    draw.point((x_pos + bit, y_off + row_idx), fill=255)
                    else:  # lr_inter (16x16, L/R 交互)
                        for row_idx in range(16):
                            L = data[row_idx * 2]
                            R = data[row_idx * 2 + 1]
                            row_bits = (L << 8) | R
                            for bit in range(16):
                                if row_bits & (0x8000 >> bit):
                                    draw.point((x_pos + bit, y_off + row_idx), fill=255)

                    all_box_entries.append(
                        f"{item['char']} {x_pos} 0 {x_pos + item['width'] + 2*CELL_PAD} {ROW_H} {current_page}")
                    x_pos += item['width'] + 2*CELL_PAD

                img = apply_style(img, style_name)
                all_images.append(finalize_line(img))
                current_page += 1

    if SINGLE_PAGE:
        _ph = [img.height for img in all_images]
        _yo = [sum(_ph[:i]) for i in range(len(_ph))]
        _cw = max(img.width for img in all_images)
        _cv = Image.new('L', (_cw, sum(_ph)), color=0)
        for _i, _im in enumerate(all_images):
            _cv.paste(_im, (0, _yo[_i]))
        _out = _cv
        _out.save(WORK_DIR / f"{OUTPUT_PREFIX}.tif", compression='raw')
        _new_box = []
        for _e in all_box_entries:
            _c, _n = _e[0], _e[2:].split()
            _dy = _yo[int(_n[4])]
            _new_box.append(f"{_c} {_n[0]} {int(_n[1])+_dy} {_n[2]} {int(_n[3])+_dy} 0")
        with open(WORK_DIR / f"{OUTPUT_PREFIX}.box", 'w', encoding='utf-8') as f:
            f.write('\n'.join(_new_box) + '\n')
        print(f"Done (single-page). {OUTPUT_PREFIX}.tif, {OUTPUT_PREFIX}.box")
        return
    _save_imgs = list(all_images)
    _save_imgs[0].save(WORK_DIR / f"{OUTPUT_PREFIX}.tif", save_all=True, append_images=_save_imgs[1:], compression='raw')
    with open(WORK_DIR / f"{OUTPUT_PREFIX}.box", 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_box_entries) + '\n')

    print(f"Done. {OUTPUT_PREFIX}.tif ({current_page} pages), {OUTPUT_PREFIX}.box")


if __name__ == '__main__':
    main()
