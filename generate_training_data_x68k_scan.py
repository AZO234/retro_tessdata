import os
import math
import unicodedata
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

CGROM_PATH = find_rom('rom/x68k/CGROM.DAT')
ANK_OFFSET = 0x3A800  # ANK (8×16) セクション開始
OUTPUT_PREFIX = 'jpn.x68k_scan.exp0'

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
ROW_H = CELL_H + 2*CELL_PAD  # scan: kanji fills full height; no height reduction


def get_fwchar_rows(cgrom, jis_row, jis_col):
    """JIS row/col → 16行分の (高位バイト, 低位バイト)。ANK 領域に重なる場合は None。"""
    offset = ((jis_row - 1) * 94 + (jis_col - 1)) * 32
    if offset + 32 > ANK_OFFSET:
        return None
    return [(cgrom[offset + i * 2], cgrom[offset + i * 2 + 1]) for i in range(16)]


def get_ank_data(cgrom, code):
    """ANK コード → 16バイト (8×16px)。"""
    offset = ANK_OFFSET + code * 16
    if offset + 16 > len(cgrom):
        return None
    return cgrom[offset:offset + 16]


def main():
    if not os.path.exists(CGROM_PATH):
        print(f"Error: {CGROM_PATH} not found.")
        return

    with open(CGROM_PATH, 'rb') as f:
        cgrom = f.read()

    chars_to_train = []
    pua_start = 0xE000
    pua_count = 0

    # 1. ASCII (0x20-0x7E)
    for c in range(0x20, 0x7F):
        data = get_ank_data(cgrom, c)
        if data and not all(b == 0 for b in data):
            chars_to_train.append({'char': chr(c), 'type': 'ank', 'data': data})

    # 2. 半角カナ (0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            char = bytes([c]).decode('cp932')
        except Exception:
            continue
        data = get_ank_data(cgrom, c)
        if data and not all(b == 0 for b in data):
            chars_to_train.append({'char': char, 'type': 'ank', 'data': data})

    # 3. JIS X 0208 全角
    for row in range(1, 95):
        for col in range(1, 95):
            rows = get_fwchar_rows(cgrom, row, col)
            if rows is None:
                break
            if all(high == 0 and low == 0 for high, low in rows):
                continue
            high_b, low_b = row + 0x20, col + 0x20
            try:
                char = unicodedata.normalize('NFC', bytes([high_b + 0x80, low_b + 0x80]).decode('euc_jp'))
            except Exception:
                char = chr(pua_start + pua_count)
                pua_count += 1
            chars_to_train.append({'char': char, 'type': 'kanji', 'rows': rows})

    total_chars = len(chars_to_train)
    num_lines = math.ceil(total_chars / CHARS_PER_LINE)

    print(f"Generating multipage TIF with scanlines (Kanji only) for X68k ({num_lines} pages, {total_chars} chars)...")

    for ext in [".tif", ".box", ".lstmf"]:
        fpath = WORK_DIR / f"{OUTPUT_PREFIX}{ext}"
        if os.path.exists(fpath):
            os.remove(fpath)

    all_images = []
    all_box_entries = []
    current_page = 0

    for style_name, repeat in STYLES:
        for _ in range(repeat):
            for l_idx in range(num_lines):
                start = l_idx * CHARS_PER_LINE
                end = min(start + CHARS_PER_LINE, total_chars)
                line_chars = chars_to_train[start:end]

                line_width = sum((8 if item['type'] == 'ank' else 16) + 2*CELL_PAD for item in line_chars)
                img = Image.new('L', (line_width, ROW_H), color=0)
                draw = CellPadDraw(ImageDraw.Draw(img))

                x_pos = 0
                for item in line_chars:

                    if item['type'] == 'ank':
                        # 半角: 通常サイズ (16px)
                        offset_x = x_pos
                        offset_y = 0 if TIGHT_PACK else PAD_V
                        for row_idx, byte in enumerate(item['data']):
                            y = offset_y + row_idx
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    draw.point((offset_x + bit, y), fill=255)
                    else:
                        # 全角: スキャンライン挿入 (16 -> 32px)
                        offset_x = x_pos
                        offset_y = 0
                        for row_idx, (high, low) in enumerate(item['rows']):
                            y = offset_y + row_idx * 2
                            for bit in range(8):
                                if high & (0x80 >> bit):
                                    draw.point((offset_x + bit, y), fill=255)
                                if low & (0x80 >> bit):
                                    draw.point((offset_x + 8 + bit, y), fill=255)

                    item_w = 8 if item['type'] == 'ank' else 16
                    all_box_entries.append(f"{item['char']} {x_pos} 0 {x_pos + item_w + 2*CELL_PAD} {ROW_H} {current_page}")
                    x_pos += item_w + 2*CELL_PAD

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
            _c, _n = _e[0], _e[2:].split()  # char is always 1 codepoint; avoids split() dropping space char
            _dy = _yo[int(_n[4])]
            _new_box.append(
                f"{_c} {_n[0]} {int(_n[1])+_dy} {_n[2]} {int(_n[3])+_dy} 0")
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
