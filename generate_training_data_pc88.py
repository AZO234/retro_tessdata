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
KANJI1_ROM_PATH = find_rom('rom/pc88/KANJI1.ROM')
KANJI2_ROM_PATH = find_rom('rom/pc88/fa_kanji2.rom')
OUTPUT_PREFIX = 'jpn.pc88.exp0'

# PC-88 KANJI1.ROM (0x20000 = 128KB) のレイアウト
# - 0x00000-0x007FF: 16dot ASCII (128 chars × 16 bytes)
# - 0x00800-0x00FFF: 16dot ANK 0x80-0xFF (128 chars × 16 bytes, グラフィック記号)
# - 0x01000-0x017FF: 8dot ANK (256 chars × 8 bytes) ← 現状こちらを採用
# - 0x02000-:        第一水準漢字 (JIS row 1-7, 16-47)
#
# KANJI2.ROM (0x20000 = 128KB)
# - 第二水準漢字 (JIS row 48-83 部分)
#
# 漢字アドレス計算式: quasi88 の kanji2addr() 移植 (NP2kai fontpc88.c と等価)
ANK8_OFFSET = 0x1000  # 8x8 ANK セクション (KANJI1.ROM 内)

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
CHAR_H = 16
ROW_H  = CHAR_H + 2*CELL_PAD if TIGHT_PACK else CELL_H


def kanji2addr(code):
    """JIS コード → (rom_idx, row_addr)。
    row_addr * 2 が ROM byte offset。 各行は (L, R) 2バイト構成。
    quasi88 の kanji2addr 関数を移植。"""
    if ((0x2121 <= code <= 0x217e) or
        (0x2221 <= code <= 0x222e) or
        (0x2330 <= code <= 0x2339) or
        (0x2341 <= code <= 0x235a) or
        (0x2361 <= code <= 0x237a) or
        (0x2421 <= code <= 0x2473) or
        (0x2521 <= code <= 0x2576) or
        (0x2621 <= code <= 0x2638) or
        (0x2641 <= code <= 0x2658) or
        (0x2721 <= code <= 0x2741) or
        (0x2751 <= code <= 0x2771)):
        addr = (((code & 0x0060) << 7) | ((code & 0x0700) << 1) | ((code & 0x001f) << 4))
        return 0, addr
    if 0x3021 <= code <= 0x4f53:
        addr = (((code & 0x0060) << 9) | ((code & 0x1f00) << 1) | ((code & 0x001f) << 4))
        return 0, addr
    if 0x5021 <= code <= 0x6f7e:
        addr = (((code & 0x0060) << 9) | ((code & 0x0f00) << 1) | ((code & 0x001f) << 4) | (code & 0x2000))
        return 1, addr
    if 0x7021 <= code <= 0x737e:
        addr = (((code & 0x0060) << 7) | ((code & 0x0700) << 1) | ((code & 0x001f) << 4))
        return 1, addr
    return None, None


def _read_kanji_data(roms, rom_idx, row_addr) -> bytes | None:
    """row_addr から 16 行 × 2 バイト = 32 バイトを抽出。"""
    rom = roms[rom_idx]
    byte_off = row_addr * 2
    if byte_off + 32 > len(rom):
        return None
    return rom[byte_off:byte_off + 32]


def build_char_to_glyph(roms, include_pua: bool = False):
    """ROM 上の有効グリフを列挙し、char → {width, rom_idx, addr, size, fmt} の辞書を返す。

    fmt='ank8'    : 8x8 (8 byte), byte[i] = i行目, MSB=左
    fmt='lr_inter': 16x16 (32 byte), [L0,R0,L1,R1,...] (16行×L/R)
    """
    char_to_glyph: dict[str, dict] = {}
    pua_chars: list[str] = []
    pua_count = 0
    pua_start = 0xE000
    kanji1 = roms[0]

    # ASCII 8x8 (0x20-0x7E)
    for c in range(0x20, 0x7F):
        addr = ANK8_OFFSET + c * 8
        if addr + 8 > len(kanji1):
            continue
        data = kanji1[addr:addr+8]
        if all(b == 0 for b in data) or all(b == 0xFF for b in data):
            continue
        char_to_glyph[chr(c)] = {'width': 8, 'rom_idx': 0, 'addr': addr, 'size': 8, 'fmt': 'ank8'}

    # 半角カナ 8x8 (cp932 0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            ch = bytes([c]).decode('cp932')
        except Exception:
            continue
        addr = ANK8_OFFSET + c * 8
        if addr + 8 > len(kanji1):
            continue
        data = kanji1[addr:addr+8]
        if all(b == 0 for b in data) or all(b == 0xFF for b in data):
            continue
        char_to_glyph[ch] = {'width': 8, 'rom_idx': 0, 'addr': addr, 'size': 8, 'fmt': 'ank8'}

    # 漢字 16x16 (KANJI1/KANJI2)
    for row in range(1, 95):
        for point in range(1, 95):
            jish = row + 0x20
            jisl = point + 0x20
            code = (jish << 8) | jisl
            rom_idx, addr = kanji2addr(code)
            if rom_idx is None:
                continue
            byte_off = addr * 2
            if byte_off + 32 > len(roms[rom_idx]):
                continue
            data = roms[rom_idx][byte_off:byte_off+32]
            if all(b == 0 for b in data) or all(b == 0xFF for b in data):
                continue

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
                char_to_glyph[ch] = {'width': 16, 'rom_idx': rom_idx, 'addr': byte_off, 'size': 32, 'fmt': 'lr_inter'}
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
    for path in [KANJI1_ROM_PATH, KANJI2_ROM_PATH]:
        if not os.path.exists(path):
            print(f"Error: {path} not found.")
            return

    with open(KANJI1_ROM_PATH, 'rb') as f:
        kanji1 = f.read()
    with open(KANJI2_ROM_PATH, 'rb') as f:
        kanji2 = f.read()
    roms = [kanji1, kanji2]

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

    print(f"Generating multipage TIF (PC-88) ({len(lines) * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

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
                        # 8x8 を 16-tall セルの中央に上下padding
                        y_off = (CHAR_H - 8) // 2  # = 4
                        for row_idx, byte in enumerate(data):
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    draw.point((x_pos + bit, y_off + row_idx), fill=255)
                    else:  # lr_inter (16x16, L/R 交互)
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
