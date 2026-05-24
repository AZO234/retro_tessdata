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

# 設定
KANJI_ROM_PATH = find_rom('rom/msx/fs-a1gt_kanjifont.rom')
ANK_PATH       = find_rom('rom/msx/JAPANESE.FNT')
OUTPUT_PREFIX  = 'jpn.msx.exp0'

# MSX FS-A1GT Kanji ROM (0x40000 = 256KB) のレイアウト
# (openMSX MSXKanji.cc + msx_charmap.py 蓄積知見 より)
# - 8192 cells × 32 byte (= 256KB)
# - cell addr = code * 32
# - code = (jis1 - 0x20) * 64 + (jis2 - 0x20)  ※実質: row_stride=2048, col_stride=32
# - MSX独自のコード割当を採用しており、JIS X 0208 標準とは一致しない。
#   実際の文字ラベルは msx_charmap.py で手動マッピングしている。
# 漢字グリフ32byteの内部配置: 4象限
#   bytes 0-7:   rows 0-7 左半 (1byte/row, MSB=左)
#   bytes 8-15:  rows 0-7 右半
#   bytes 16-23: rows 8-15 左半
#   bytes 24-31: rows 8-15 右半

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2
CHAR_H = 16
ROW_H  = CHAR_H + 2*CELL_PAD if TIGHT_PACK else CELL_H


def kanji_addr(jis1: int, jis2: int) -> int:
    """JIS位置 → MSX KANJI ROM byte offset (各glyphは32byte)。"""
    return (jis1 - 0x20) * 2048 + (jis2 - 0x20) * 32


def build_char_to_glyph(rom, fnt, include_pua: bool = False):
    """ROM 上の有効グリフを列挙し、char → {width, src, addr, size, fmt} の辞書を返す。

    src='ank' は JAPANESE.FNT を参照、'kanji' は KANJI ROM を参照。
    fmt='ank8'      : 8x8 (8 byte), byte[i] = i行目, MSB=左
    fmt='msx_4quad' : 16x16 (32 byte), 4象限レイアウト
    """
    char_to_glyph: dict[str, dict] = {}
    pua_chars: list[str] = []
    pua_count = 0
    pua_start = 0xE000

    def _add_ank(ch, code, is_pua=False):
        addr = code * 8
        if addr + 8 > len(fnt):
            return False
        data = fnt[addr:addr+8]
        if all(b == 0 for b in data):
            return False
        char_to_glyph[ch] = {'width': 8, 'src': 'ank', 'addr': addr, 'size': 8, 'fmt': 'ank8'}
        if is_pua:
            pua_chars.append(ch)
        return True

    # ASCII 8x8 (0x20-0x7E)
    for c in range(0x20, 0x7F):
        _add_ank(chr(c), c)

    # 半角カナ 8x8 (cp932 0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            ch = bytes([c]).decode('cp932')
        except Exception:
            continue
        _add_ank(ch, c)

    # ANK 規格外領域 (0x01-0x1F, 0x80-0x9F) は msx_charmap か PUA
    for code in list(range(0x01, 0x20)) + list(range(0x80, 0xA0)):
        if code in ANK_EXT_OVERRIDES and ANK_EXT_OVERRIDES[code]:
            ch = ANK_EXT_OVERRIDES[code]
            if ch not in char_to_glyph:
                _add_ank(ch, code)
        elif include_pua:
            ch = chr(pua_start + pua_count)
            if _add_ank(ch, code, is_pua=True):
                pua_count += 1

    # 漢字 16x16 (MSX-specific code → 文字)
    # row 0 (jis1=0x20): 標準JIS外の拡張記号
    for jis2 in range(0x20, 0x80):
        addr = kanji_addr(0x20, jis2)
        if addr + 32 > len(rom):
            continue
        data = rom[addr:addr+32]
        if all(b == 0 for b in data):
            continue
        key = (0x20, jis2)
        if key in ROW0_OVERRIDES and ROW0_OVERRIDES[key]:
            ch = ROW0_OVERRIDES[key]
        elif include_pua:
            ch = chr(pua_start + pua_count)
            pua_count += 1
            pua_chars.append(ch)
        else:
            continue
        if ch not in char_to_glyph:
            char_to_glyph[ch] = {'width': 16, 'src': 'kanji', 'addr': addr, 'size': 32, 'fmt': 'msx_4quad'}

    # row 1-94 (jis1=0x21-0x7E)
    for jis1 in range(0x21, 0x7F):
        for jis2 in range(0x20, 0x80):
            addr = kanji_addr(jis1, jis2)
            if addr + 32 > len(rom):
                continue
            data = rom[addr:addr+32]
            if all(b == 0 for b in data):
                continue

            key = (jis1, jis2)
            is_pua = False
            if key in CHAR_OVERRIDES:
                if CHAR_OVERRIDES[key]:
                    ch = CHAR_OVERRIDES[key]
                else:
                    if not include_pua:
                        continue
                    ch = chr(pua_start + pua_count)
                    pua_count += 1
                    is_pua = True
            else:
                try:
                    ch = unicodedata.normalize('NFC',
                        bytes([jis1 + 0x80, jis2 + 0x80]).decode('euc_jp'))
                except Exception:
                    if not include_pua:
                        continue
                    ch = chr(pua_start + pua_count)
                    pua_count += 1
                    is_pua = True

            if ch not in char_to_glyph:
                char_to_glyph[ch] = {'width': 16, 'src': 'kanji', 'addr': addr, 'size': 32, 'fmt': 'msx_4quad'}
                if is_pua:
                    pua_chars.append(ch)

    return char_to_glyph, pua_chars


# ─────────────── 行ストリーム生成 ───────────────

def iter_lines_charlist(char_to_glyph: dict, limit_chars: int):
    items = sorted(char_to_glyph.items(), key=lambda kv: (kv[1]['src'], kv[1]['addr']))
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

    include_pua = os.environ.get('RETRO_INCLUDE_PUA', 'false').lower() == 'true'
    char_to_glyph, pua_chars = build_char_to_glyph(rom, fnt, include_pua=include_pua)
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

    print(f"Generating multipage TIF (MSX) ({len(lines) * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

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
                    src = rom if item['src'] == 'kanji' else fnt
                    addr = item['addr']
                    size = item['size']
                    data = src[addr:addr+size]

                    if item['fmt'] == 'ank8':
                        y_off = (CHAR_H - 8) // 2
                        for row_idx, byte in enumerate(data):
                            for bit in range(8):
                                if byte & (0x80 >> bit):
                                    draw.point((x_pos + bit, y_off + row_idx), fill=255)
                    else:  # msx_4quad
                        y_off = 0 if TIGHT_PACK else PAD_V
                        for r in range(16):
                            if r < 8:
                                L = data[r]; R = data[r + 8]
                            else:
                                L = data[(r-8) + 16]; R = data[(r-8) + 24]
                            row_bits = (L << 8) | R
                            for bit in range(16):
                                if row_bits & (0x8000 >> bit):
                                    draw.point((x_pos + bit, y_off + r), fill=255)

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
