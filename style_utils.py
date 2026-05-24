import os
from pathlib import Path
import numpy as np
from PIL import Image

_HERE = Path(__file__).resolve().parent
WORK_DIR = Path(os.environ.get('RETRO_WORK_DIR', _HERE))

STYLES = [
    ('bold',   3),  # 白地黒文字 太字 — 実PC-98ゲーム画面の主ドメイン (ボールド体)
    ('normal', 1),  # 白地黒文字 通常 — 細字/非太字画面の保険
]
# 注: inverse_* (黒地白文字) スタイルおよびノイズ付加機能は廃止した。本番前処理が
# 必ず白地黒文字へ正規化し、かつ2値化で薄い汚れも消えるため、逆極性データもノイズ
# データも推論で意味を持たないため。出力は常にクリーンな白地黒文字。

# --- Feature flags: False / 0 に設定するだけで元の動作に戻る ---
SINGLE_PAGE   = False  # True: 全グリフを1枚のTIFに; False: マルチページTIF (Tesseract学習には False が必須)
TIGHT_PACK    = True   # True: 上下パディングなし; False: 元のPAD_Vあり (横方向ジェネレータのみ)
CELL_PAD      = 1      # 各グリフ周囲の余白(px)。0 で元の動作に戻る

# main.py --padding / --style による上書き (サブプロセス実行時に有効)
if 'RETRO_CELL_PAD' in os.environ:
    CELL_PAD = int(os.environ['RETRO_CELL_PAD'])
if 'RETRO_STYLES' in os.environ:
    # 書式: 'bold:2,normal:1'
    STYLES = [(n, int(w)) for entry in os.environ['RETRO_STYLES'].split(',')
              for n, w in [entry.split(':')]]
if 'RETRO_TIGHT_PACK' in os.environ:
    TIGHT_PACK = os.environ['RETRO_TIGHT_PACK'].lower() == 'true'
if 'RETRO_SINGLE_PAGE' in os.environ:
    SINGLE_PAGE = os.environ['RETRO_SINGLE_PAGE'].lower() == 'true'


class CellPadDraw:
    """ImageDraw ラッパー: 全 draw.point 呼び出しに pad / y_offset を加算する。

    cell_pad / y_offset を行ごとにランダム化すれば、LSTM が「字間 1px」「ベースライン
    固定」のような幾何規則を区切り信号として過学習する問題を防げる。指定なしなら
    モジュール定数 CELL_PAD を使う (旧挙動互換)。
    """
    def __init__(self, base_draw, cell_pad=None, y_offset=0):
        self._d = base_draw
        self._cp = CELL_PAD if cell_pad is None else cell_pad
        self._yo = y_offset

    def point(self, xy, **kw):
        x, y = xy
        self._d.point((x + self._cp, y + self._cp + self._yo), **kw)


def apply_style(glyph_img, style):
    """PIL Image (L mode, white-on-black) にスタイル変換を適用する。
    'bold' は横1pxずらしOR合成で太字化、それ以外 ('normal') は素通し。
    """
    if style == 'bold':
        arr = np.array(glyph_img, dtype=np.uint8)
        shifted = np.zeros_like(arr)
        shifted[:, 1:] = arr[:, :-1]
        return Image.fromarray(arr | shifted)
    return glyph_img


def finalize_line(img):
    """常に白地黒文字へ反転して返す (inverse 機能は廃止)。"""
    return Image.eval(img, lambda x: 255 - x)
