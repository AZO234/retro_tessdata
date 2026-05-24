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

SUBSYSC_ROM_PATH = find_rom('rom/fm77/subsys_c.rom')
KANJI_ROM_PATH   = find_rom('rom/fm77/kanji.rom')
OUTPUT_PREFIX    = 'jpn.fm77_scan.exp0'

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
ROW_H = CELL_H + 2*CELL_PAD  # scan: kanji fills full height; no height reduction


def get_ank_data(rom, code):
    offset = code * 8
    if offset + 8 > len(rom): return None
    data = rom[offset:offset + 8]
    return None if all(b == 0 for b in data) else data


def get_kanji_data(rom, jis1, jis2):
    offset = ((jis1 << 8) | jis2) * 2
    if offset + 32 > len(rom): return None
    data = rom[offset:offset + 32]
    return None if all(b == 0 for b in data) else data


def main():
    if not os.path.exists(SUBSYSC_ROM_PATH):
        print(f"Error: {SUBSYSC_ROM_PATH} not found.")
        return
    if not os.path.exists(KANJI_ROM_PATH):
        print(f"Error: {KANJI_ROM_PATH} not found.")
        return

    with open(SUBSYSC_ROM_PATH, 'rb') as f: subsysc = f.read()
    with open(KANJI_ROM_PATH, 'rb') as f: kanji_rom = f.read()

    chars_to_train = []
    pua_start = 0xE000
    pua_count = 0

    # 1. ASCII (0x20-0x7E)
    for c in range(0x20, 0x7F):
        data = get_ank_data(subsysc, c)
        if data: chars_to_train.append({'char': chr(c), 'type': 'ank', 'data': data})

    # 3. 半角カナ (0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        data = get_ank_data(subsysc, c)
        if data:
            try: char = bytes([c]).decode('cp932')
            except:
                char = chr(pua_start + pua_count)
                pua_count += 1
            chars_to_train.append({'char': char, 'type': 'ank', 'data': data})

    # 5. 全角 JIS X 0208
    for jis1 in range(0x21, 0x7F):
        for jis2 in range(0x21, 0x7F):
            data = get_kanji_data(kanji_rom, jis1, jis2)
            if data:
                try: char = unicodedata.normalize('NFC', bytes([jis1 + 0x80, jis2 + 0x80]).decode('euc_jp'))
                except:
                    char = chr(pua_start + pua_count)
                    pua_count += 1
                chars_to_train.append({'char': char, 'type': 'kanji', 'data': data})

    total_chars = len(chars_to_train)
    num_lines = math.ceil(total_chars / CHARS_PER_LINE)

    print(f"Generating multipage TIF (Kanji with scanlines) ({num_lines * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

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
                end   = min(start + CHARS_PER_LINE, total_chars)
                line_chars = chars_to_train[start:end]

                img_w = sum((8 if item['type'] == 'ank' else 16) + 2*CELL_PAD for item in line_chars)
                img = Image.new('L', (img_w, ROW_H), color=0)
                draw = CellPadDraw(ImageDraw.Draw(img))

                x_pos = 0
                for item in line_chars:
                    if item['type'] == 'ank':
                        ox = x_pos
                        oy = (CELL_H - 8) // 2
                        for r, byte in enumerate(item['data']):
                            for bit in range(8):
                                if byte & (0x80 >> bit): draw.point((ox + bit, oy + r), fill=255)
                    else:
                        ox = x_pos
                        oy = 0
                        for r in range(16):
                            left, right = item['data'][r*2], item['data'][r*2+1]
                            y = oy + r * 2
                            for bit in range(8):
                                if left  & (0x80 >> bit): draw.point((ox + bit,     y), fill=255)
                                if right & (0x80 >> bit): draw.point((ox + 8 + bit, y), fill=255)

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

    print(f"Done. {OUTPUT_PREFIX}.tif, {OUTPUT_PREFIX}.box")

if __name__ == '__main__': main()
