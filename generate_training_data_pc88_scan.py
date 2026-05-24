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

KANJI1_ROM_PATH = find_rom('rom/pc88/KANJI1.ROM')
KANJI2_ROM_PATH = find_rom('rom/pc88/fa_kanji2.rom')

ANK_OFFSET = 0x1000
OUTPUT_PREFIX = 'jpn.pc88_scan.exp0'

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
ROW_H = CELL_H + 2*CELL_PAD  # scan: kanji fills full height; no height reduction


def kanji2addr(code):
    """JIS コード → (rom_idx, addr)。quasi88 の kanji2addr 関数を移植。"""
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
    elif 0x3021 <= code <= 0x4f53:
        addr = (((code & 0x0060) << 9) | ((code & 0x1f00) << 1) | ((code & 0x001f) << 4))
        return 0, addr
    elif 0x5021 <= code <= 0x6f7e:
        addr = (((code & 0x0060) << 9) | ((code & 0x0f00) << 1) | ((code & 0x001f) << 4) | (code & 0x2000))
        return 1, addr
    elif 0x7021 <= code <= 0x737e:
        addr = (((code & 0x0060) << 7) | ((code & 0x0700) << 1) | ((code & 0x001f) << 4))
        return 1, addr
    return None, None


def get_kanji_rows(kanji_roms, rom_idx, addr):
    """16行分の (左バイト, 右バイト) リストを返す。"""
    rom = kanji_roms[rom_idx]
    rows = []
    for i in range(16):
        offset = (addr + i) * 2
        if offset + 1 >= len(rom):
            return None
        rows.append((rom[offset], rom[offset + 1]))
    return rows


def main():
    for path in [KANJI1_ROM_PATH, KANJI2_ROM_PATH]:
        if not os.path.exists(path):
            print(f"Error: {path} not found.")
            return

    with open(KANJI1_ROM_PATH, 'rb') as f:
        kanji1 = f.read()
    with open(KANJI2_ROM_PATH, 'rb') as f:
        kanji2 = f.read()
    kanji_roms = [kanji1, kanji2]

    chars_to_train = []
    pua_start = 0xE000
    pua_count = 0

    # 1. ASCII (0x20-0x7E)
    for c in range(0x20, 0x7F):
        data = kanji1[ANK_OFFSET + c * 8 : ANK_OFFSET + c * 8 + 8]
        if not all(b == 0 for b in data):
            chars_to_train.append({'char': chr(c), 'type': 'ank', 'data': bytes(data)})

    # 2. 半角カナ (0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            char = bytes([c]).decode('cp932')
        except Exception:
            continue
        data = kanji1[ANK_OFFSET + c * 8 : ANK_OFFSET + c * 8 + 8]
        if not all(b == 0 for b in data):
            chars_to_train.append({'char': char, 'type': 'ank', 'data': bytes(data)})

    # 3. JIS X 0208 (KANJI1/KANJI2 ROM) — スキャンライン付き 16×32 で描画
    for row in range(1, 95):
        for point in range(1, 95):
            high, low = row + 0x20, point + 0x20
            jis_code = (high << 8) | low
            rom_idx, addr = kanji2addr(jis_code)
            if rom_idx is None:
                continue
            rows = get_kanji_rows(kanji_roms, rom_idx, addr)
            if rows is None or all(left == 0 and right == 0 for left, right in rows):
                continue
            try:
                char = bytes([high + 0x80, low + 0x80]).decode('euc_jp')
            except Exception:
                char = chr(pua_start + pua_count)
                pua_count += 1
            chars_to_train.append({'char': char, 'type': 'kanji', 'rows': rows})

    total_chars = len(chars_to_train)
    num_lines = math.ceil(total_chars / CHARS_PER_LINE)

    print(f"Generating multipage TIF ({num_lines} pages, {total_chars} chars, kanji with scanlines)...")

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
                        offset_x = x_pos
                        offset_y = (CELL_H - 8) // 2
                        for row_idx, byte in enumerate(item['data']):
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    draw.point((offset_x + bit, offset_y + row_idx), fill=255)
                    else:
                        offset_x = x_pos
                        offset_y = 0
                        for row_idx, (left, right) in enumerate(item['rows']):
                            y = offset_y + row_idx * 2
                            for bit in range(8):
                                if left & (0x80 >> bit):
                                    draw.point((offset_x + bit, y), fill=255)
                                if right & (0x80 >> bit):
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
