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

try:
    from msx_charmap import CHAR_OVERRIDES, ROW0_OVERRIDES, ANK_EXT_OVERRIDES
except ImportError:
    CHAR_OVERRIDES = {}
    ROW0_OVERRIDES = {}
    ANK_EXT_OVERRIDES = {}

KANJI_ROM_PATH = find_rom('rom/msx/fs-a1gt_kanjifont.rom')
ANK_PATH       = find_rom('rom/msx/JAPANESE.FNT')
OUTPUT_PREFIX  = 'jpn.msx_scan.exp0'

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
ROW_H = CELL_H + 2*CELL_PAD  # scan: kanji fills full height; no height reduction


def get_ank_data(fnt, code):
    """ANK コード → 8バイト (8×8px)。"""
    offset = code * 8
    if offset + 8 > len(fnt):
        return None
    data = fnt[offset:offset + 8]
    return None if all(b == 0 for b in data) else data


def get_kanji_data(rom, jis1, jis2):
    """JIS バイト → 32バイト (16×16px, 4象限レイアウト)。
    レイアウト: bytes 0-7 = rows 0-7 左半, bytes 8-15 = rows 0-7 右半,
                bytes 16-23 = rows 8-15 左半, bytes 24-31 = rows 8-15 右半
    """
    offset = (jis1 - 0x20) * 2048 + (jis2 - 0x20) * 32
    if offset + 32 > len(rom):
        return None
    data = rom[offset:offset + 32]
    return None if all(b == 0 for b in data) else data


def main():
    if not os.path.exists(KANJI_ROM_PATH):
        print(f"Error: {KANJI_ROM_PATH} not found.")
        return
    if not os.path.exists(ANK_PATH):
        print(f"Error: {ANK_PATH} not found.")
        return

    with open(KANJI_ROM_PATH, 'rb') as f:
        rom = f.read()
    with open(ANK_PATH, 'rb') as f:
        fnt = f.read()

    chars_to_train = []
    pua_start = 0xE000
    pua_count = 0

    # 0. ANK 低域 (0x01-0x1F)
    for c in range(0x01, 0x20):
        data = get_ank_data(fnt, c)
        if data is None:
            continue
        if c in ANK_EXT_OVERRIDES and ANK_EXT_OVERRIDES[c]:
            char = ANK_EXT_OVERRIDES[c]
        else:
            char = chr(pua_start + pua_count)
            pua_count += 1
        chars_to_train.append({'char': char, 'type': 'ank', 'data': data})

    # 1. ASCII (0x20-0x7E)
    for c in range(0x20, 0x7F):
        data = get_ank_data(fnt, c)
        if data:
            chars_to_train.append({'char': chr(c), 'type': 'ank', 'data': data})

    # 2. 半角カナ (0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            char = bytes([c]).decode('cp932')
        except Exception:
            continue
        data = get_ank_data(fnt, c)
        if data:
            chars_to_train.append({'char': char, 'type': 'ank', 'data': data})

    # 2b. ANK 拡張 (0x80-0x9F)
    for c in range(0x80, 0xA0):
        data = get_ank_data(fnt, c)
        if data is None:
            continue
        if c in ANK_EXT_OVERRIDES and ANK_EXT_OVERRIDES[c]:
            char = ANK_EXT_OVERRIDES[c]
        else:
            char = chr(pua_start + pua_count)
            pua_count += 1
        chars_to_train.append({'char': char, 'type': 'ank', 'data': data})

    # 3a. 0区
    for jis2 in range(0x20, 0x80):
        data = get_kanji_data(rom, 0x20, jis2)
        if data is None:
            continue
        key = (0x20, jis2)
        if key in ROW0_OVERRIDES and ROW0_OVERRIDES[key]:
            char = ROW0_OVERRIDES[key]
        else:
            char = chr(pua_start + pua_count)
            pua_count += 1
        chars_to_train.append({'char': char, 'type': 'kanji', 'data': data})

    # 3b. JIS X 0208 全角
    for jis1 in range(0x21, 0x7F):
        for jis2 in range(0x20, 0x80):
            data = get_kanji_data(rom, jis1, jis2)
            if data is None:
                continue
            key = (jis1, jis2)
            if key in CHAR_OVERRIDES:
                if CHAR_OVERRIDES[key]:
                    char = CHAR_OVERRIDES[key]
                else:
                    char = chr(pua_start + pua_count)
                    pua_count += 1
            else:
                try:
                    char = unicodedata.normalize('NFC',
                        bytes([jis1 + 0x80, jis2 + 0x80]).decode('euc_jp'))
                except Exception:
                    char = chr(pua_start + pua_count)
                    pua_count += 1
            chars_to_train.append({'char': char, 'type': 'kanji', 'data': data})

    total_chars = len(chars_to_train)
    num_lines = math.ceil(total_chars / CHARS_PER_LINE)

    print(f"Generating multipage TIF with scanlines (Kanji only) for MSX ({num_lines} pages, {total_chars} chars)...")

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

                line_width = sum((8 if item['type'] in ('ank', 'ank16') else 16) + 2*CELL_PAD for item in line_chars)
                img = Image.new('L', (line_width, ROW_H), color=0)
                draw = CellPadDraw(ImageDraw.Draw(img))

                x_pos = 0
                for item in line_chars:

                    if item['type'] == 'ank':
                        # 半角: 通常サイズ (8px)
                        ox = 0
                        oy = 12
                        for row_idx, byte in enumerate(item['data']):
                            y = oy + row_idx
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    draw.point((ox + bit, y), fill=255)
                    else:
                        # 全角: スキャンライン挿入 (16 -> 32px)
                        d = item['data']
                        ox = 0
                        oy = (CELL_SIZE - 32) // 2
                        for r in range(16):
                            left  = d[r]       if r < 8 else d[(r - 8) + 16]
                            right = d[r + 8]   if r < 8 else d[(r - 8) + 24]
                            y = oy + r * 2
                            for bit in range(8):
                                if left & (0x80 >> bit):
                                    draw.point((ox + bit,     y), fill=255)
                                if right & (0x80 >> bit):
                                    draw.point((ox + 8 + bit, y), fill=255)

                    item_w = 8 if item['type'] in ('ank', 'ank16') else 16
                    all_box_entries.append(
                        f"{item['char']} {x_pos} 0 {x_pos + item_w + 2*CELL_PAD} {ROW_H} {current_page}")
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
    _save_imgs[0].save(WORK_DIR / f"{OUTPUT_PREFIX}.tif",
                       save_all=True, append_images=_save_imgs[1:],
                       compression='raw')
    with open(WORK_DIR / f"{OUTPUT_PREFIX}.box", 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_box_entries) + '\n')

    print(f"Done. {OUTPUT_PREFIX}.tif ({current_page} pages), {OUTPUT_PREFIX}.box")


if __name__ == '__main__':
    main()
