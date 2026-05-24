import os
import math
import random
from PIL import Image, ImageDraw
from style_utils import STYLES, apply_style, finalize_line, SINGLE_PAGE, TIGHT_PACK, CELL_PAD, CellPadDraw, WORK_DIR

# 字間ジッタ範囲。PC-98 ゲーム画面はベースライン固定・X位置固定なので
# y_offset 系のランダムジッタは導入しない (= 過学習方向のノイズになる)。
# 字間 (CELL_PAD) だけが実画面で変動する要素 (BIOS/DOSは 1px、ADV/メニューは 0px 等)。
JITTER_CELL_PAD_MIN = int(os.environ.get('RETRO_JITTER_CELL_PAD_MIN', '0'))
JITTER_CELL_PAD_MAX = int(os.environ.get('RETRO_JITTER_CELL_PAD_MAX', '3'))
JITTER_Y_OFFSET     = int(os.environ.get('RETRO_JITTER_Y_OFFSET', '0'))  # 通常 0
JITTER_SEED         = int(os.environ.get('RETRO_JITTER_SEED', '42'))


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
OUTPUT_PREFIX = 'jpn.pc98.exp0'
MAP_FILE = 'char_map.txt'

# V98 FONT.ROM (0x46800 bytes) のレイアウト  (NP2kai fontv98.c 由来)
# - 0x0000-0x07FF: ANK 8x8 (256 chars × 8 bytes)
# - 0x0800-0x0FFF: ANK 8x16 前半 (128 chars × 16 bytes)  - ASCII
# - 0x1000-0x17FF: ANK 8x16 後半 (128 chars × 16 bytes)  - 半角カナ
# - 0x1800-:       KNJ 16x16  各JIS行 0x60*32 = 0xC00 bytes、列 0x20-0x7F
#                  glyph 内バイト配置: 0..15=左半行0-15, 16..31=右半行0-15
ASCII_BASE = 0x0800
KANA_BASE  = 0x1000
KANJI_BASE = 0x1800
KANJI_ROW_STRIDE = 0xC00

CHARS_PER_LINE = 50
CELL_H = 32
PAD_V = (CELL_H - 16) // 2  # = 8
CHAR_H = 16  # actual glyph height
ROW_H  = CHAR_H + 2*CELL_PAD if TIGHT_PACK else CELL_H  # tight: remove PAD_V


def build_char_to_glyph(rom, include_pua: bool = False):
    """ROM 上の有効グリフを列挙し、char → {width, addr, size} の辞書を返す。

    - ASCII (0x20-0x7E)            : width=8, size=16
    - 半角カナ (cp932 0xA1-0xDF)   : width=8, size=16
    - JIS X 0208 漢字 (row 1-94)   : width=16, size=32

    include_pua=True の時のみ、JIS にデコードできないセル(非ブランク)を
    PUA (U+E000+) として登録する。
    既定 False: PUA を除外する (学習時の言語モデル発散を防ぐため)。
    """
    char_to_glyph: dict[str, dict] = {}
    pua_count = 0
    pua_chars: list[str] = []

    # ASCII 8x16: addr = ASCII_BASE + c * 16
    for c in range(0x20, 0x7F):
        addr = ASCII_BASE + c * 16
        if addr + 16 > len(rom):
            continue
        data = rom[addr:addr+16]
        if all(b == 0 for b in data) or all(b == 0xFF for b in data):
            continue
        char_to_glyph[chr(c)] = {'width': 8, 'addr': addr, 'size': 16}

    # 半角カナ 8x16: addr = KANA_BASE + (c - 0x80) * 16  (c=0xA1-0xDF)
    for c in range(0xA1, 0xE0):
        try:
            ch = bytes([c]).decode('cp932')
        except Exception:
            continue
        addr = KANA_BASE + (c - 0x80) * 16
        if addr + 16 > len(rom):
            continue
        data = rom[addr:addr+16]
        if all(b == 0 for b in data) or all(b == 0xFF for b in data):
            continue
        char_to_glyph[ch] = {'width': 8, 'addr': addr, 'size': 16}

    # 漢字 16x16: addr = KANJI_BASE + (row-1) * KANJI_ROW_STRIDE + (jisl - 0x20) * 32
    pua_start = 0xE000
    for row in range(1, 95):                       # JIS row 1-94
        for col in range(0x21, 0x7F):              # JIS col 0x21-0x7E
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

            addr = KANJI_BASE + (row - 1) * KANJI_ROW_STRIDE + (jisl - 0x20) * 32
            if addr + 32 > len(rom):
                continue
            data = rom[addr:addr+32]
            if all(b == 0 for b in data) or all(b == 0xFF for b in data):
                continue

            if ch not in char_to_glyph:
                char_to_glyph[ch] = {'width': 16, 'addr': addr, 'size': 32}
                if is_pua:
                    pua_chars.append(ch)

    return char_to_glyph, pua_chars


# ─────────────── 行ストリーム生成 ───────────────

def iter_lines_charlist(char_to_glyph: dict, retro_range_filter, limit_chars: int):
    """旧仕様: 辞書順 char 列を CHARS_PER_LINE で区切ったストリーム。"""
    seq: list[str] = []
    # ASCII / kana / kanji の順
    if retro_range_filter('ascii'):
        for c in range(0x20, 0x7F):
            ch = chr(c)
            if ch in char_to_glyph:
                seq.append(ch)
    if retro_range_filter('kana'):
        for c in range(0xA1, 0xE0):
            try:
                ch = bytes([c]).decode('cp932')
            except Exception:
                continue
            if ch in char_to_glyph:
                seq.append(ch)

    # 漢字 (addr 順): char_to_glyph に存在する全角文字を ROM 上の順に拾う
    kanji = [(g['addr'], ch) for ch, g in char_to_glyph.items() if g['width'] == 16]
    kanji.sort()
    if retro_range_filter('jis_all'):
        for _, ch in kanji:
            seq.append(ch)

    if limit_chars > 0:
        seq = seq[:limit_chars]

    for i in range(0, len(seq), CHARS_PER_LINE):
        yield seq[i:i+CHARS_PER_LINE]


def iter_lines_corpus(corpus_path: str, char_to_glyph: dict, pua_chars: list,
                       max_lines: int):
    """新仕様: 実文章コーパスから ≤CHARS_PER_LINE の行ストリームを生成。

    PUA文字は learning rate を不安定化させる発散原因 (言語モデル文脈が皆無な為)。
    pua_chars が空でない場合のみ末尾に showcase 行を追加する (include_pua=True時のみ)。
    """
    text = open(corpus_path, encoding='utf-8').read()

    renderable = set(char_to_glyph.keys())
    yielded = 0

    for raw_line in text.split('\n'):
        # 描画可能な文字のみ抽出
        filtered = [c for c in raw_line if c in renderable]
        if not filtered:
            continue
        # CHARS_PER_LINE で分割
        for i in range(0, len(filtered), CHARS_PER_LINE):
            chunk = filtered[i:i+CHARS_PER_LINE]
            yield chunk
            yielded += 1
            if max_lines > 0 and yielded >= max_lines:
                break
        if max_lines > 0 and yielded >= max_lines:
            break

    # PUA showcase は include_pua=True の時だけ (pua_chars が非空)
    if pua_chars:
        for i in range(0, len(pua_chars), CHARS_PER_LINE):
            yield pua_chars[i:i+CHARS_PER_LINE]


def main():
    if not os.path.exists(FONT_ROM_PATH):
        print(f"Error: {FONT_ROM_PATH} not found.")
        return
    with open(FONT_ROM_PATH, 'rb') as f: rom = f.read()

    include_pua = os.environ.get('RETRO_INCLUDE_PUA', 'false').lower() == 'true'
    char_to_glyph, pua_chars = build_char_to_glyph(rom, include_pua=include_pua)
    print(f'描画可能文字: {len(char_to_glyph)} (うち PUA: {len(pua_chars)}, include_pua={include_pua})')

    # モード選択: コーパスパス指定があればコーパスモード
    corpus_path = os.environ.get('RETRO_CORPUS_PATH', '').strip()
    max_lines   = int(os.environ.get('RETRO_MAX_LINES', '10000'))
    limit_chars = int(os.environ.get('RETRO_LIMIT_CHARS', '0'))
    retro_range = os.environ.get('RETRO_RANGE', 'all').lower().split(',')

    def range_filter(key: str) -> bool:
        if 'all' in retro_range:
            return True
        if key in retro_range:
            return True
        if key == 'jis_all':
            return any(k in retro_range for k in ('jis1', 'jis2', 'jis_misc', 'jis_ext'))
        return False

    if corpus_path:
        if not os.path.exists(corpus_path):
            print(f'Error: corpus not found: {corpus_path}')
            return
        print(f'コーパスモード: {corpus_path}  (max_lines={max_lines})')
        line_iter = iter_lines_corpus(corpus_path, char_to_glyph, pua_chars, max_lines)
    else:
        print('レガシーモード: JIS辞書順char list')
        line_iter = iter_lines_charlist(char_to_glyph, range_filter, limit_chars)

    # 一旦リスト化 (スタイル毎に再利用するため)
    lines = list(line_iter)
    total_chars = sum(len(l) for l in lines)
    print(f'生成行数: {len(lines)} / 総文字数: {total_chars}')

    print(f"Generating multipage TIF (PC-98) ({len(lines) * sum(r for _,r in STYLES)} pages, {total_chars} chars × {len(STYLES)} styles)...")

    for ext in [".tif", ".box", ".lstmf"]:
        fpath = WORK_DIR / f"{OUTPUT_PREFIX}{ext}"
        if os.path.exists(fpath):
            os.remove(fpath)

    all_images = []
    all_box_entries = []
    current_page = 0

    # 行ジッタ用 RNG (seed 固定で再現可能)
    rng = random.Random(JITTER_SEED)

    # スタイル横断インターリーブ: line 0 を全style → line 1 を全style → ...
    # こうすることで「途中で全ドメインがガラッと切り替わる」shockを回避し、
    # finetune ベースモデルが最初から全styleに馴染んでいく。
    for line_chars_src in lines:
        # 各文字に glyph 情報を付与
        line_chars = [
            {'char': ch, **char_to_glyph[ch]} for ch in line_chars_src
        ]
        if not line_chars:
            continue

        # 行ごとの字間 (CELL_PAD) を 0..3 でランダム化。
        # CELL_PAD 0 → 字間密着 (実画像 ADV/メニュー画面に多い)
        # CELL_PAD 1-3 → 余白あり (BIOS/DOS 等 ROM ベタ書きに多い)
        # 行頭X固定・ベースラインY固定の PC-98 画面性質に従い、y_offset は通常 0。
        line_pad = rng.randint(JITTER_CELL_PAD_MIN, JITTER_CELL_PAD_MAX)
        line_y_off = rng.randint(-JITTER_Y_OFFSET, JITTER_Y_OFFSET) if JITTER_Y_OFFSET > 0 else 0
        # 行画像高さ
        line_row_h = CHAR_H + 2*line_pad if TIGHT_PACK else CELL_H
        if JITTER_Y_OFFSET > 0:
            line_row_h += 2 * JITTER_Y_OFFSET  # y_off 分の上下余裕

        line_width = sum(item['width'] + 2*line_pad for item in line_chars)

        # 各スタイルで同じ行ジッタを共有する (同じ line_chars の異なる style が
        # 異なる幾何にならないようにし、style 学習の独立性を保つ)。
        for style_name, repeat in STYLES:
            for _ in range(repeat):
                img = Image.new('L', (line_width, line_row_h), color=0)
                draw = CellPadDraw(ImageDraw.Draw(img),
                                    cell_pad=line_pad,
                                    y_offset=line_y_off)

                x_pos = 0
                for item in line_chars:
                    size = item['size']
                    addr = item['addr']
                    font_data = rom[addr:addr+size] if addr + size <= len(rom) else None

                    if font_data:
                        if item['width'] == 16:
                            for i in range(16):
                                row_bits = (font_data[i] << 8) | font_data[i+16]
                                for bit in range(16):
                                    if row_bits & (0x8000 >> bit):
                                        draw.point((x_pos + bit, (0 if TIGHT_PACK else PAD_V) + i), fill=255)
                        else:
                            for i in range(16):
                                row_bits = font_data[i]
                                for bit in range(8):
                                    if row_bits & (0x80 >> bit):
                                        draw.point((x_pos + bit, (0 if TIGHT_PACK else PAD_V) + i), fill=255)

                    all_box_entries.append(f"{item['char']} {x_pos} 0 {x_pos + item['width'] + 2*line_pad} {line_row_h} {current_page}")
                    x_pos += item['width'] + 2*line_pad

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
