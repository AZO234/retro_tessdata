# レトロPCフォント Tesseract学習データ

<img src="images/learning.png">

レトロPCのフォントから作成したTesseract用学習データです。  
`tessdata` ディレクトリをご覧ください。zipファイルは解凍してお使いください。

ドットグリフの学習データなので、印刷物のOCRは向いてないと思います。



## 動作手順

### 準備・インストール

#### Windows

- Visual Studio 2026 (C++)

- Python 3.13

エイリアス解除を、管理者権限のPowerShellで実行

```powershell
Remove-Item "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe" -Force
Remove-Item "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe" -Force
```

環境変数のPATHに`C:\Python313`を追加する。

- vcpkg

```powershell
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
```

- Tesseract

```powershell
.\vcpkg.exe install tesseract[training-tools]:x64-windows
```

環境変数のPATHに`C:\vcpkg\packages\tesseract_x64-windows\tools\tesseract`を追加する。

- この学習環境をインストール

```powershell
git clone https://github.com/AZO234/retro_tessdata.git
cd retro_tessdata
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Linux/macOS

- Tesseract（学習ツール `lstmtraining` 等を含む）

```bash
$ cd ~
$ sudo apt-get install tesseract-ocr tesseract-ocr-all
```

- この学習環境をインストール

```bash
$ git clone https://github.com/AZO234/retro_tessdata.git
$ cd retro_tessdata
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Python依存は `Pillow` と `numpy` のみです（lstmf は Python で直接生成するため text2image 等は不要）。  
ただし Tesseract 本体に加え、学習用バイナリ `lstmtraining` / `combine_lang_model` /
`unicharset_extractor` / `merge_unicharsets` / `combine_tessdata` が PATH 上に必要です。



### フォントROM配置

#### PC-8801

- `rom/pc88/KANJI1.ROM`
- `rom/pc88/KANJI2.ROM`

#### PC-9801

- `rom/pc98/FONT.ROM`

#### MSX

- `rom/msx/JAPANESE.FNT`
- `rom/msx/fs-a1gt_kanjifont.rom`

#### X68000

- `rom/x68k/CGROM.DAT`

#### FM-77(FM-7)

- `rom/fm77/subsys_c.rom`
- `rom/fm77/kanji.rom`

#### FM-TOWNS (FMR-60/70互換)

- `rom/fmt/FMT_F20.ROM`

- `rom/fmt/FMT_FNT.ROM`



### 学習

#### Windows

```powershell
.venv\Scripts\activate
python main.py <architecture> full --iterate 100000
```

#### POSIX

```bash
$ source .venv/bin/activate
$ python main.py <architecture> full --iterate 100000
```

`<architecture>` は対象機種名。

- PC-8801 ： `pc88`  `pc88_vert` `pc88_scan`
- PC-9801 ： `pc98` `pc98_vert` `pc98_scan`
- MSX ： `msx` `msx_vert` `msx_scan`
- X68000 ： `x68k` `x68k_vert` `x68k_scan`
- FM-77(FM-7) ： `fm77` `fm77_vert` `fm77_scan`
- FM-TOWNS (FMR-60/70互換)： `fmt` `fmt_vert` `fmt_scan`  `f20` `f20_vert` `f20_scan`

`***_vert`で縦書き用。

- `ー—〜… ‥`（長音類）、および `「」 （） 『』【】` などの括弧類 を右に90度回転
  - 長音の縦書きは、厳密には書き始めの「ハネ」は無く書き終わりは「止め」になるが、あえてこのまま
- `、 。ぁぃぅぇぉっゃゅょァィゥェォッャュョ` を左下から右上にシフト

`***_scan`でスキャンライン挿入用。

- スキャンラインを挿入して縦に倍加した全角文字（半角は通常サイズ）。横書き専用



#### 処理ステップ（`<function>`）

`full` は一連の処理をまとめて実行します。個別に実行することもできます。

| function | 内容 |
| --- | --- |
| `clean`    | 生成物・中間ファイルの削除 |
| `generate` | 学習画像（`.tif` / `.box`）生成 |
| `image`    | マルチページTIFを1ページPNGに変換（確認用） |
| `concat`   | unicharset + starter traineddata + lstmf 生成 |
| `train`    | lstmtraining + エクスポート |
| `full`     | 上記を `clean → generate → image → concat → train` の順に一括実行 |

学習だけ追加したい場合は `python main.py <architecture> train --iterate 200000` を実行
（既存チェックポイントから継続学習します）。



#### オプション

| オプション | デフォルト | 説明 |
| --- | --- | --- |
| `--iterate N`              | 10000          | 学習イテレーション数（本番推奨: 100000〜） |
| `--padding N`              | 1              | セルパディング（ドット）。グリフ周囲の余白。行ごとにジッタ化され、字間やベースラインを区切り信号として過学習する問題を防ぐ |
| `--style name:weight`     | `bold:3` `normal:1` | フォントスタイルと重み。複数指定可。`bold`=太字 / `normal`=通常 |
| `--range RANGE`           | all            | 文字範囲をカンマ区切りで限定（`ascii,kana,jis1,jis2,jis_misc,jis_ext`） |
| `--limit-chars N`         | 0              | 各カテゴリの最大文字数（0=無制限）。お試し用 |
| `--tight-pack` / `--no-tight-pack` | tight-pack | 上下余白を詰める／詰めない（詰めない場合 net_h=32 固定） |
| `--corpus TOKENS`         | （なし＝辞書順） | 実文章コーパスで学習行を生成（下記参照） |
| `--max-lines N`           | 10000          | コーパスから生成する最大行数 |
| `--finetune BASE_LANG`    | jpn            | ベース言語からファインチューニング（下記参照） |
| `--no-finetune`           | —              | フルスクラッチ学習（`--finetune` より優先） |

`python main.py -h` でヘルプ表示。



#### スタイル（`--style`）

`--style bold:3` は「太字スタイル＆重み3」の意味。`--style` を複数指定すると、その比率で
混ぜて学習します。未指定時のデフォルトは `bold:3` ＋ `normal:1`（実ゲーム画面の多くが
ボールド体のため、太字を主ドメインにしている）。

利用可能なスタイルは `bold`（太字）と `normal`（通常）の2つ。  
※ 黒地白文字（inverse）スタイルとノイズ付加機能は廃止しました。本番の前処理が必ず
白地黒文字へ正規化し、2値化で薄い汚れも消えるため、逆極性・ノイズデータは推論で意味を
持たないためです。



#### 実文章コーパス（`--corpus`）

未指定だと文字をJIS辞書順に並べただけの学習行になりますが、`--corpus` を指定すると
実際の日本語文章を学習行に使えます（言語モデル文脈が付くため実画面での認識精度が
上がりやすい）。トークンを `+` で連結指定します。

| トークン | 内容 |
| --- | --- |
| `auto`    | 青空文庫（文学） |
| `wiki`    | Wikipedia ゲーム/アニメ等サブカル |
| `wikigen` | Wikipedia 現代一般（科学/社会/歴史/文化 等） |
| `kanwa`   | Wiktionary 慣用句・ことわざ・四字熟語 |

例：

```bash
$ python main.py pc98 full --iterate 100000 --corpus auto+wiki+wikigen+kanwa
```



#### ファインチューニング（`--finetune` / `--no-finetune`）

デフォルトでは `--finetune jpn` が有効で、`tessdata_best` の `jpn` モデルから継続学習します
（jpn の unicharset を併合し、jpn の LSTM 重みを初期値にする）。日本語認識能力を引き継げる
ため、少ないイテレーションでも実用精度に届きやすくなります。  
完全にゼロから学習したい場合は `--no-finetune` を指定してください。

`--iterate 100000` は10万回学習の意味。BCERが十分下がれば（ほぼ0%）学習完了の目安です。



### 出力学習データ

学習結果は作業ディレクトリ `base_<機種>/tessdata/` に出力されます。

- 横書き： `base_<機種>/tessdata/<機種>.traineddata`（例 `base_pc98/tessdata/pc98.traineddata`）
- 縦書き： `base_<機種>/tessdata/<機種>_vert.traineddata`（例 `base_pc98/tessdata/pc98_vert.traineddata`）
- スキャン： `base_<機種>/tessdata/<機種>_scan.traineddata`

使用時は Tesseract の `tessdata` ディレクトリ（または `--tessdata-dir`）に置き、
`tesseract image.png out -l pc98` のように機種名で指定します。複数機種を併用するなら
`-l pc98+pc88+x68k` のように `+` で連結できます。



## 学習データの扱いについて

日本においてAIの学習データ利用は、著作権法第30条の4に基づき、原則として無断で行うことが可能です。
（しかしながら、意匠の関係性が切り離せないものでもあります。）



## ライセンス

GPL-3.0
