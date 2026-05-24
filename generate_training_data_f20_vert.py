import os
import math
import unicodedata as ud
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


FONT_ROM_PATH = find_rom('rom/fmt/FMT_F20.ROM')
OUTPUT_PREFIX = 'jpn_vert.f20.exp0'

CHARS_PER_LINE = 50
CELL_SIZE = 24
ROW_H = CELL_SIZE + 2*CELL_PAD  # vert
F20_BASE   = 0x2810
F20_STRIDE = 60  # 3バイト/行 × 20行 (20×20px)


def get_char_data(rom, jis1, jis2):
    addr = F20_BASE + ((jis1 - 0x21) * 94 + (jis2 - 0x21)) * F20_STRIDE
    if addr + F20_STRIDE > len(rom):
        return None
    data = rom[addr:addr + F20_STRIDE]
    return None if all(b == 0 for b in data) else data


def main():
    if not os.path.exists(FONT_ROM_PATH):
        print(f"Error: {FONT_ROM_PATH} not found.")
        return

    with open(FONT_ROM_PATH, 'rb') as f:
        rom = f.read()

    chars_to_train = []
    pua_start = 0xE000
    pua_count = 0

    for jis1 in range(0x21, 0x7F):
        for jis2 in range(0x21, 0x7F):
            data = get_char_data(rom, jis1, jis2)
            if data is None:
                continue
            try:
                char = ud.normalize('NFC',
                    bytes([jis1 + 0x80, jis2 + 0x80]).decode('euc_jp'))
            except Exception:
                char = chr(pua_start + pua_count)
                pua_count += 1
            if ud.category(char) == 'Zs':
                continue
            chars_to_train.append({'char': char, 'data': data})

    total_chars = len(chars_to_train)
    num_lines   = math.ceil(total_chars / CHARS_PER_LINE)

    print(f"Generating multipage TIF (F20 Vertical) ({num_lines * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

    for _ext in ['.tif', '.box', '.lstmf']:
        (WORK_DIR / f"{OUTPUT_PREFIX}{_ext}").unlink(missing_ok=True)

    rotate_chars = "ー—…‥「」」（）『』【】〔〕〈〉《》［］｛｝"
    shift_chars  = "、。ぁぃぅぇぉっゃゅょゎァィゥェォッャュョヮヵヶ"

    all_images = []
    all_box_entries = []
    current_page = 0

    for style_name, repeat in STYLES:
        for _ in range(repeat):
            for l_idx in range(num_lines):
                start      = l_idx * CHARS_PER_LINE
                end        = min(start + CHARS_PER_LINE, total_chars)
                line_chars = chars_to_train[start:end]

                line_height = len(line_chars) * (CELL_SIZE + 2*CELL_PAD)
                img = Image.new('L', (CELL_SIZE + 2*CELL_PAD, line_height), color=0)

                for c_idx, item in enumerate(line_chars):
                    char_img  = Image.new('L', (CELL_SIZE, CELL_SIZE), color=0)
                    char_draw = ImageDraw.Draw(char_img)

                    ox = (CELL_SIZE - 20) // 2
                    oy = (CELL_SIZE - 20) // 2
                    d  = item['data']
                    for r in range(20):
                        val = (d[r*3] << 16) | (d[r*3+1] << 8) | d[r*3+2]
                        for bit in range(20):
                            if val & (0x800000 >> bit):
                                char_draw.point((ox + bit, oy + r), fill=255)

                    char_img = apply_style(char_img, style_name)
                    if item['char'] in rotate_chars:
                        char_img = char_img.rotate(-90)
                    elif item['char'] in shift_chars:
                        tmp = Image.new('L', (CELL_SIZE, CELL_SIZE), color=0)
                        tmp.paste(char_img, (4, -4))
                        char_img = tmp

                    base_y = c_idx * (CELL_SIZE + 2*CELL_PAD)
                    img.paste(char_img, (CELL_PAD, base_y + CELL_PAD))

                    all_box_entries.append(f"{item['char']} 0 {base_y} {CELL_SIZE + 2*CELL_PAD} {base_y + CELL_SIZE + 2*CELL_PAD} {current_page}")

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
