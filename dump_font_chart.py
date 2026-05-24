"""
レトロPCフォントROMのグリフ一覧を1枚のPNGに出力する。

使い方:
    python dump_font_chart.py [target]
    target: pc98 (デフォルト) / pc88 / x68k / fm77 / fmt / msx

出力: font_chart_<target>.png

セクション構成 (Unicode 範囲ベース):
  1. ASCII (U+0020-U+007E)
  2. 半角カナ (U+FF61-U+FF9F)
  3. 全角記号・かな (U+3000-U+30FF)
  4. CJK統合漢字 (U+4E00-U+9FFF)
  5. その他 (全角ASCII、ギリシャ文字、ラテン拡張等)
  6. PUA (U+E000+)
"""
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


# ─────────────── 機種別ローダー ───────────────

def load_target(target: str):
    """ターゲット機種の char_to_glyph と data取り出しclosure を返す。"""
    if target == 'pc98':
        from generate_training_data_pc98 import build_char_to_glyph, FONT_ROM_PATH
        with open(FONT_ROM_PATH, 'rb') as f:
            rom = f.read()
        c2g, _ = build_char_to_glyph(rom, include_pua=True)
        def getter(item):
            return rom[item['addr']:item['addr']+item['size']]
        return c2g, getter

    if target == 'x68k':
        from generate_training_data_x68k import build_char_to_glyph, CGROM_PATH
        with open(CGROM_PATH, 'rb') as f:
            rom = f.read()
        c2g, _ = build_char_to_glyph(rom, include_pua=True)
        def getter(item):
            return rom[item['addr']:item['addr']+item['size']]
        return c2g, getter

    if target == 'fmt':
        from generate_training_data_fmt import build_char_to_glyph, FONT_ROM_PATH
        with open(FONT_ROM_PATH, 'rb') as f:
            rom = f.read()
        c2g, _ = build_char_to_glyph(rom, include_pua=True)
        def getter(item):
            return rom[item['addr']:item['addr']+item['size']]
        return c2g, getter

    if target == 'pc88':
        from generate_training_data_pc88 import build_char_to_glyph, KANJI1_ROM_PATH, KANJI2_ROM_PATH
        with open(KANJI1_ROM_PATH, 'rb') as f: k1 = f.read()
        with open(KANJI2_ROM_PATH, 'rb') as f: k2 = f.read()
        roms = [k1, k2]
        c2g, _ = build_char_to_glyph(roms, include_pua=True)
        def getter(item):
            return roms[item['rom_idx']][item['addr']:item['addr']+item['size']]
        return c2g, getter

    if target == 'fm77':
        from generate_training_data_fm77 import build_char_to_glyph, SUBSYSC_ROM_PATH, KANJI_ROM_PATH
        with open(SUBSYSC_ROM_PATH, 'rb') as f: s = f.read()
        with open(KANJI_ROM_PATH, 'rb') as f: k = f.read()
        roms = [s, k]
        c2g, _ = build_char_to_glyph(roms, include_pua=True)
        def getter(item):
            return roms[item['rom_idx']][item['addr']:item['addr']+item['size']]
        return c2g, getter

    if target == 'msx':
        from generate_training_data_msx import build_char_to_glyph, KANJI_ROM_PATH, ANK_PATH
        with open(KANJI_ROM_PATH, 'rb') as f: rom = f.read()
        with open(ANK_PATH, 'rb') as f: fnt = f.read()
        c2g, _ = build_char_to_glyph(rom, fnt, include_pua=True)
        def getter(item):
            src = rom if item['src'] == 'kanji' else fnt
            return src[item['addr']:item['addr']+item['size']]
        return c2g, getter

    sys.exit(f'未対応の機種: {target} (対応: pc98 / pc88 / x68k / fm77 / fmt / msx)')


# ─────────────── レンダリング ───────────────

def render_glyph(data, item) -> Image.Image:
    """機種別の byte format を吸収してPIL画像を返す。"""
    width = item['width']
    fmt   = item.get('fmt')  # PC-98 は fmt 無し

    # 8x8 (PC-88, FM-77, MSX の ANK)
    if fmt == 'ank8':
        img = Image.new('L', (8, 8), color=255)
        for i in range(8):
            byte = data[i]
            for bit in range(8):
                if byte & (0x80 >> bit):
                    img.putpixel((bit, i), 0)
        return img

    # 8x16 (PC-98, X68k, FM-TOWNS の ANK)
    if width == 8:
        img = Image.new('L', (8, 16), color=255)
        for i in range(16):
            byte = data[i]
            for bit in range(8):
                if byte & (0x80 >> bit):
                    img.putpixel((bit, i), 0)
        return img

    # 16x16 漢字
    img = Image.new('L', (16, 16), color=255)
    if fmt is None:  # PC-98: bytes 0-15=L, 16-31=R
        for i in range(16):
            row_bits = (data[i] << 8) | data[i+16]
            for bit in range(16):
                if row_bits & (0x8000 >> bit):
                    img.putpixel((bit, i), 0)
    elif fmt in ('x68k_k', 'lr_inter'):  # [L0,R0,L1,R1,...]
        for i in range(16):
            row_bits = (data[i*2] << 8) | data[i*2+1]
            for bit in range(16):
                if row_bits & (0x8000 >> bit):
                    img.putpixel((bit, i), 0)
    elif fmt == 'msx_4quad':  # 4象限
        for r in range(16):
            if r < 8:
                L = data[r]; R = data[r+8]
            else:
                L = data[(r-8)+16]; R = data[(r-8)+24]
            row_bits = (L << 8) | R
            for bit in range(16):
                if row_bits & (0x8000 >> bit):
                    img.putpixel((bit, r), 0)
    return img


# ─────────────── ラベルフォント ───────────────

def load_label_font(size: int = 9):
    for fp in [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/Library/Fonts/Arial.ttf',
    ]:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ─────────────── Unicode セクション分類 ───────────────

SECTIONS = [
    ('ASCII',           0x0020, 0x007F),
    ('Half-width Kana', 0xFF61, 0xFFA0),
    ('Hiragana',        0x3040, 0x30A0),
    ('Katakana',        0x30A0, 0x3100),
    ('CJK Symbols',     0x3000, 0x3040),
    ('Fullwidth ASCII', 0xFF01, 0xFF5F),
    ('CJK Unified',     0x4E00, 0xA000),
    ('Latin Ext / Greek', 0x00A0, 0x0500),
    ('Other BMP',       0x0500, 0xE000),
    ('PUA',             0xE000, 0xF900),
]


def classify(ch: str) -> int:
    cp = ord(ch)
    for idx, (_, lo, hi) in enumerate(SECTIONS):
        if lo <= cp < hi:
            return idx
    return len(SECTIONS)  # 雑多


# ─────────────── メイン ───────────────

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'pc98'
    char_to_glyph, getter = load_target(target)
    print(f'[{target}] グリフ数: {len(char_to_glyph)}')

    # セクション別にグリフを分類
    section_chars: list[list[str]] = [[] for _ in range(len(SECTIONS) + 1)]
    for ch in char_to_glyph.keys():
        section_chars[classify(ch)].append(ch)
    for chars in section_chars:
        chars.sort(key=ord)

    CELL_W = 18
    CELL_H = 18
    MARGIN_L = 12
    MARGIN_T = 14
    SECTION_GAP = 22
    COLS_PER_ROW = 80  # 1行 80字 (= キャンバス幅 ~1500px)

    font_lbl = load_label_font(9)
    font_head = load_label_font(12)

    # サイズ計算
    total_rows = 0
    section_rows = []
    for i, chars in enumerate(section_chars):
        if not chars:
            section_rows.append(0)
            continue
        rows = (len(chars) + COLS_PER_ROW - 1) // COLS_PER_ROW
        section_rows.append(rows)
        total_rows += rows

    canvas_w = MARGIN_L + COLS_PER_ROW * CELL_W + 20
    canvas_h = (
        MARGIN_T
        + sum((section_rows[i] * CELL_H + SECTION_GAP) for i in range(len(section_rows)) if section_rows[i] > 0)
        + 30
    )
    print(f'キャンバス: {canvas_w} × {canvas_h}')

    canvas = Image.new('L', (canvas_w, canvas_h), color=255)
    draw = ImageDraw.Draw(canvas)

    def paste_glyph(ch, x, y):
        if ch not in char_to_glyph:
            return
        info = char_to_glyph[ch]
        try:
            data = getter(info)
        except Exception:
            return
        glyph = render_glyph(data, info)
        canvas.paste(glyph, (x, y))

    y = MARGIN_T
    # タイトル
    draw.text((MARGIN_L, y), f'FONT CHART: {target.upper()}  -  {len(char_to_glyph)} glyphs', fill=0, font=font_head)
    y += 18

    for i, (sec_name, lo, hi) in enumerate(SECTIONS + [('Misc', 0, 0)]):
        chars = section_chars[i]
        if not chars:
            continue
        if i < len(SECTIONS):
            label = f'{sec_name} (U+{lo:04X} - U+{hi-1:04X})  -  {len(chars)} chars'
        else:
            label = f'Misc  -  {len(chars)} chars'
        draw.text((MARGIN_L, y), label, fill=0, font=font_lbl)
        y += 12

        for idx, ch in enumerate(chars):
            col = idx % COLS_PER_ROW
            row = idx // COLS_PER_ROW
            x = MARGIN_L + col * CELL_W
            cy = y + row * CELL_H
            paste_glyph(ch, x, cy)

        y += section_rows[i] * CELL_H + SECTION_GAP

    out_path = HERE / f'font_chart_{target}.png'
    canvas.save(out_path, optimize=True)
    print(f'保存: {out_path}')


if __name__ == '__main__':
    main()
