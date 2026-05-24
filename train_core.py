"""
Tesseract LSTM 学習パイプライン共通ロジック。
Windows / macOS / Linux 対応。
"""
import io
import os
import shutil
import struct
import subprocess
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path


LANGDATA_BASE = 'https://github.com/tesseract-ocr/langdata_lstm/raw/main/'
LANGDATA_FILES = [
    'radical-stroke.txt',
    'Latin.unicharset',
    'Katakana.unicharset',
    'Hiragana.unicharset',
    'Han.unicharset',
    'Greek.unicharset',
    'Cyrillic.unicharset',
]

TESSDATA_BEST_URL = 'https://github.com/tesseract-ocr/tessdata_best/raw/main/'


# ─────────────────────── ユーティリティ ───────────────────────

def find_tess_dir() -> Path:
    """Tesseract 実行ファイルのディレクトリを返す。"""
    tess = shutil.which('tesseract')
    if tess:
        return Path(tess).parent

    # Windows デフォルト
    for win in [
        Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Tesseract-OCR',
        Path('C:/Program Files/Tesseract-OCR'),
        Path('C:/Program Files (x86)/Tesseract-OCR'),
    ]:
        if (win / 'tesseract.exe').exists():
            return win

    # macOS Homebrew
    for mac in [Path('/opt/homebrew/bin'), Path('/usr/local/bin')]:
        if (mac / 'tesseract').exists():
            return mac

    raise RuntimeError(
        'Tesseract が見つかりません。PATH に追加するか、インストールしてください。'
    )


def exe(tess_dir: Path, name: str) -> str:
    """実行ファイルパスを返す (Windows: .exe 付き)。"""
    if sys.platform == 'win32':
        return str(tess_dir / f'{name}.exe')
    return str(tess_dir / name)


def run(cmd, env=None, check=True):
    """コマンドを実行し、失敗時は例外を投げる。"""
    print(f'\n$ {" ".join(str(c) for c in cmd)}')
    return subprocess.run([str(c) for c in cmd], env=env, check=check)


def download(url: str, dest: Path):
    """ファイルが存在しない場合のみダウンロードする。"""
    if dest.exists() and dest.stat().st_size > 0:
        # 壊れた HTML を排除
        with open(dest, 'rb') as f:
            head = f.read(20)
        if b'DOCTYPE' in head or b'<html' in head.lower():
            dest.unlink()
        else:
            return
    print(f'Downloading {url} ...')
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest))


def generate_lstmf(tif_path: Path, box_path: Path, lstmf_path: Path,
                   vertical: bool = False,
                   unicharset_path: Path | None = None) -> None:
    """
    マルチページ TIF + box ファイルから lstmf を Python で直接生成する。
    Tesseract 5.x DocumentData / ImageData バイナリ形式に準拠。
    既存の Tesseract モデル不要（フルスクラッチ対応）。

    lstmf バイナリ構造 (Tesseract 5.x, little-endian):
      page_count: uint32                       ← std::vector<ImageData*>::size
      pages[]:
          non_null     : uint8                 ← 1 = 有効, 0 = null
          imagefilename: uint32 len + UTF-8 bytes (空文字でよい)
          page_number  : int32
          image_data   : uint32 len + PNG bytes (std::vector<char>)
          language     : uint32 len + UTF-8 bytes (空文字でよい)
          transcription: uint32 len + UTF-8 bytes
          boxes        : uint32 N + N × TBOX
                         TBOX = bot_left(left:int16, bottom:int16) +
                                top_right(right:int16, top:int16) = 8 bytes
          box_texts    : uint32 count + (uint32 len + UTF-8 bytes) × count
          vertical     : uint8
    """
    from PIL import Image

    def u32(n):  return struct.pack('<I', n)

    def ser_str(s: str) -> bytes:
        b = s.encode('utf-8')
        return u32(len(b)) + b

    def img_png(img: Image.Image) -> bytes:
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()

    # マルチページ TIF 読み込み
    imgs: list[Image.Image] = []
    tif = Image.open(str(tif_path))
    try:
        while True:
            imgs.append(tif.copy())
            tif.seek(tif.tell() + 1)
    except EOFError:
        pass

    # unicharset を読み、有効な単一コードポイントの集合を作る。
    # unicharset_extractor は半角/全角スペース等を除外するため、
    # box ファイルにあっても unicharset に無い文字は recoder で encode 不能。
    valid_chars: set[str] | None = None
    if unicharset_path is not None and unicharset_path.exists():
        valid_chars = set()
        with open(str(unicharset_path), encoding='utf-8') as f:
            f.readline()  # 1 行目はエントリー数
            for line in f:
                token = line.split(' ', 1)[0]
                if len(token) == 1:
                    valid_chars.add(token)

    # box ファイル解析: page → [(char, x1, y1, x2, y2)]
    # 座標は Tesseract 形式 (y=0 が画像下端) — box ファイル生成時と同じ
    page_boxes: dict[int, list] = defaultdict(list)
    skipped = 0
    with open(str(box_path), encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            char = line[0]              # 常に 1 コードポイント
            if valid_chars is not None and char not in valid_chars:
                skipped += 1
                continue
            parts = line[2:].split()    # "x1 y1 x2 y2 page"
            if len(parts) >= 5:
                x1, y1, x2, y2, pg = map(int, parts[:5])
                page_boxes[pg].append((char, x1, y1, x2, y2))
    if skipped:
        print(f'  unicharset 外の {skipped} エントリーを除外しました')

    out = io.BytesIO()

    # std::vector<ImageData*>::Serialize → uint32 count から開始
    out.write(u32(len(imgs)))

    for pg_idx, img in enumerate(imgs):
        boxes = page_boxes.get(pg_idx, [])
        if vertical:
            boxes.sort(key=lambda b: -b[4])   # y2 降順 (上→下)
        else:
            boxes.sort(key=lambda b: b[1])     # x1 昇順 (左→右)

        # non_null flag (ポインタが non-null である事を示す)
        out.write(struct.pack('B', 1))

        # imagefilename_ (string)
        out.write(ser_str(''))

        # page_number_ (int32)
        out.write(struct.pack('<i', pg_idx))

        # image_data_ (std::vector<char>: uint32 count + bytes)
        png_bytes = img_png(img)
        out.write(u32(len(png_bytes)))
        out.write(png_bytes)

        # language_ (string)
        out.write(ser_str(''))

        # transcription_ (string)
        out.write(ser_str(''.join(c for c, *_ in boxes)))

        # boxes_ (std::vector<TBOX>: uint32 N + N × (4 × int16))
        out.write(u32(len(boxes)))
        for _, x1, y1, x2, y2 in boxes:
            # TBOX = bot_left(x=left, y=bottom) + top_right(x=right, y=top)
            out.write(struct.pack('<4h', x1, y1, x2, y2))

        # box_texts_ (std::vector<string>: uint32 count + STRING[])
        out.write(u32(len(boxes)))
        for char, *_ in boxes:
            out.write(ser_str(char))

        # vertical_text_ (bool: 1 byte)
        out.write(struct.pack('B', 1 if vertical else 0))

    with open(str(lstmf_path), 'wb') as f:
        f.write(out.getvalue())

    total_boxes = sum(len(v) for v in page_boxes.values())
    print(f'lstmf 生成完了: {lstmf_path.name} ({len(imgs)} pages, {total_boxes} boxes)')


# ─────────────────────── ファインチューニング補助 ───────────────────────

def download_base_traineddata(base_lang: str, cache_dir: Path) -> Path:
    """tessdata_best からベース言語の traineddata をダウンロードしてキャッシュ。"""
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / f'{base_lang}.traineddata'
    if not dest.exists() or dest.stat().st_size < 1_000_000:
        url = TESSDATA_BEST_URL + f'{base_lang}.traineddata'
        download(url, dest)
    return dest


def extract_component(traineddata: Path, suffix: str, tess_dir: Path) -> Path:
    """traineddata から指定suffix(.lstm, .lstm-unicharset 等)のコンポーネントを取り出す。"""
    out_path = traineddata.parent / f'{traineddata.stem}{suffix}'
    if not out_path.exists():
        run([exe(tess_dir, 'combine_tessdata'),
             '-e', str(traineddata), str(out_path)])
    return out_path


def merge_unicharsets(base_uc: Path, our_uc: Path, out_uc: Path,
                       tess_dir: Path) -> None:
    """2つのunicharsetを併合する (Tesseract公式の merge_unicharsets を使用)。"""
    out_uc.parent.mkdir(parents=True, exist_ok=True)
    run([exe(tess_dir, 'merge_unicharsets'),
         str(base_uc), str(our_uc), str(out_uc)])


# ─────────────────────── パイプラインステップ ───────────────────────

def step_clean(cfg: dict, work_dir: Path):
    """生成物・中間ファイル・出力ディレクトリを削除する。"""
    lang   = cfg['lang']
    prefix = cfg['prefix']
    output_dir = work_dir / f'output_{lang}'
    tessdata_dir = work_dir / 'tessdata'

    if output_dir.exists():
        shutil.rmtree(output_dir)
    for ext in ['.tif', '.box', '.lstmf', '.full.traineddata']:
        (work_dir / f'{prefix}{ext}').unlink(missing_ok=True)
    (work_dir / f'unicharset_{lang}').unlink(missing_ok=True)
    (work_dir / f'train_list_{lang}.txt').unlink(missing_ok=True)
    lang_dir = work_dir / lang
    if lang_dir.exists():
        shutil.rmtree(lang_dir)
    (tessdata_dir / f'{lang}.traineddata').unlink(missing_ok=True)
    print(f'Clean done: {lang}')


def step_concat(cfg: dict, work_dir: Path, tess_dir: Path,
                finetune_from: str | None = None):
    """unicharset 抽出 → starter traineddata 生成 → lstmf 生成。

    finetune_from が指定された場合 (例 'jpn'): そのベースモデルの unicharset を
    取得して併合した unicharset で starter traineddata を生成する。
    """
    lang   = cfg['lang']
    prefix = cfg['prefix']
    output_dir  = work_dir / f'output_{lang}'
    tessdata_dir = work_dir / 'tessdata'
    langdata_dir = work_dir / 'temp_langdata'
    base_dir     = work_dir / 'base_models'

    output_dir.mkdir(parents=True, exist_ok=True)
    tessdata_dir.mkdir(parents=True, exist_ok=True)
    langdata_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: unicharset
    print('\n--- Step 1: unicharset (extract from box) ---')
    our_uc = work_dir / f'unicharset_{lang}'
    run([exe(tess_dir, 'unicharset_extractor'),
         '--output_unicharset', our_uc,
         work_dir / f'{prefix}.box'])

    # Step 1.5 (optional): ベースunicharsetとの併合
    final_uc = our_uc
    if finetune_from:
        print(f'\n--- Step 1.5: merge unicharset with {finetune_from} base ---')
        base_tdat = download_base_traineddata(finetune_from, base_dir)
        base_uc = extract_component(base_tdat, '.lstm-unicharset', tess_dir)
        merged_uc = work_dir / f'unicharset_{lang}_merged'
        merge_unicharsets(base_uc, our_uc, merged_uc, tess_dir)
        final_uc = merged_uc

    # Step 2: starter traineddata
    print('\n--- Step 2: starter traineddata ---')
    for fname in LANGDATA_FILES:
        download(LANGDATA_BASE + fname, langdata_dir / fname)
    run([exe(tess_dir, 'combine_lang_model'),
         '--input_unicharset', final_uc,
         '--script_dir',       langdata_dir,
         '--output_dir',       work_dir,
         '--lang',             lang])
    lang_traineddata = work_dir / lang / f'{lang}.traineddata'
    shutil.copy(lang_traineddata, work_dir / f'{prefix}.full.traineddata')
    shutil.copy(lang_traineddata, tessdata_dir / f'{lang}.traineddata')

    # Step 3: lstmf (Python 直接生成 — 外部学習データ不要)
    print('\n--- Step 3: lstmf ---')
    (work_dir / f'{prefix}.lstmf').unlink(missing_ok=True)
    generate_lstmf(
        tif_path        = work_dir / f'{prefix}.tif',
        box_path        = work_dir / f'{prefix}.box',
        lstmf_path      = work_dir / f'{prefix}.lstmf',
        vertical        = cfg.get('vert', False),
        unicharset_path = final_uc,
    )

    listfile = work_dir / f'train_list_{lang}.txt'
    with open(listfile, 'w', encoding='utf-8', newline='\n') as _f:
        _f.write(str((work_dir / f'{prefix}.lstmf').resolve()) + '\n')
    print(f'lstmf list: {listfile}')


def step_train(cfg: dict, work_dir: Path, tess_dir: Path,
               max_iterations: int = 10000,
               finetune_from: str | None = None):
    """lstmtraining + チェックポイントエクスポート。

    finetune_from が指定された場合: ベースモデル (例 jpn) の LSTM 重みから
    継続学習する。--net_spec は使わない (ネットワーク構造はベースのものを継承)。
    """
    lang         = cfg['lang']
    prefix       = cfg['prefix']
    net_h        = cfg['net_h']
    output_dir   = work_dir / f'output_{lang}'
    tessdata_dir = work_dir / 'tessdata'
    listfile     = work_dir / f'train_list_{lang}.txt'
    base_dir     = work_dir / 'base_models'

    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 4: 学習
    print('\n--- Step 4: lstmtraining ---')
    checkpoint = output_dir / f'{lang}_checkpoint'
    base_cmd = [exe(tess_dir, 'lstmtraining'),
                '--model_output',  output_dir / lang,
                '--traineddata',   work_dir / f'{prefix}.full.traineddata',
                '--train_listfile', listfile,
                '--max_iterations', str(max_iterations)]

    if checkpoint.exists():
        # 途中再開: --continue_from は自分自身のcheckpoint
        run(base_cmd + ['--continue_from', checkpoint])
    elif finetune_from:
        # 新規開始 (ファインチューニング): ベースLSTMから継続
        base_tdat = download_base_traineddata(finetune_from, base_dir)
        base_lstm = extract_component(base_tdat, '.lstm', tess_dir)
        print(f'  ベースモデル: {base_tdat.name} (LSTM: {base_lstm.name})')
        run(base_cmd + [
            '--continue_from',    base_lstm,
            '--old_traineddata',  base_tdat,
        ])
    else:
        # 新規開始 (フルスクラッチ): --net_spec で構造定義
        uc_tmp = work_dir / 'tmp_uc.lstm-unicharset'
        run([exe(tess_dir, 'combine_tessdata'),
             '-e', work_dir / f'{prefix}.full.traineddata',
             str(uc_tmp)])
        with open(uc_tmp, encoding='utf-8') as _f:
            unichar_size = int(_f.readline())
        uc_tmp.unlink(missing_ok=True)

        net_spec = (f'[1,{net_h},0,1 Ct3,3,16 Mp3,3 Lfys64 Lfx96 Lrx96 Lfx512 '
                    f'O1c{unichar_size}]')
        run(base_cmd + ['--net_spec', net_spec])

    # Step 5: エクスポート
    print('\n--- Step 5: export ---')
    if checkpoint.exists():
        run([exe(tess_dir, 'lstmtraining'),
             '--stop_training',
             '--continue_from',  checkpoint,
             '--traineddata',    work_dir / f'{prefix}.full.traineddata',
             '--model_output',   tessdata_dir / f'{lang}.traineddata'])
        print(f'Exported: {tessdata_dir / lang}.traineddata')
    else:
        print('No checkpoint found, skipping export.')
