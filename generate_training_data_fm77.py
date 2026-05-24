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
SUBSYSC_ROM_PATH = find_rom('rom/fm77/subsys_c.rom')
KANJI_ROM_PATH   = find_rom('rom/fm77/KANJI.ROM')
OUTPUT_PREFIX    = 'jpn.fm77.exp0'

# FM-77 KANJI.ROM (0x20000 = 128KB) のレイアウト
# (NP2kai fontfm7.c fm7knjcpy 移植)
# - row 1-7   (JIS 0x21-0x27, 記号/かな): base 0x00000, sparse with j-block shifts
# - row 16-31 (JIS 0x30-0x3F): base 0x08000
# - row 32-79 (JIS 0x40-0x4F): base 0x14000
# subsys_c.rom (0x2800 = 10KB): ANK 8x8 at offset = code*8
# 漢字グリフ32byte: 各行L,R交互 [L0,R0,L1,R1,...L15,R15]

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2
CHAR_H = 16
ROW_H  = CHAR_H + 2*CELL_PAD if TIGHT_PACK else CELL_H


def kanji_addr(jis_row: int, jisl: int) -> int | None:
    """JIS row (1-94) と jisl (0x21-0x7E) → KANJI.ROM 内 byte offset。
    NP2kai fontfm7.c fm7knjcpy 移植。"""
    i, j = jis_row, jisl
    if 0x01 <= i < 0x08:
        addr = ((j & 0x1f) * 0x20) + (i * 0x400)
        if j >= 0x60:
            addr += 0x2000
        elif j >= 0x40:
            addr += 0x4000
        return addr
    if 0x10 <= i < 0x20:
        return 0x08000 + ((j & 0x1f) * 0x20) + ((i - 0x10) * 0x400) + (((j // 0x20) - 1) * 0x4000)
    if 0x20 <= i < 0x50:
        return 0x14000 + ((j & 0x1f) * 0x20) + ((i - 0x20) * 0x400) + (((j // 0x20) - 1) * 0x4000)
    return None


def build_char_to_glyph(roms, include_pua: bool = False):
    """ROM 上の有効グリフを列挙し、char → {width, rom_idx, addr, size, fmt} の辞書を返す。

    roms = [subsys_c.rom, KANJI.ROM]
    fmt='ank8'    : 8x8 (8 byte), byte[i] = i行目, MSB=左
    fmt='lr_inter': 16x16 (32 byte), [L0,R0,L1,R1,...]
    """
    char_to_glyph: dict[str, dict] = {}
    pua_chars: list[str] = []
    pua_count = 0
    pua_start = 0xE000
    subsysc = roms[0]
    kanji = roms[1]

    def add_ank(ch, code):
        addr = code * 8
        if addr + 8 > len(subsysc):
            return False
        data = subsysc[addr:addr+8]
        if all(b == 0 for b in data) or all(b == 0xFF for b in data):
            return False
        char_to_glyph[ch] = {'width': 8, 'rom_idx': 0, 'addr': addr, 'size': 8, 'fmt': 'ank8'}
        return True

    # ASCII 8x8 (0x20-0x7E)
    for c in range(0x20, 0x7F):
        add_ank(chr(c), c)

    # 半角カナ 8x8 (cp932 0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            ch = bytes([c]).decode('cp932')
        except Exception:
            continue
        add_ank(ch, c)

    # FM-7固有 ANK 規格外領域 (0x00-0x1F, 0x80-0x9F, 0xE0-0xFF) は PUA 扱い
    if include_pua:
        for code in list(range(0x00, 0x20)) + list(range(0x80, 0xA0)) + list(range(0xE0, 0x100)):
            ch = chr(pua_start + pua_count)
            if add_ank(ch, code):
                pua_chars.append(ch)
                pua_count += 1

    # 漢字 16x16 (KANJI.ROM)
    for row in range(1, 95):
        for col in range(0x21, 0x7F):
            addr = kanji_addr(row, col)
            if addr is None:
                continue
            if addr + 32 > len(kanji):
                continue
            data = kanji[addr:addr+32]
            if all(b == 0 for b in data) or all(b == 0xFF for b in data):
                continue

            jish, jisl = row + 0x20, col
            is_pua = False
            try:
                ch = bytes([jish + 0x80, jisl + 0x80]).decode('euc_jp')
            except Exception:
                if not include_pua:
                    continue
                ch = chr(pua_start + pua_count)
                pua_count += 1
                is_pua = True

            if ch not in char_to_glyph:
                char_to_glyph[ch] = {'width': 16, 'rom_idx': 1, 'addr': addr, 'size': 32, 'fmt': 'lr_inter'}
                if is_pua:
                    pua_chars.append(ch)

    return char_to_glyph, pua_chars


# ─────────────── 行ストリーム生成 ───────────────

def iter_lines_charlist(char_to_glyph: dict, limit_chars: int):
    items = sorted(char_to_glyph.items(), key=lambda kv: (kv[1]['rom_idx'], kv[1]['addr']))
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
    for path in [SUBSYSC_ROM_PATH, KANJI_ROM_PATH]:
        if not os.path.exists(path):
            print(f"Error: {path} not found.")
            return

    with open(SUBSYSC_ROM_PATH, 'rb') as f:
        subsysc = f.read()
    with open(KANJI_ROM_PATH, 'rb') as f:
        kanji = f.read()
    roms = [subsysc, kanji]

    include_pua = os.environ.get('RETRO_INCLUDE_PUA', 'false').lower() == 'true'
    char_to_glyph, pua_chars = build_char_to_glyph(roms, include_pua=include_pua)
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

    print(f"Generating multipage TIF (FM-77) ({len(lines) * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

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
                    rom = roms[item['rom_idx']]
                    addr = item['addr']
                    size = item['size']
                    data = rom[addr:addr+size]

                    if item['fmt'] == 'ank8':
                        y_off = (CHAR_H - 8) // 2
                        for row_idx, byte in enumerate(data):
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    draw.point((x_pos + bit, y_off + row_idx), fill=255)
                    else:  # lr_inter
                        y_off = 0 if TIGHT_PACK else PAD_V
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
