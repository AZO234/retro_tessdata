"""
Retro Tesseract 学習 CLI
使い方: python main.py <target> <function> [options]

<function>:
  clean                        : 生成物の削除
  full                         : clean + generate + image + concat + train
  generate [--padding N]       : 学習画像 (.tif / .box) 生成
           [--style name:weight]
  image                        : マルチページ TIF を 1 ページ PNG に変換
  concat                       : unicharset + starter traineddata + lstmf 生成
  train    [--iterate N]       : lstmtraining + エクスポート

本番学習例:
  python main.py pc98 full --padding 1 --iterate 100000
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from train_core import find_tess_dir, step_clean, step_concat, step_train
from train_configs import get_config, ALL_TARGETS


def build_env(padding: int, styles: list[str], work_dir: Path,
              char_range: str = 'all', tight_pack: bool = True,
              limit_chars: int = 0,
              corpus_path: str | None = None,
              max_lines: int = 10000) -> dict:
    env = os.environ.copy()
    env['RETRO_CELL_PAD'] = str(padding)
    env['RETRO_WORK_DIR'] = str(work_dir)
    env['RETRO_RANGE']    = char_range
    env['RETRO_TIGHT_PACK'] = 'true' if tight_pack else 'false'
    env['RETRO_LIMIT_CHARS'] = str(limit_chars)
    env['RETRO_MAX_LINES'] = str(max_lines)
    if styles:
        env['RETRO_STYLES'] = ','.join(styles)
    if corpus_path:
        env['RETRO_CORPUS_PATH'] = corpus_path
    return env


def run_generate(target: str, env: dict):
    script = HERE / f'generate_training_data_{target}.py'
    if not script.exists():
        sys.exit(f'エラー: {script} が見つかりません。')
    cmd = [sys.executable, str(script)]
    print(f'\n$ {" ".join(cmd)}')
    result = subprocess.run(cmd, env=env, cwd=str(HERE))
    if result.returncode != 0:
        sys.exit(f'generate 失敗 (終了コード {result.returncode})')


def step_image(cfg: dict, work_dir: Path):
    """マルチページ TIF を 1 ページ PNG に変換する。
    横書き: 上から下に連結 / 縦書き: 右から左に連結
    """
    from PIL import Image

    prefix = cfg['prefix']
    tif_path = work_dir / f'{prefix}.tif'
    if not tif_path.exists():
        sys.exit(f'エラー: {tif_path} が見つかりません。generate を先に実行してください。')

    pages = []
    with Image.open(tif_path) as im:
        try:
            while True:
                pages.append(im.copy())
                im.seek(im.tell() + 1)
        except EOFError:
            pass

    print(f'Loaded {len(pages)} pages from {tif_path.name}')

    is_vert = cfg.get('vert', False)

    if is_vert:
        # 縦書き: ページ 0 が右端、右から左へ並べる
        total_w = sum(p.width for p in pages)
        max_h = max(p.height for p in pages)
        out = Image.new('L', (total_w, max_h), color=128)
        x = 0
        for p in reversed(pages):
            out.paste(p, (x, 0))
            x += p.width
    else:
        # 横書き: 上から下に積む
        max_w = max(p.width for p in pages)
        total_h = sum(p.height for p in pages)
        out = Image.new('L', (max_w, total_h), color=128)
        y = 0
        for p in pages:
            out.paste(p, (0, y))
            y += p.height

    png_path = work_dir / f'{prefix}.png'
    out.save(str(png_path))
    print(f'Saved: {png_path}  ({out.width}x{out.height}px)')


def main():
    parser = argparse.ArgumentParser(
        description='Retro Tesseract 学習 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('target', choices=ALL_TARGETS,
                        metavar='target',
                        help=f'学習対象: {{{", ".join(ALL_TARGETS)}}}')
    parser.add_argument('function',
                        choices=['clean', 'full', 'generate', 'image', 'concat', 'train'],
                        metavar='function',
                        help='実行する処理: clean / full / generate / image / concat / train')
    parser.add_argument('--padding', type=int, default=1,
                        metavar='N',
                        help='セルパディング幅 (ドット数, デフォルト: 1)  [generate / full]')
    parser.add_argument('--style', action='append', default=[],
                        dest='styles',
                        metavar='name:weight',
                        help='スタイル指定, 複数可  [generate / full]')
    parser.add_argument('--iterate', type=int, default=10000,
                        metavar='N',
                        help='学習イテレーション数 (デフォルト: 10000, 本番推奨: 100000)  [train / full]')
    parser.add_argument('--range', default='all',
                        metavar='RANGE',
                        help='文字範囲 (ascii,kana,jis1,jis2,jis_misc,jis_ext) [generate / full]')
    parser.add_argument('--limit-chars', type=int, default=0,
                        metavar='N',
                        help='各カテゴリーの最大文字数 (0で無制限) [generate / full]')
    parser.add_argument('--tight-pack', action='store_true', default=True,
                        help='上下パディングを詰める (デフォルト: True) [generate / full]')
    parser.add_argument('--no-tight-pack', action='store_false', dest='tight_pack',
                        help='上下パディングを詰めない (net_h=32に固定される) [generate / full]')
    parser.add_argument('--corpus', default=None,
                        metavar='PATH|token+token+...',
                        help='実文章コーパス。tokens: '
                             '"auto"=青空文庫, '
                             '"wiki"=Wikipedia ゲーム/アニメ(サブカル), '
                             '"wikigen"=Wikipedia 現代一般 (科学/社会/歴史/文化等), '
                             '"kanwa"=Wiktionary 慣用句/ことわざ/四字熟語。'
                             '"+" で連結指定 (例: auto+wiki+wikigen+kanwa)。'
                             '未指定でレガシー(JIS辞書順)モード [generate / full]')
    parser.add_argument('--max-lines', type=int, default=10000,
                        metavar='N',
                        help='コーパスから生成する最大行数 (デフォルト: 10000) [generate / full]')
    parser.add_argument('--finetune', default='jpn',
                        metavar='BASE_LANG',
                        help='ベース言語からファインチューニング (デフォルト: jpn)。'
                             'unicharset併合 + --continue_from で学習開始。'
                             '指定がなければ機種用tessdata未存在時に jpn ベストを自動DL [concat / train / full]')
    parser.add_argument('--no-finetune', action='store_true',
                        help='ファインチューニング無効化 (フルスクラッチ学習)。--finetune より優先 [concat / train / full]')
    args = parser.parse_args()
    if args.no_finetune:
        args.finetune = None
    target = args.target
    func   = args.function

    work_dir = HERE / f'base_{target}'
    work_dir.mkdir(exist_ok=True)

    # コーパス自動取得 (--corpus auto / wiki / wikigen / kanwa / 連結指定 / <path>)
    # トークン: auto=aozora, wiki=サブカル, wikigen=現代一般, kanwa=慣用句
    corpus_path = args.corpus
    if corpus_path:
        sources = []
        for token in corpus_path.split('+'):
            t = token.strip().lower()
            if t in ('auto', 'aozora'):
                sources.append('aozora')
            elif t in ('wiki', 'wikipedia', 'wikisub'):
                sources.append('wiki')
            elif t in ('wikigen', 'wikigeneral'):
                sources.append('wikigen')
            elif t in ('kanwa', '漢和'):
                sources.append('kanwa')
            elif t:
                sources = []  # ファイルパス指定なら sources は使わない
                break
        if len(sources) == 1:
            from corpus_utils import (fetch_aozora_corpus, fetch_wikipedia_corpus,
                                       fetch_wikipedia_general_corpus, fetch_kanwa_corpus)
            single = sources[0]
            if single == 'aozora':
                corpus_path = str(fetch_aozora_corpus(work_dir, min_chars=500_000))
            elif single == 'wiki':
                corpus_path = str(fetch_wikipedia_corpus(work_dir, min_chars=1_000_000))
            elif single == 'wikigen':
                corpus_path = str(fetch_wikipedia_general_corpus(work_dir, min_chars=1_000_000))
            elif single == 'kanwa':
                corpus_path = str(fetch_kanwa_corpus(work_dir, min_chars=200_000))
        elif len(sources) > 1:
            from corpus_utils import fetch_combined_corpus
            corpus_path = str(fetch_combined_corpus(work_dir, sources, min_chars=500_000))

    env = build_env(args.padding, args.styles, work_dir,
                    char_range=args.range, tight_pack=args.tight_pack,
                    limit_chars=args.limit_chars,
                    corpus_path=corpus_path,
                    max_lines=args.max_lines)

    cfg = get_config(target, cell_pad=args.padding, tight_pack=args.tight_pack)

    tess_dir = find_tess_dir() if func not in ('generate', 'image', 'clean') else None

    print(f'Target   : {target}')
    print(f'Function : {func}')
    print(f'Work dir : {work_dir}')
    if tess_dir:
        print(f'Tess dir : {tess_dir}')
    if func in ('generate', 'full'):
        print(f'Padding  : {args.padding}')
        if args.styles:
            print(f'Styles   : {", ".join(args.styles)}')
        if corpus_path:
            print(f'Corpus   : {corpus_path}  (max_lines={args.max_lines})')
        else:
            print(f'Corpus   : (none — legacy char-list mode)')
    if func in ('train', 'full', 'concat'):
        if args.finetune:
            print(f'Finetune : ベース言語 = {args.finetune}')
    if func in ('train', 'full'):
        print(f'Iterate  : {args.iterate}')

    if func == 'clean':
        step_clean(cfg, work_dir)

    elif func == 'generate':
        run_generate(target, env)

    elif func == 'image':
        step_image(cfg, work_dir)

    elif func == 'concat':
        step_concat(cfg, work_dir, tess_dir, finetune_from=args.finetune)

    elif func == 'train':
        step_train(cfg, work_dir, tess_dir, max_iterations=args.iterate,
                   finetune_from=args.finetune)

    elif func == 'full':
        tess_dir = find_tess_dir()
        step_clean(cfg, work_dir)
        run_generate(target, env)
        step_image(cfg, work_dir)
        step_concat(cfg, work_dir, tess_dir, finetune_from=args.finetune)
        step_train(cfg, work_dir, tess_dir, max_iterations=args.iterate,
                   finetune_from=args.finetune)


if __name__ == '__main__':
    main()
