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
CGROM_PATH = find_rom('rom/x68k/CGROM.DAT')
OUTPUT_PREFIX = 'jpn.x68k.exp0'

# X68000 CGROM.DAT のレイアウト (NP2kai fontx68k.c 由来)
# - 0x00000-0x05240: 漢字Block1 (JIS row 1-7)
# - 0x05e00-0x1d600: 漢字Block2 (JIS row 16-47, 第一水準漢字)
# - 0x1d600-0x3a100: 漢字Block3 (JIS row 48-83 + row 84部分)
# - 0x3a100-:        8dot ANK (8x8) ※学習対象外
# - 0x3aa00-:        16dot ASCII (code 0x20-0x7F, 16byte/char)
# - 0x3b200-:        16dot 半角カナ (code 0xA0-0xDF, 64chars × 16byte)
# 漢字グリフ32byteの内部配置: 各行L,Rが交互 [L0,R0,L1,R1,...L15,R15]
# ASCII と 半角カナ で参照用ベースは偶然同一: 0x3A800 + code*16
ANK_BASE = 0x3A800
KANJI_BLOCK1_BASE = 0x00000        # row 1-7
KANJI_BLOCK2_BASE = 0x05E00        # row 16-47
KANJI_BLOCK3_BASE = 0x1D600        # row 48-83 (+row84 部分)
KANJI_COL_COUNT   = 0x5E           # = 94 cols per row

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
CHAR_H = 16
ROW_H  = CHAR_H + 2*CELL_PAD if TIGHT_PACK else CELL_H


def kanji_addr(jis_row: int, jis_col: int) -> int | None:
    """JIS row(1-94) と JIS col(0x21-0x7E) から CGROM内の漢字アドレスを返す。
    収録されていない領域は None。"""
    i, j = jis_row, jis_col
    if 0x01 <= i < 0x08:
        return KANJI_BLOCK1_BASE + (((i - 0x01) * KANJI_COL_COUNT) + (j - 0x21)) * 0x20
    if 0x10 <= i < 0x30:
        return KANJI_BLOCK2_BASE + (((i - 0x10) * KANJI_COL_COUNT) + (j - 0x21)) * 0x20
    if 0x30 <= i < 0x54:
        return KANJI_BLOCK3_BASE + (((i - 0x30) * KANJI_COL_COUNT) + (j - 0x21)) * 0x20
    if i == 0x54 and j < 0x25:
        return KANJI_BLOCK3_BASE + (((0x54 - 0x30) * KANJI_COL_COUNT) + (j - 0x21)) * 0x20
    return None


def build_char_to_glyph(rom, include_pua: bool = False):
    """ROM 上の有効グリフを列挙し、char → {width, addr, size, fmt} の辞書を返す。

    fmt='ank'    : 8x16, 16 byte, ピクセル = byte[i] のビット
    fmt='x68k_k' : 16x16, 32 byte, ピクセル = byte[i*2..i*2+1] (L,R交互)
    """
    char_to_glyph: dict[str, dict] = {}
    pua_count = 0
    pua_chars: list[str] = []

    # ASCII 8x16: addr = ANK_BASE + code*16  (code=0x20-0x7E)
    for c in range(0x20, 0x7F):
        addr = ANK_BASE + c * 16
        if addr + 16 > len(rom):
            continue
        data = rom[addr:addr+16]
        if all(b == 0 for b in data):
            continue
        char_to_glyph[chr(c)] = {'width': 8, 'addr': addr, 'size': 16, 'fmt': 'ank'}

    # 半角カナ 8x16: addr = ANK_BASE + code*16 (code=0xA1-0xDF, cp932)
    for c in range(0xA1, 0xE0):
        try:
            ch = bytes([c]).decode('cp932')
        except Exception:
            continue
        addr = ANK_BASE + c * 16
        if addr + 16 > len(rom):
            continue
        data = rom[addr:addr+16]
        if all(b == 0 for b in data):
            continue
        char_to_glyph[ch] = {'width': 8, 'addr': addr, 'size': 16, 'fmt': 'ank'}

    # 漢字 16x16 (3 ブロック構成)
    pua_start = 0xE000
    for row in range(1, 95):
        for col in range(0x21, 0x7F):
            addr = kanji_addr(row, col)
            if addr is None:
                continue
            if addr + 32 > len(rom):
                continue
            jish, jisl = row + 0x20, col
            is_pua = False
            try:
                ch = bytes([jish + 0x80, jisl + 0x80]).decode('euc_jp')
            except Exception:
                if not include_pua:
                    pua_count += 1
                    continue
                ch = chr(pua_start + pua_count)
                pua_count += 1
                is_pua = True

            data = rom[addr:addr+32]
            if all(b == 0 for b in data) or all(b == 0xFF for b in data):
                continue

            if ch not in char_to_glyph:
                char_to_glyph[ch] = {'width': 16, 'addr': addr, 'size': 32, 'fmt': 'x68k_k'}
                if is_pua:
                    pua_chars.append(ch)

    return char_to_glyph, pua_chars


# ─────────────── 行ストリーム生成 ───────────────

def iter_lines_charlist(char_to_glyph: dict, limit_chars: int):
    """旧仕様: addr 順 char 列を CHARS_PER_LINE で区切ったストリーム。"""
    items = sorted(char_to_glyph.items(), key=lambda kv: kv[1]['addr'])
    seq = [ch for ch, _ in items]
    if limit_chars > 0:
        seq = seq[:limit_chars]
    for i in range(0, len(seq), CHARS_PER_LINE):
        yield seq[i:i+CHARS_PER_LINE]


def iter_lines_corpus(corpus_path: str, char_to_glyph: dict, pua_chars: list,
                       max_lines: int):
    """実文章コーパスから ≤CHARS_PER_LINE の行ストリームを生成。"""
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
    if not os.path.exists(CGROM_PATH):
        print(f"Error: {CGROM_PATH} not found.")
        return

    with open(CGROM_PATH, 'rb') as f:
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

    print(f"Generating multipage TIF (X68k) ({len(lines) * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

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
                    else:  # x68k_k (16x16, L/R 交互)
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
