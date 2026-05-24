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
FONT_ROM_PATH = find_rom('rom/pc98/FONT.ROM')
OUTPUT_PREFIX = 'jpn.pc98_scan.exp0'

# セクションオフセット
ASCII_OFFSET = 0x00000 
KANA_OFFSET  = 0x00800 
KANJI_OFFSET = 0x01800 

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
ROW_H = CELL_H + 2*CELL_PAD  # scan: kanji fills full height; no height reduction

def get_font_data(rom, offset, index, size):
    addr = offset + (index * size)
    if addr + size > len(rom): return None
    return rom[addr:addr+size]

def main():
    if not os.path.exists(FONT_ROM_PATH):
        print(f"Error: {FONT_ROM_PATH} not found.")
        return
    with open(FONT_ROM_PATH, 'rb') as f: rom = f.read()

    chars_to_train = []
    pua_start = 0xE000
    pua_count = 0

    # 1. ASCII
    for c in range(0x20, 0x7F):
        chars_to_train.append({'char': chr(c), 'width': 8, 'offset': ASCII_OFFSET, 'index': c})
    # 2. 半角カナ
    for c in range(0xA1, 0xE0):
        try:
            char = bytes([c]).decode('cp932')
            chars_to_train.append({'char': char, 'width': 8, 'offset': KANA_OFFSET, 'index': c})
        except: pass
    # 3. 漢字
    jis_candidates = []
    for row in range(1, 95):
        for point in range(1, 95):
            high, low = row + 0x20, point + 0x20
            try:
                char = bytes([high + 0x80, low + 0x80]).decode('euc_jp')
                jis_candidates.append(char)
            except:
                char = chr(pua_start + pua_count)
                jis_candidates.append(char)
                pua_count += 1
    
    for rom_idx, char in enumerate(jis_candidates):
        data = get_font_data(rom, KANJI_OFFSET, rom_idx, 32)
        if data is None:
            break
        if not (all(b == 0 for b in data) or all(b == 0xFF for b in data)):
            chars_to_train.append({'char': char, 'width': 16, 'offset': KANJI_OFFSET, 'index': rom_idx})

    total_chars = len(chars_to_train)
    num_lines = math.ceil(total_chars / CHARS_PER_LINE)

    print(f"Generating multipage TIF (PC-98 Scanlines) ({num_lines * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

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

                line_width = sum(item['width'] + 2*CELL_PAD for item in line_chars)
                img = Image.new('L', (line_width, ROW_H), color=0)
                draw = CellPadDraw(ImageDraw.Draw(img))

                x_pos = 0
                for item in line_chars:
                    size = 32 if item['width'] == 16 else 16
                    font_data = get_font_data(rom, item['offset'], item['index'], size)

                    if font_data:
                        if item['width'] == 16:
                            # 漢字: スキャンライン挿入 (16 -> 32px), CELL_H=32でピッタリ
                            for i in range(16):
                                row_bits = (font_data[i * 2] << 8) | font_data[i * 2 + 1]
                                y = i * 2
                                for bit in range(16):
                                    if row_bits & (0x8000 >> bit):
                                        draw.point((x_pos + bit, y), fill=255)
                        else:
                            # 半角: 通常サイズ (16px), PAD_Vでセンタリング
                            for i in range(16):
                                row_bits = font_data[i]
                                y = (0 if TIGHT_PACK else PAD_V) + i
                                for bit in range(8):
                                    if row_bits & (0x80 >> bit):
                                        draw.point((x_pos + bit, y), fill=255)

                    all_box_entries.append(f"{item['char']} {x_pos} 0 {x_pos + item['width'] + 2*CELL_PAD} {ROW_H} {current_page}")
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

if __name__ == '__main__': main()
