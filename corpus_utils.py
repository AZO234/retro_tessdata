"""
日本語コーパス取得・前処理 (青空文庫 + Wikipedia)。
学習画像生成時に「実文章」を入力として渡すためのユーティリティ。

設計方針:
- 青空文庫: 公開URL から複数作品の txt を取得 (Shift_JIS or UTF-8)、ルビ/注記を除去
- Wikipedia (CC BY-SA): action=query API 経由でカテゴリ巡回 + 各記事の本文を取得 (現代日本語)
- 旧字体は新字体への置換は行わない (PC-98 ROM が表現可能なら学習対象とする)

対外API:
- fetch_aozora_corpus(cache_dir, min_chars) -> Path  (古典文学コーパス)
- fetch_wikipedia_corpus(cache_dir, min_chars) -> Path (現代日本語コーパス, ゲーム/アニメ等)
- fetch_combined_corpus(cache_dir, sources, min_chars) -> Path  (混合コーパス)
"""
import json
import re
import time
import urllib.parse
import urllib.request
import zipfile
import io
from pathlib import Path


# 公開ドメイン作品の直接URL (Aozora ZIP)。
# 著者・代表作を分散させ、語彙多様性を確保する。
# 一部失敗しても全体が継続できるよう、必要量を超える点数を用意。
AOZORA_WORKS = [
    # 夏目漱石
    ('https://www.aozora.gr.jp/cards/000148/files/789_ruby_5639.zip',  '吾輩は猫である'),
    ('https://www.aozora.gr.jp/cards/000148/files/773_ruby_5968.zip',  'こころ'),
    ('https://www.aozora.gr.jp/cards/000148/files/752_ruby_2438.zip',  '坊っちゃん'),
    # 芥川龍之介
    ('https://www.aozora.gr.jp/cards/000879/files/127_ruby_150.zip',   '羅生門'),
    ('https://www.aozora.gr.jp/cards/000879/files/179_ruby_873.zip',   '蜘蛛の糸'),
    ('https://www.aozora.gr.jp/cards/000879/files/92_ruby_164.zip',    '地獄変'),
    # 太宰治
    ('https://www.aozora.gr.jp/cards/000035/files/1567_ruby_4948.zip', '走れメロス'),
    ('https://www.aozora.gr.jp/cards/000035/files/301_ruby_5915.zip',  '人間失格'),
    # 宮沢賢治
    ('https://www.aozora.gr.jp/cards/000081/files/456_ruby_145.zip',   '銀河鉄道の夜'),
    ('https://www.aozora.gr.jp/cards/000081/files/43737_ruby_17656.zip', '注文の多い料理店'),
    # 森鴎外
    ('https://www.aozora.gr.jp/cards/000129/files/692_ruby_71.zip',    '舞姫'),
    # 中島敦
    ('https://www.aozora.gr.jp/cards/000119/files/624_ruby_5732.zip',  '山月記'),
    # 樋口一葉
    ('https://www.aozora.gr.jp/cards/000064/files/389_ruby_173.zip',   'たけくらべ'),
    # 国木田独歩
    ('https://www.aozora.gr.jp/cards/000038/files/45252_ruby_24906.zip', '武蔵野'),
]


# ─────────────── テキストクリーニング ───────────────

_RE_RUBY        = re.compile(r'《[^》]*》')             # 漢字《ふりがな》→ 漢字
_RE_RUBY_MARK   = re.compile(r'｜')                       # ふりがな起点指示子
_RE_NOTE        = re.compile(r'［＃[^］]*］')           # ［＃...］ 注記
_RE_NOTE_INLINE = re.compile(r'〔[^〕]*〕')             # 〔..〕 注記もまれにある
_RE_HEADER_SEP  = re.compile(r'^-{20,}\s*$', re.MULTILINE)
_RE_FOOTER      = re.compile(r'^底本：.*$', re.MULTILINE | re.DOTALL)


def clean_aozora_text(raw: str) -> str:
    """青空文庫の生テキストから本文だけを抽出する。"""
    # ヘッダ: 最初の "------------------------------" 行から
    # 次の "------------------------------" までを除去 (タイトル/著者/凡例)
    seps = list(_RE_HEADER_SEP.finditer(raw))
    if len(seps) >= 2:
        raw = raw[seps[1].end():]

    # フッタ: 底本: 以降を切り捨て
    m = _RE_FOOTER.search(raw)
    if m:
        raw = raw[:m.start()]

    # 注記・ルビを除去
    raw = _RE_NOTE.sub('', raw)
    raw = _RE_NOTE_INLINE.sub('', raw)
    raw = _RE_RUBY.sub('', raw)
    raw = _RE_RUBY_MARK.sub('', raw)

    # 改行・空白の正規化: 連続改行→単一改行、行頭/行末の空白除去
    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    return '\n'.join(lines)


# ─────────────── ダウンロード ───────────────

def _decode_zip_text(zip_bytes: bytes) -> str | None:
    """青空ZIPから .txt を取り出し、文字コード自動判定でデコード。"""
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            txt_names = [n for n in z.namelist() if n.lower().endswith('.txt')]
            if not txt_names:
                return None
            data = z.read(txt_names[0])
    except zipfile.BadZipFile:
        return None

    # 青空文庫は Shift_JIS が主、稀に UTF-8
    for enc in ('shift_jis', 'cp932', 'utf-8'):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return None


def fetch_aozora_corpus(cache_dir: Path, min_chars: int = 500_000,
                        verbose: bool = True) -> Path:
    """
    青空文庫から min_chars 以上のコーパスを取得し、cache_dir/corpus_aozora.txt に保存。
    既存ファイルが min_chars を満たしていれば再ダウンロードしない。

    Returns: コーパスファイルのパス
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / 'corpus_aozora.txt'

    if out_path.exists() and out_path.stat().st_size > 0:
        existing_chars = sum(1 for _ in out_path.read_text(encoding='utf-8'))
        if existing_chars >= min_chars:
            if verbose:
                print(f'コーパスキャッシュ利用: {out_path} ({existing_chars} chars)')
            return out_path

    chunks: list[str] = []
    total = 0
    for url, title in AOZORA_WORKS:
        if total >= min_chars:
            break
        if verbose:
            print(f'  取得中: {title}')
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'retro_tessdata-corpus/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                zip_bytes = resp.read()
        except Exception as e:
            if verbose:
                print(f'    スキップ ({e})')
            continue

        raw = _decode_zip_text(zip_bytes)
        if not raw:
            if verbose:
                print(f'    スキップ (ZIP/エンコーディング不明)')
            continue
        cleaned = clean_aozora_text(raw)
        if not cleaned:
            continue
        chunks.append(cleaned)
        total += len(cleaned)
        if verbose:
            print(f'    +{len(cleaned)} chars (累計 {total})')

    if not chunks:
        raise RuntimeError('青空文庫からテキストを取得できませんでした。ネットワークまたはURLを確認してください。')

    body = '\n'.join(chunks)
    out_path.write_text(body, encoding='utf-8')
    if verbose:
        print(f'コーパス保存: {out_path} ({len(body)} chars)')
        _print_corpus_sample(body, label='Aozora')
    return out_path


def load_corpus(corpus_path: Path) -> str:
    """コーパステキストをUTF-8で読み込む。"""
    return Path(corpus_path).read_text(encoding='utf-8')


def filter_to_renderable(text: str, renderable: set) -> str:
    """ROMで描画できる文字のみを残す。改行は残す。"""
    out = []
    for ch in text:
        if ch == '\n' or ch in renderable:
            out.append(ch)
    return ''.join(out)


# ═══════════════ MediaWiki (Wikipedia / Wiktionary) ═══════════════
# CC BY-SA で配布される現代日本語コーパス。
# - Wikipedia サブカル: レトロゲーム/アニメ/ノベル領域の語彙
# - Wikipedia 現代一般: ランダム記事から広範な現代日本語
# - Wiktionary 漢和慣例: 慣用句・ことわざ・四字熟語

WIKIPEDIA_API = 'https://ja.wikipedia.org/w/api.php'
WIKTIONARY_API = 'https://ja.wiktionary.org/w/api.php'
WIKI_API = WIKIPEDIA_API  # 後方互換
WIKI_UA = 'retro_tessdata-corpus/1.0 (https://github.com/AZO234/retro_tessdata)'

# サブカル領域 (ゲーム/アニメ/ノベル/漫画)
WIKI_SEEDS_SUBCULTURE = [
    'Category:コンピュータゲーム',
    'Category:日本のロールプレイングゲーム',
    'Category:日本のアドベンチャーゲーム',
    'Category:アニメ作品',
    'Category:ライトノベル',
    'Category:漫画作品',
]

# 現代一般領域 (科学・社会・歴史・文化など、広範な現代日本語)
WIKI_SEEDS_GENERAL = [
    'Category:科学',
    'Category:社会',
    'Category:歴史',
    'Category:地理',
    'Category:文化',
    'Category:芸術',
    'Category:スポーツ',
    'Category:工業',
    'Category:人物',
    'Category:技術',
]

# Wiktionary 漢和慣例 (慣用句・ことわざ・四字熟語)
WIKTIONARY_SEEDS_KANWA = [
    'カテゴリ:慣用句',
    'カテゴリ:ことわざ',
    'カテゴリ:四字熟語',
]

WIKI_SEED_CATEGORIES = WIKI_SEEDS_SUBCULTURE  # 後方互換

# Wikipedia 特有のノイズパターン
_RE_WIKI_CITATIONS  = re.compile(r'\[\d+\]')                  # [1][2] 脚注
_RE_WIKI_BRACKETS   = re.compile(r'\[編集\]')                  # [編集] リンク残り
_RE_MULTI_SPACE     = re.compile(r'[ \t]+')                    # 連続スペース
_RE_MULTI_NEWLINE   = re.compile(r'\n{3,}')                    # 3連以上の改行
# wikitext 残骸: テンプレート未展開、出典URLなど
_RE_URL             = re.compile(r'https?://\S+')
_RE_TEMPLATE_LEAK   = re.compile(r'\{\{[^}]{1,200}\}\}')


def _wiki_request(params: dict, api_url: str = WIKIPEDIA_API) -> dict:
    """MediaWiki API GET (Wikipedia/Wiktionary 共通)。retry 3回。"""
    params = {**params, 'format': 'json', 'utf8': '1'}
    qs = urllib.parse.urlencode(params)
    url = f'{api_url}?{qs}'
    req = urllib.request.Request(url, headers={'User-Agent': WIKI_UA})
    last_err = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            last_err = e
            time.sleep(1 + attempt)
    raise RuntimeError(f'MediaWiki API failure ({api_url}): {last_err}')


# タイトル除外パターン (一覧・索引・年表など content の薄い記事)
_RE_TITLE_EXCLUDE = re.compile(r'(一覧|索引|年表|テンプレート|^Wikipedia:|^Help:|^Portal:|^Template:|^Category:)')


def _wiki_list_category_members(category: str, limit: int = 500,
                                  member_type: str = 'page',
                                  main_namespace_only: bool = True,
                                  api_url: str = WIKIPEDIA_API) -> list[str]:
    """カテゴリ直下のメンバー一覧を取得。
    member_type='page' でページのみ、'subcat' でサブカテゴリのみ。
    main_namespace_only=True で 標準名前空間 (記事本体) のみに限定。
    """
    titles: list[str] = []
    cont: dict | None = None
    while len(titles) < limit:
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': category,
            'cmtype': member_type,
            'cmlimit': str(min(500, limit - len(titles))),
        }
        if main_namespace_only and member_type == 'page':
            params['cmnamespace'] = '0'
        if cont:
            params.update(cont)
        data = _wiki_request(params, api_url=api_url)
        for m in data.get('query', {}).get('categorymembers', []):
            title = m['title']
            # 一覧・索引などのコンテンツ薄い記事を除外
            if member_type == 'page' and _RE_TITLE_EXCLUDE.search(title):
                continue
            titles.append(title)
        if 'continue' in data:
            cont = data['continue']
        else:
            break
    return titles


def _wiki_list_with_subcats(category: str, page_limit: int = 200,
                              subcat_depth: int = 1,
                              api_url: str = WIKIPEDIA_API) -> list[str]:
    """カテゴリと最大 subcat_depth 階層のサブカテゴリから記事を集める。"""
    pages = list(_wiki_list_category_members(category, limit=page_limit,
                                              member_type='page', api_url=api_url))
    if subcat_depth > 0 and len(pages) < page_limit:
        subcats = _wiki_list_category_members(category, limit=50,
                                                member_type='subcat', api_url=api_url)
        for sub in subcats:
            if len(pages) >= page_limit:
                break
            more = _wiki_list_with_subcats(sub,
                                            page_limit=page_limit - len(pages),
                                            subcat_depth=subcat_depth - 1,
                                            api_url=api_url)
            pages.extend(more)
    # 重複除去 (順序保持)
    seen = set()
    out = []
    for p in pages:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _wiki_fetch_plaintext(titles: list[str], api_url: str = WIKIPEDIA_API) -> dict[str, str]:
    """記事の平文を取得 (MediaWiki API は explaintext+batch 不可なので1件ずつ)。"""
    out: dict[str, str] = {}
    for title in titles:
        params = {
            'action': 'query',
            'prop': 'extracts',
            'titles': title,
            'explaintext': '1',
            'exsectionformat': 'plain',
        }
        try:
            data = _wiki_request(params, api_url=api_url)
        except Exception:
            continue
        for page in data.get('query', {}).get('pages', {}).values():
            t = page.get('title', '')
            text = page.get('extract', '')
            if text:
                out[t] = text
        time.sleep(0.3)  # rate limiting (各リクエスト間)
    return out


def _wiki_random_titles(count: int, api_url: str = WIKIPEDIA_API) -> list[str]:
    """ランダムに main namespace のページタイトルを取得。"""
    titles: list[str] = []
    while len(titles) < count:
        params = {
            'action': 'query',
            'list': 'random',
            'rnnamespace': '0',
            'rnlimit': str(min(10, count - len(titles))),
        }
        try:
            data = _wiki_request(params, api_url=api_url)
        except Exception:
            break
        for m in data.get('query', {}).get('random', []):
            title = m.get('title', '')
            if title and not _RE_TITLE_EXCLUDE.search(title):
                titles.append(title)
        time.sleep(0.3)
    return titles[:count]


def clean_wiki_text(raw: str) -> str:
    """Wikipedia の平文から OCR 学習に不要なノイズを除去。"""
    text = raw
    text = _RE_URL.sub('', text)
    text = _RE_WIKI_CITATIONS.sub('', text)
    text = _RE_WIKI_BRACKETS.sub('', text)
    text = _RE_TEMPLATE_LEAK.sub('', text)
    text = _RE_MULTI_SPACE.sub(' ', text)
    text = _RE_MULTI_NEWLINE.sub('\n\n', text)
    # 各行を strip
    lines = [l.strip() for l in text.splitlines()]
    # 短すぎる行 (3文字未満) や記号のみ行は除外
    lines = [l for l in lines if len(l) >= 3 and any('぀' <= c <= '鿿' for c in l)]
    return '\n'.join(lines)


def _fetch_mediawiki_by_categories(cache_dir: Path,
                                     out_filename: str,
                                     seed_categories: list[str],
                                     min_chars: int,
                                     per_category: int,
                                     api_url: str,
                                     subcat_depth: int,
                                     label: str,
                                     verbose: bool = True) -> Path:
    """MediaWiki (Wikipedia/Wiktionary) からカテゴリ巡回でコーパス取得する共通実装。"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / out_filename

    if out_path.exists() and out_path.stat().st_size > 0:
        existing_chars = len(out_path.read_text(encoding='utf-8'))
        if existing_chars >= min_chars:
            if verbose:
                print(f'{label} コーパスキャッシュ利用: {out_path} ({existing_chars} chars)')
            return out_path

    all_titles: set[str] = set()
    for cat in seed_categories:
        if verbose:
            print(f'  カテゴリ巡回 ({label}): {cat}')
        try:
            titles = _wiki_list_with_subcats(cat, page_limit=per_category,
                                              subcat_depth=subcat_depth, api_url=api_url)
        except Exception as e:
            if verbose:
                print(f'    スキップ ({e})')
            continue
        new_titles = [t for t in titles if t not in all_titles]
        all_titles.update(new_titles)
        if verbose:
            print(f'    +{len(new_titles)} titles (累計 {len(all_titles)})')

    if not all_titles:
        raise RuntimeError(f'{label} からタイトルを取得できませんでした。')

    chunks: list[str] = []
    total = 0
    titles_list = list(all_titles)
    for i in range(0, len(titles_list), 20):
        if total >= min_chars:
            break
        batch = titles_list[i:i+20]
        if verbose:
            print(f'  記事取得 ({label}) {i+1}〜{i+len(batch)} / {len(titles_list)} ...')
        extracts = _wiki_fetch_plaintext(batch, api_url=api_url)
        for title, raw_text in extracts.items():
            cleaned = clean_wiki_text(raw_text)
            if cleaned:
                chunks.append(cleaned)
                total += len(cleaned)

    if not chunks:
        raise RuntimeError(f'{label} から本文を取得できませんでした。')

    body = '\n'.join(chunks)
    out_path.write_text(body, encoding='utf-8')
    if verbose:
        print(f'{label} コーパス保存: {out_path} ({len(body)} chars, {len(chunks)} articles)')
        _print_corpus_sample(body, label=label)
    return out_path


def fetch_wikipedia_corpus(cache_dir: Path,
                           min_chars: int = 1_000_000,
                           per_category: int = 200,
                           verbose: bool = True) -> Path:
    """Wikipedia サブカル (ゲーム/アニメ/ノベル) コーパスを取得。 → corpus_wiki.txt"""
    return _fetch_mediawiki_by_categories(
        cache_dir, 'corpus_wiki.txt', WIKI_SEEDS_SUBCULTURE,
        min_chars=min_chars, per_category=per_category,
        api_url=WIKIPEDIA_API, subcat_depth=1, label='Wiki(サブカル)', verbose=verbose)


def fetch_wikipedia_general_corpus(cache_dir: Path,
                                    min_chars: int = 1_000_000,
                                    n_random: int = 1000,
                                    per_category: int = 80,
                                    verbose: bool = True) -> Path:
    """Wikipedia 現代一般 (科学/社会/歴史/文化等) + ランダム記事のコーパス。 → corpus_wikigen.txt"""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / 'corpus_wikigen.txt'

    if out_path.exists() and out_path.stat().st_size > 0:
        existing_chars = len(out_path.read_text(encoding='utf-8'))
        if existing_chars >= min_chars:
            if verbose:
                print(f'Wiki(現代一般) コーパスキャッシュ利用: {out_path} ({existing_chars} chars)')
            return out_path

    # シードカテゴリから集める + ランダム記事
    all_titles: set[str] = set()
    for cat in WIKI_SEEDS_GENERAL:
        if verbose:
            print(f'  カテゴリ巡回 (Wiki現代一般): {cat}')
        try:
            titles = _wiki_list_with_subcats(cat, page_limit=per_category,
                                              subcat_depth=1, api_url=WIKIPEDIA_API)
        except Exception as e:
            if verbose:
                print(f'    スキップ ({e})')
            continue
        new_titles = [t for t in titles if t not in all_titles]
        all_titles.update(new_titles)
        if verbose:
            print(f'    +{len(new_titles)} titles (累計 {len(all_titles)})')

    if n_random > 0:
        if verbose:
            print(f'  ランダム記事を {n_random} 件追加取得...')
        rand_titles = _wiki_random_titles(n_random, api_url=WIKIPEDIA_API)
        new_titles = [t for t in rand_titles if t not in all_titles]
        all_titles.update(new_titles)
        if verbose:
            print(f'    +{len(new_titles)} random titles (累計 {len(all_titles)})')

    if not all_titles:
        raise RuntimeError('Wikipedia (現代一般) からタイトルを取得できませんでした。')

    chunks: list[str] = []
    total = 0
    titles_list = list(all_titles)
    for i in range(0, len(titles_list), 20):
        if total >= min_chars:
            break
        batch = titles_list[i:i+20]
        if verbose:
            print(f'  記事取得 (Wiki現代一般) {i+1}〜{i+len(batch)} / {len(titles_list)} ...')
        extracts = _wiki_fetch_plaintext(batch, api_url=WIKIPEDIA_API)
        for title, raw_text in extracts.items():
            cleaned = clean_wiki_text(raw_text)
            if cleaned:
                chunks.append(cleaned)
                total += len(cleaned)

    if not chunks:
        raise RuntimeError('Wikipedia (現代一般) から本文を取得できませんでした。')

    body = '\n'.join(chunks)
    out_path.write_text(body, encoding='utf-8')
    if verbose:
        print(f'Wiki(現代一般) コーパス保存: {out_path} ({len(body)} chars, {len(chunks)} articles)')
        _print_corpus_sample(body, label='Wiki(現代一般)')
    return out_path


def fetch_kanwa_corpus(cache_dir: Path,
                       min_chars: int = 200_000,
                       per_category: int = 500,
                       verbose: bool = True) -> Path:
    """Wiktionary から慣用句・ことわざ・四字熟語のコーパスを取得。 → corpus_kanwa.txt"""
    return _fetch_mediawiki_by_categories(
        cache_dir, 'corpus_kanwa.txt', WIKTIONARY_SEEDS_KANWA,
        min_chars=min_chars, per_category=per_category,
        api_url=WIKTIONARY_API, subcat_depth=0, label='漢和慣例(Wiktionary)', verbose=verbose)


def _print_corpus_sample(body: str, label: str = '', head: int = 3, tail: int = 3):
    """コーパス内容の頭/末尾サンプルを print する (取得確認用)。"""
    lines = [l for l in body.splitlines() if l.strip()]
    print(f'--- {label} corpus preview (head {head} / tail {tail} lines) ---')
    for l in lines[:head]:
        print(f'  ▶ {l[:80]}{"…" if len(l) > 80 else ""}')
    if len(lines) > head + tail:
        print(f'  ... ({len(lines) - head - tail} more lines)')
    for l in lines[-tail:]:
        print(f'  ▶ {l[:80]}{"…" if len(l) > 80 else ""}')
    print('---')


def fetch_combined_corpus(cache_dir: Path,
                          sources: list[str],
                          min_chars: int = 500_000,
                          verbose: bool = True) -> Path:
    """
    複数ソース (aozora/wiki) を取得して連結。cache_dir/corpus_combined.txt に保存。

    sources: ['aozora', 'wiki'] など
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_path = cache_dir / 'corpus_combined.txt'

    paths: list[Path] = []
    for src in sources:
        if src == 'aozora':
            paths.append(fetch_aozora_corpus(cache_dir, min_chars=min_chars, verbose=verbose))
        elif src == 'wiki':
            paths.append(fetch_wikipedia_corpus(cache_dir, min_chars=min_chars, verbose=verbose))
        elif src == 'wikigen':
            paths.append(fetch_wikipedia_general_corpus(cache_dir, min_chars=min_chars, verbose=verbose))
        elif src == 'kanwa':
            paths.append(fetch_kanwa_corpus(cache_dir, min_chars=min(min_chars, 200_000), verbose=verbose))
        else:
            raise ValueError(f'Unknown corpus source: {src}')

    # 各ソースの行を個別に保持し、ラウンドロビンで交互に出力する。
    # こうすることで --max-lines N でも全ソースが等しく代表される。
    # (旧実装は連結だけだったため、頭から N 行で切ると後ろのソースが学習対象外になっていた)
    per_source_lines: list[list[str]] = []
    for p in paths:
        lines = [l for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
        per_source_lines.append(lines)

    if verbose:
        for name, lines in zip(sources, per_source_lines):
            print(f'  source {name:10s}: {len(lines):6d} 行')

    interleaved: list[str] = []
    max_len = max(len(s) for s in per_source_lines)
    for i in range(max_len):
        for src_lines in per_source_lines:
            if i < len(src_lines):
                interleaved.append(src_lines[i])

    body = '\n'.join(interleaved)
    out_path.write_text(body, encoding='utf-8')
    if verbose:
        print(f'連結コーパス保存 (ラウンドロビン交互): {out_path} '
              f'({len(body)} chars, {len(interleaved)} lines, sources={sources})')
        _print_corpus_sample(body, label='Combined')
    return out_path
