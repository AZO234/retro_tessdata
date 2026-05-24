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
KANJI_ROM_PATH   = find_rom('rom/fm77/KANJI.ROM')
OUTPUT_PREFIX    = 'jpn_vert.fm77.exp0'

CHARS_PER_LINE = 50
CELL_SIZE = 32
ROW_H = CELL_SIZE + 2*CELL_PAD  # vert


def get_ank_data(rom, code):
    """ANK コード → 8バイト (8×8px)。"""
    offset = code * 8
    if offset + 8 > len(rom):
        return None
    data = rom[offset:offset + 8]
    return None if all(b == 0 for b in data) else data


def get_kanji_data(rom, jis1, jis2):
    """JIS バイト → 32バイト (16×16px, 順次レイアウト)。
    offset = ((jis1 << 8) | jis2) * 2
    row r: data[r*2]=左8px, data[r*2+1]=右8px, MSB=左端
    """
    offset = ((jis1 << 8) | jis2) * 2
    if offset + 32 > len(rom):
        return None
    data = rom[offset:offset + 32]
    return None if all(b == 0 for b in data) else data


def main():
    if not os.path.exists(SUBSYSC_ROM_PATH):
        print(f"Error: {SUBSYSC_ROM_PATH} not found.")
        return
    if not os.path.exists(KANJI_ROM_PATH):
        print(f"Error: {KANJI_ROM_PATH} not found.")
        return

    with open(SUBSYSC_ROM_PATH, 'rb') as f:
        subsysc = f.read()
    with open(KANJI_ROM_PATH, 'rb') as f:
        kanji_rom = f.read()

    chars_to_train = []
    pua_start = 0xE000
    pua_count = 0

    # 1. ASCII (0x20-0x7E)
    for c in range(0x20, 0x7F):
        data = get_ank_data(subsysc, c)
        if data is None: continue
        chars_to_train.append({'char': chr(c), 'type': 'ank', 'data': data})

    # 3. 半角カナ (0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        data = get_ank_data(subsysc, c)
        if data is None: continue
        try:
            char = bytes([c]).decode('cp932')
        except Exception:
            char = chr(pua_start + pua_count)
            pua_count += 1
        chars_to_train.append({'char': char, 'type': 'ank', 'data': data})

    # 5. 全角 JIS X 0208 (jis1=0x21-0x7E, jis2=0x21-0x7E)
    for jis1 in range(0x21, 0x7F):
        for jis2 in range(0x21, 0x7F):
            data = get_kanji_data(kanji_rom, jis1, jis2)
            if data is None: continue
            try:
                char = unicodedata.normalize('NFC',
                    bytes([jis1 + 0x80, jis2 + 0x80]).decode('euc_jp'))
            except Exception:
                char = chr(pua_start + pua_count)
                pua_count += 1
            chars_to_train.append({'char': char, 'type': 'kanji', 'data': data})

    total_chars = len(chars_to_train)
    num_lines = math.ceil(total_chars / CHARS_PER_LINE)

    print(f"Generating multipage TIF ({num_lines} pages, {total_chars} chars)...")

    for ext in [".tif", ".box", ".lstmf"]:
        fpath = WORK_DIR / f"{OUTPUT_PREFIX}{ext}"
        if os.path.exists(fpath):
            os.remove(fpath)

    rotate_chars = "ー—〜…‥''""「」（）『』【】〔〕〈〉《》［］｛｝"
    shift_chars = "、。ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ"

    all_images = []
    all_box_entries = []
    current_page = 0

    for style_name, repeat in STYLES:
        for _ in range(repeat):
            for l_idx in range(num_lines):
                start = l_idx * CHARS_PER_LINE
                end   = min(start + CHARS_PER_LINE, total_chars)
                line_chars = chars_to_train[start:end]

                line_width = len(line_chars) * (CELL_SIZE + 2*CELL_PAD)
                img = Image.new('L', (line_width, ROW_H), color=0)

                for c_idx, item in enumerate(line_chars):
                    char_img = Image.new('L', (CELL_SIZE, CELL_SIZE), color=0)
                    char_draw = ImageDraw.Draw(char_img)

                    if item['type'] == 'ank':
                        ox = (CELL_SIZE - 8) // 2
                        oy = (CELL_SIZE - 8) // 2
                        for row_idx, byte in enumerate(item['data']):
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    char_draw.point((ox + bit, oy + row_idx), fill=255)
                    else:
                        d = item['data']
                        ox = (CELL_SIZE - 16) // 2
                        oy = (CELL_SIZE - 16) // 2
                        for r in range(16):
                            left  = d[r * 2]
                            right = d[r * 2 + 1]
                            for bit in range(8):
                                if left & (0x80 >> bit):
                                    char_draw.point((ox + bit,     oy + r), fill=255)
                                if right & (0x80 >> bit):
                                    char_draw.point((ox + 8 + bit, oy + r), fill=255)

                    char_img = apply_style(char_img, style_name)
                    if item['char'] in rotate_chars:
                        char_img = char_img.rotate(-90)
                    elif item['char'] in shift_chars:
                        tmp = Image.new('L', (CELL_SIZE, CELL_SIZE), color=0)
                        tmp.paste(char_img, (4, -4))
                        char_img = tmp

                    base_x = c_idx * (CELL_SIZE + 2*CELL_PAD)
                    img.paste(char_img, (base_x + CELL_PAD, CELL_PAD))

                    all_box_entries.append(
                        f"{item['char']} {base_x} 0 {base_x + CELL_SIZE + 2*CELL_PAD} {ROW_H} {current_page}")

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
    _save_imgs[0].save(WORK_DIR / f"{OUTPUT_PREFIX}.tif",
                       save_all=True, append_images=_save_imgs[1:],
                       compression='raw')
    with open(WORK_DIR / f"{OUTPUT_PREFIX}.box", 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_box_entries) + '\n')

    print(f"Done. {OUTPUT_PREFIX}.tif ({current_page} pages), {OUTPUT_PREFIX}.box")


if __name__ == '__main__':
    main()
