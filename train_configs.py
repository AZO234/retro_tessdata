"""
機種別学習設定。
row_h / net_h は CELL_PAD / TIGHT_PACK に依存するため、
get_config() 呼び出し時に style_utils から動的に取得する。
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))


def get_all_configs(cell_pad: int | None = None, tight_pack: bool | None = None):
    """全機種設定を返す。cell_pad / tight_pack は None なら style_utils の値を使う。"""
    from style_utils import CELL_PAD as _CP, TIGHT_PACK as _TP
    CP = cell_pad   if cell_pad   is not None else _CP
    TP = tight_pack if tight_pack is not None else _TP

    _STD_H    = 16 + 2*CP if TP else 32   # 標準横型 CHAR_H=16
    _SCAN_H   = 32 + 2*CP                  # スキャン系 CELL_H=32
    _F20_H    = 20 + 2*CP if TP else 24    # f20 CHAR_H=20
    _F20S_H   = 40 + 2*CP                  # f20_scan CELL_H=40
    _VERT_H   = 32 + 2*CP                  # vert CELL_SIZE=32
    _F20V_H   = 24 + 2*CP                  # f20_vert CELL_SIZE=24

    def net_h(h):
        return max(h, 32)

    return {
        # ── 標準横型 ─────────────────────────────────────────
        'pc98':      dict(lang='pc98',       prefix='jpn.pc98.exp0',      row_h=_STD_H,  net_h=net_h(_STD_H),  psm=6, vert=False),
        'fm77':      dict(lang='fm77',       prefix='jpn.fm77.exp0',      row_h=_STD_H,  net_h=net_h(_STD_H),  psm=6, vert=False),
        'fmt':       dict(lang='fmt',        prefix='jpn.fmt.exp0',       row_h=_STD_H,  net_h=net_h(_STD_H),  psm=6, vert=False),
        'msx':       dict(lang='msx',        prefix='jpn.msx.exp0',       row_h=_STD_H,  net_h=net_h(_STD_H),  psm=6, vert=False),
        'pc88':      dict(lang='pc88',       prefix='jpn.pc88.exp0',      row_h=_STD_H,  net_h=net_h(_STD_H),  psm=6, vert=False),
        'x68k':      dict(lang='x68k',       prefix='jpn.x68k.exp0',      row_h=_STD_H,  net_h=net_h(_STD_H),  psm=6, vert=False),
        # ── スキャン横型 ──────────────────────────────────────
        'pc98_scan': dict(lang='pc98_scan',  prefix='jpn.pc98_scan.exp0', row_h=_SCAN_H, net_h=net_h(_SCAN_H), psm=6, vert=False),
        'fm77_scan': dict(lang='fm77_scan',  prefix='jpn.fm77_scan.exp0', row_h=_SCAN_H, net_h=net_h(_SCAN_H), psm=6, vert=False),
        'fmt_scan':  dict(lang='fmt_scan',   prefix='jpn.fmt_scan.exp0',  row_h=_SCAN_H, net_h=net_h(_SCAN_H), psm=6, vert=False),
        'msx_scan':  dict(lang='msx_scan',   prefix='jpn.msx_scan.exp0',  row_h=_SCAN_H, net_h=net_h(_SCAN_H), psm=6, vert=False),
        'pc88_scan': dict(lang='pc88_scan',  prefix='jpn.pc88_scan.exp0', row_h=_SCAN_H, net_h=net_h(_SCAN_H), psm=6, vert=False),
        'x68k_scan': dict(lang='x68k_scan',  prefix='jpn.x68k_scan.exp0', row_h=_SCAN_H, net_h=net_h(_SCAN_H), psm=6, vert=False),
        # ── f20 系 ────────────────────────────────────────────
        'f20':       dict(lang='f20',        prefix='jpn.f20.exp0',       row_h=_F20_H,  net_h=net_h(_F20_H),  psm=6, vert=False),
        'f20_scan':  dict(lang='f20_scan',   prefix='jpn.f20_scan.exp0',  row_h=_F20S_H, net_h=net_h(_F20S_H), psm=6, vert=False),
        # ── 縦方向 ────────────────────────────────────────────
        'f20_vert':  dict(lang='f20_vert',   prefix='jpn_vert.f20.exp0',  row_h=_F20V_H, net_h=net_h(_F20V_H), psm=5, vert=True),
        'pc98_vert': dict(lang='pc98_vert',  prefix='jpn_vert.pc98.exp0', row_h=_VERT_H, net_h=net_h(_VERT_H), psm=5, vert=True),
        'fm77_vert': dict(lang='fm77_vert',  prefix='jpn_vert.fm77.exp0', row_h=_VERT_H, net_h=net_h(_VERT_H), psm=5, vert=True),
        'fmt_vert':  dict(lang='fmt_vert',   prefix='jpn_vert.fmt.exp0',  row_h=_VERT_H, net_h=net_h(_VERT_H), psm=5, vert=True),
        'msx_vert':  dict(lang='msx_vert',   prefix='jpn_vert.msx.exp0',  row_h=_VERT_H, net_h=net_h(_VERT_H), psm=5, vert=True),
        'pc88_vert': dict(lang='pc88_vert',  prefix='jpn_vert.pc88.exp0', row_h=_VERT_H, net_h=net_h(_VERT_H), psm=5, vert=True),
        'x68k_vert': dict(lang='x68k_vert',  prefix='jpn_vert.x68k.exp0', row_h=_VERT_H, net_h=net_h(_VERT_H), psm=5, vert=True),
    }


def get_config(target: str, cell_pad=None, tight_pack=None) -> dict:
    configs = get_all_configs(cell_pad=cell_pad, tight_pack=tight_pack)
    if target not in configs:
        raise ValueError(f"Unknown target: {target!r}. Available: {sorted(configs)}")
    return configs[target]


ALL_TARGETS = list(get_all_configs().keys())
