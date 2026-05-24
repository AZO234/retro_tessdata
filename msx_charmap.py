# MSX 非漢字キャラクターマッピング補正テーブル
# 視覚確認用画像: /tmp/msx_nonkanji_detailed.png
#
# ベースライン: euc_jp でデコードした値。デコード不能な位置は euc_jis_2004 で補完。
# ROMのグリフとラベルが一致しない場合は右辺の文字を正しいものに書き換えてください。
# ERR=両方失敗。正しい文字を入れてください（空文字列のまま → PUA文字で代替）。

# ===== 0区 (jis1=0x20): 標準JIS前の拡張全角文字 =====
# 確認画像: /tmp/msx_extra_chars.png (上段)
# グリフを見て正しい文字を入れてください。
ROW0_OVERRIDES = {
    (0x20, 0x21): '',  # ten= 1
    (0x20, 0x22): '',  # ten= 2
    (0x20, 0x23): '',  # ten= 3
    (0x20, 0x24): '',  # ten= 4
    (0x20, 0x25): '',  # ten= 5
    (0x20, 0x26): '',  # ten= 6
    (0x20, 0x27): '',  # ten= 7
    (0x20, 0x28): '',  # ten= 8
    (0x20, 0x29): '',  # ten= 9
    (0x20, 0x2A): '',  # ten=10
    (0x20, 0x2B): '',  # ten=11
    (0x20, 0x2C): '',  # ten=12
    (0x20, 0x2D): '',  # ten=13
    (0x20, 0x2E): '',  # ten=14
    (0x20, 0x2F): '',  # ten=15
    (0x20, 0x30): '',  # ten=16
    (0x20, 0x31): '',  # ten=17
    (0x20, 0x32): '',  # ten=18
    (0x20, 0x33): '',  # ten=19
    (0x20, 0x34): '',  # ten=20
    (0x20, 0x35): '',  # ten=21
    (0x20, 0x36): '',  # ten=22
    (0x20, 0x37): '',  # ten=23
    (0x20, 0x38): '',  # ten=24
    (0x20, 0x39): '',  # ten=25
    (0x20, 0x3A): '',  # ten=26
    (0x20, 0x3B): '',  # ten=27
    (0x20, 0x3C): '',  # ten=28
    (0x20, 0x3D): '',  # ten=29
    (0x20, 0x3E): '',  # ten=30
    (0x20, 0x3F): '',  # ten=31
    (0x20, 0x40): '',  # ten=32
    (0x20, 0x41): '',  # ten=33
    (0x20, 0x42): '',  # ten=34
    (0x20, 0x43): '',  # ten=35
    (0x20, 0x44): '',  # ten=36
    (0x20, 0x45): '',  # ten=37
    (0x20, 0x46): '',  # ten=38
    (0x20, 0x47): '',  # ten=39
    (0x20, 0x48): '',  # ten=40
    (0x20, 0x49): '',  # ten=41
    (0x20, 0x4A): '',  # ten=42
    (0x20, 0x4B): '',  # ten=43
    (0x20, 0x4C): '',  # ten=44
    (0x20, 0x4D): '',  # ten=45
    (0x20, 0x4E): '',  # ten=46
    (0x20, 0x4F): '',  # ten=47
    (0x20, 0x50): '',  # ten=48
    (0x20, 0x51): '',  # ten=49
    (0x20, 0x52): '',  # ten=50
    (0x20, 0x53): '',  # ten=51
    (0x20, 0x54): '',  # ten=52
    (0x20, 0x55): '',  # ten=53
    (0x20, 0x56): '',  # ten=54
    (0x20, 0x57): '',  # ten=55
    (0x20, 0x58): '',  # ten=56
    (0x20, 0x59): '',  # ten=57
    (0x20, 0x5A): '',  # ten=58
    (0x20, 0x5B): '',  # ten=59
    (0x20, 0x5C): '',  # ten=60
    (0x20, 0x5D): '',  # ten=61
    (0x20, 0x5E): '',  # ten=62
    (0x20, 0x5F): '',  # ten=63
    (0x20, 0x60): '',  # ten=64
    (0x20, 0x61): '',  # ten=65
    (0x20, 0x62): '',  # ten=66
    (0x20, 0x63): '',  # ten=67
    (0x20, 0x64): '',  # ten=68
    (0x20, 0x65): '',  # ten=69
    (0x20, 0x66): '',  # ten=70
    (0x20, 0x67): '',  # ten=71
    (0x20, 0x68): '',  # ten=72
    (0x20, 0x69): '',  # ten=73
    (0x20, 0x6A): '',  # ten=74
    (0x20, 0x6B): '',  # ten=75
    (0x20, 0x6C): '',  # ten=76
    (0x20, 0x6D): '',  # ten=77
    (0x20, 0x6E): '',  # ten=78
    (0x20, 0x6F): '',  # ten=79
    (0x20, 0x70): '',  # ten=80
    (0x20, 0x71): '',  # ten=81
    (0x20, 0x72): '',  # ten=82
    (0x20, 0x73): '',  # ten=83
    (0x20, 0x74): '',  # ten=84
    (0x20, 0x75): '',  # ten=85
    (0x20, 0x76): '',  # ten=86
    (0x20, 0x77): '',  # ten=87
    (0x20, 0x78): '',  # ten=88
    (0x20, 0x79): '',  # ten=89
    (0x20, 0x7A): '',  # ten=90
    (0x20, 0x7B): '',  # ten=91
    (0x20, 0x7C): '',  # ten=92
    (0x20, 0x7D): '',  # ten=93
    (0x20, 0x7E): '',  # ten=94
}

CHAR_OVERRIDES = {
    # ===== Row 1: 記号・括弧・数学記号 =====
    (0x21, 0x21): '',  # ten= 1  U+3000 IDEOGRAPHIC SPACE 
    (0x21, 0x22): '',  # ten= 2  U+3001 IDEOGRAPHIC COMMA 
    (0x21, 0x23): '',  # ten= 3  U+3002 IDEOGRAPHIC FULL STOP 
    (0x21, 0x24): '',  # ten= 4  U+FF0C FULLWIDTH COMMA 
    (0x21, 0x25): '',  # ten= 5  U+FF0E FULLWIDTH FULL STOP 
    (0x21, 0x26): '',  # ten= 6  U+30FB KATAKANA MIDDLE DOT 
    (0x21, 0x27): '',  # ten= 7  U+FF1A FULLWIDTH COLON 
    (0x21, 0x28): '',  # ten= 8  U+FF1B FULLWIDTH SEMICOLON 
    (0x21, 0x29): '',  # ten= 9  U+FF1F FULLWIDTH QUESTION MARK 
    (0x21, 0x2A): '',  # ten=10  U+FF01 FULLWIDTH EXCLAMATION MARK 
    (0x21, 0x2B): '',  # ten=11  U+309B KATAKANA-HIRAGANA VOICED SOUND MARK 
    (0x21, 0x2C): '',  # ten=12  U+309C KATAKANA-HIRAGANA SEMI-VOICED SOUND 
    (0x21, 0x2D): '',  # ten=13  U+00B4 ACUTE ACCENT 
    (0x21, 0x2E): '',  # ten=14  U+FF40 FULLWIDTH GRAVE ACCENT 
    (0x21, 0x2F): '',  # ten=15  U+00A8 DIAERESIS 
    (0x21, 0x30): '',  # ten=16  U+FF3E FULLWIDTH CIRCUMFLEX ACCENT 
    (0x21, 0x31): '',  # ten=17  U+FFE3 FULLWIDTH MACRON 
    (0x21, 0x32): '',  # ten=18  U+FF3F FULLWIDTH LOW LINE 
    (0x21, 0x33): '',  # ten=19  U+30FD KATAKANA ITERATION MARK 
    (0x21, 0x34): '',  # ten=20  U+30FE KATAKANA VOICED ITERATION MARK 
    (0x21, 0x35): '',  # ten=21  U+309D HIRAGANA ITERATION MARK 
    (0x21, 0x36): '',  # ten=22  U+309E HIRAGANA VOICED ITERATION MARK 
    (0x21, 0x37): '',  # ten=23  U+3003 DITTO MARK 
    (0x21, 0x38): '',  # ten=24  U+4EDD CJK UNIFIED IDEOGRAPH-4EDD 
    (0x21, 0x39): '',  # ten=25  U+3005 IDEOGRAPHIC ITERATION MARK 
    (0x21, 0x3A): '',  # ten=26  U+3006 IDEOGRAPHIC CLOSING MARK 
    (0x21, 0x3B): '',  # ten=27  U+3007 IDEOGRAPHIC NUMBER ZERO 
    (0x21, 0x3C): '',  # ten=28  U+30FC KATAKANA-HIRAGANA PROLONGED SOUND M 
    (0x21, 0x3D): '',  # ten=29  U+2015 HORIZONTAL BAR 
    (0x21, 0x3E): '',  # ten=30  U+2010 HYPHEN 
    (0x21, 0x40): '',  # ten=32  U+FF3C FULLWIDTH REVERSE SOLIDUS 
    (0x21, 0x42): '、',  # ten=34  U+2016 DOUBLE VERTICAL LINE 
    (0x21, 0x43): '。',  # ten=35  U+FF5C FULLWIDTH VERTICAL LINE 
    (0x21, 0x44): '，',  # ten=36  U+2026 HORIZONTAL ELLIPSIS 
    (0x21, 0x45): '．',  # ten=37  U+2025 TWO DOT LEADER 
    (0x21, 0x46): '・',  # ten=38  U+2018 LEFT SINGLE QUOTATION MARK 
    (0x21, 0x47): '：',  # ten=39  U+2019 RIGHT SINGLE QUOTATION MARK 
    (0x21, 0x48): '；',  # ten=40  U+201C LEFT DOUBLE QUOTATION MARK 
    (0x21, 0x49): '？',  # ten=41  U+201D RIGHT DOUBLE QUOTATION MARK 
    (0x21, 0x4A): '！',  # ten=42  U+FF08 FULLWIDTH LEFT PARENTHESIS 
    (0x21, 0x4B): '゛',  # ten=43  U+FF09 FULLWIDTH RIGHT PARENTHESIS 
    (0x21, 0x4C): '゜',  # ten=44  U+3014 LEFT TORTOISE SHELL BRACKET 
    (0x21, 0x4D): '´',  # ten=45  U+3015 RIGHT TORTOISE SHELL BRACKET 
    (0x21, 0x4E): '｀',  # ten=46  U+FF3B FULLWIDTH LEFT SQUARE BRACKET 
    (0x21, 0x4F): '¨',  # ten=47  U+FF3D FULLWIDTH RIGHT SQUARE BRACKET 
    (0x21, 0x50): '＾',  # ten=48  U+FF5B FULLWIDTH LEFT CURLY BRACKET 
    (0x21, 0x51): '￣',  # ten=49  U+FF5D FULLWIDTH RIGHT CURLY BRACKET 
    (0x21, 0x52): '＿',  # ten=50  U+3008 LEFT ANGLE BRACKET 
    (0x21, 0x53): 'ヽ',  # ten=51  U+3009 RIGHT ANGLE BRACKET 
    (0x21, 0x54): 'ヾ',  # ten=52  U+300A LEFT DOUBLE ANGLE BRACKET 
    (0x21, 0x55): 'ゝ',  # ten=53  U+300B RIGHT DOUBLE ANGLE BRACKET 
    (0x21, 0x56): 'ゞ',  # ten=54  U+300C LEFT CORNER BRACKET 
    (0x21, 0x57): '〃',  # ten=55  U+300D RIGHT CORNER BRACKET 
    (0x21, 0x58): '仝',  # ten=56  U+300E LEFT WHITE CORNER BRACKET 
    (0x21, 0x59): '々',  # ten=57  U+300F RIGHT WHITE CORNER BRACKET 
    (0x21, 0x5A): '〆',  # ten=58  U+3010 LEFT BLACK LENTICULAR BRACKET 
    (0x21, 0x5B): '〇',  # ten=59  U+3011 RIGHT BLACK LENTICULAR BRACKET 
    (0x21, 0x5C): 'ー',  # ten=60  U+FF0B FULLWIDTH PLUS SIGN 
    (0x21, 0x5D): '―',  # ten=61  U+2212 MINUS SIGN
    (0x21, 0x5E): '‐',  # ten=62  U+00B1 PLUS-MINUS SIGN 
    (0x21, 0x5F): '＼',  # ten=63  U+00D7 MULTIPLICATION SIGN 
    (0x21, 0x60): '‖',  # ten=64  U+00F7 DIVISION SIGN 
    (0x21, 0x61): '｜',  # ten=65  U+FF1D FULLWIDTH EQUALS SIGN 
    (0x21, 0x62): '…',  # ten=66  U+2260 NOT EQUAL TO 
    (0x21, 0x63): '‥',  # ten=67  U+FF1C FULLWIDTH LESS-THAN SIGN 
    (0x21, 0x64): '‘',  # ten=68  U+FF1E FULLWIDTH GREATER-THAN SIGN 
    (0x21, 0x65): '’',  # ten=69  U+2266 LESS-THAN OVER EQUAL TO 
    (0x21, 0x66): '“',  # ten=70  U+2267 GREATER-THAN OVER EQUAL TO 
    (0x21, 0x67): '”',  # ten=71  U+221E INFINITY 
    (0x21, 0x68): '（',  # ten=72  U+2234 THEREFORE 
    (0x21, 0x69): '）',  # ten=73  U+2642 MALE SIGN 
    (0x21, 0x6A): '〔',  # ten=74  U+2640 FEMALE SIGN 
    (0x21, 0x6B): '〕',  # ten=75  U+00B0 DEGREE SIGN 
    (0x21, 0x6C): '↑',  # ten=76  U+2032 PRIME 
    (0x21, 0x6D): '↓',  # ten=77  U+2033 DOUBLE PRIME 
    (0x21, 0x6E): '［',  # ten=78  U+2103 DEGREE CELSIUS 
    (0x21, 0x6F): '］',  # ten=79  U+FFE5 FULLWIDTH YEN SIGN 
    (0x21, 0x70): '｛',  # ten=80  U+FF04 FULLWIDTH DOLLAR SIGN 
    (0x21, 0x71): '｝',  # ten=81  U+00A2 CENT SIGN 
    (0x21, 0x72): '〈',  # ten=82  U+00A3 POUND SIGN 
    (0x21, 0x73): '〉',  # ten=83  U+FF05 FULLWIDTH PERCENT SIGN 
    (0x21, 0x74): '《',  # ten=84  U+FF03 FULLWIDTH NUMBER SIGN 
    (0x21, 0x75): '》',  # ten=85  U+FF06 FULLWIDTH AMPERSAND 
    (0x21, 0x76): '「',  # ten=86  U+FF0A FULLWIDTH ASTERISK 
    (0x21, 0x77): '」',  # ten=87  U+FF20 FULLWIDTH COMMERCIAL AT 
    (0x21, 0x78): '『',  # ten=88  U+00A7 SECTION SIGN 
    (0x21, 0x79): '』',  # ten=89  U+2606 WHITE STAR 
    (0x21, 0x7A): '【',  # ten=90  U+2605 BLACK STAR 
    (0x21, 0x7B): '】',  # ten=91  U+25CB WHITE CIRCLE 
    (0x21, 0x7C): '＋',  # ten=92  U+25CF BLACK CIRCLE 
    (0x21, 0x7D): '−',  # ten=93  U+25CE BULLSEYE 
    (0x21, 0x7E): '±',  # ten=94  U+25C7 WHITE DIAMOND 

    # ===== Row 2: 特殊記号・数学 =====
    (0x22, 0x21): '〜',  # ten= 1  U+25C6 BLACK DIAMOND 
    (0x22, 0x22): '‖',  # ten= 2  U+25A1 WHITE SQUARE 
    (0x22, 0x23): '｜',  # ten= 3  U+25A0 BLACK SQUARE 
    (0x22, 0x24): '…',  # ten= 4  U+25B3 WHITE UP-POINTING TRIANGLE 
    (0x22, 0x25): '‥',  # ten= 5  U+25B2 BLACK UP-POINTING TRIANGLE 
    (0x22, 0x26): '‘',  # ten= 6  U+25BD WHITE DOWN-POINTING TRIANGLE 
    (0x22, 0x27): '’',  # ten= 7  U+25BC BLACK DOWN-POINTING TRIANGLE 
    (0x22, 0x28): '“',  # ten= 8  U+203B REFERENCE MARK 
    (0x22, 0x29): '”',  # ten= 9  U+3012 POSTAL MARK 
    (0x22, 0x2A): '（',  # ten=10  U+2192 RIGHTWARDS ARROW 
    (0x22, 0x2B): '）',  # ten=11  U+2190 LEFTWARDS ARROW 
    (0x22, 0x2C): '〔',  # ten=12  U+2191 UPWARDS ARROW 
    (0x22, 0x2D): '〕',  # ten=13  U+2193 DOWNWARDS ARROW 
    (0x22, 0x2E): '［',  # ten=14  U+3013 GETA MARK 
    (0x22, 0x2F): '］',  # ten=15  U+FF07 FULLWIDTH APOSTROPHE (jis2004)
    (0x22, 0x30): '｛',  # ten=16  U+FF02 FULLWIDTH QUOTATION MARK (jis2004)
    (0x22, 0x31): '｝',  # ten=17  U+FF0D FULLWIDTH HYPHEN-MINUS (jis2004)
    (0x22, 0x32): '〈',  # ten=18  U+FF5E FULLWIDTH TILDE (jis2004)
    (0x22, 0x33): '〉',  # ten=19  U+3033 VERTICAL KANA REPEAT MARK UPPER HAL (jis2004)
    (0x22, 0x34): '《',  # ten=20  U+3034 VERTICAL KANA REPEAT WITH VOICED SO (jis2004)
    (0x22, 0x35): '》',  # ten=21  U+3035 VERTICAL KANA REPEAT MARK LOWER HAL (jis2004)
    (0x22, 0x36): '「',  # ten=22  U+303B VERTICAL IDEOGRAPHIC ITERATION MARK (jis2004)
    (0x22, 0x37): '」',  # ten=23  U+303C MASU MARK (jis2004)
    (0x22, 0x38): '『',  # ten=24  U+30FF KATAKANA DIGRAPH KOTO (jis2004)
    (0x22, 0x39): '』',  # ten=25  U+309F HIRAGANA DIGRAPH YORI (jis2004)
    (0x22, 0x3A): '【',  # ten=26  U+2208 ELEMENT OF 
    (0x22, 0x3B): '】',  # ten=27  U+220B CONTAINS AS MEMBER 
    (0x22, 0x3C): '＋',  # ten=28  U+2286 SUBSET OF OR EQUAL TO 
    (0x22, 0x3D): '−',  # ten=29  U+2287 SUPERSET OF OR EQUAL TO
    (0x22, 0x3E): '±',  # ten=30  U+2282 SUBSET OF 
    (0x22, 0x3F): '×',  # ten=31  U+2283 SUPERSET OF 
    (0x22, 0x40): '÷',  # ten=32  U+222A UNION 
    (0x22, 0x41): '＝',  # ten=33  U+2229 INTERSECTION 
    (0x22, 0x42): '≠',  # ten=34  U+2284 NOT A SUBSET OF (jis2004)
    (0x22, 0x43): '＜',  # ten=35  U+2285 NOT A SUPERSET OF (jis2004)
    (0x22, 0x44): '＞',  # ten=36  U+228A SUBSET OF WITH NOT EQUAL TO (jis2004)
    (0x22, 0x45): '≦',  # ten=37  U+228B SUPERSET OF WITH NOT EQUAL TO (jis2004)
    (0x22, 0x46): '≧',  # ten=38  U+2209 NOT AN ELEMENT OF (jis2004)
    (0x22, 0x47): '∞',  # ten=39  U+2205 EMPTY SET (jis2004)
    (0x22, 0x48): '∴',  # ten=40  U+2305 PROJECTIVE (jis2004)
    (0x22, 0x49): '♂',  # ten=41  U+2306 PERSPECTIVE (jis2004)
    (0x22, 0x4A): '♀',  # ten=42  U+2227 LOGICAL AND 
    (0x22, 0x4B): '°',  # ten=43  U+2228 LOGICAL OR 
    (0x22, 0x4C): '′',  # ten=44  U+00AC NOT SIGN 
    (0x22, 0x4D): '″',  # ten=45  U+21D2 RIGHTWARDS DOUBLE ARROW 
    (0x22, 0x4E): '℃',  # ten=46  U+21D4 LEFT RIGHT DOUBLE ARROW 
    (0x22, 0x4F): '￥',  # ten=47  U+2200 FOR ALL 
    (0x22, 0x50): '＄',  # ten=48  U+2203 THERE EXISTS 
    (0x22, 0x51): '¢',  # ten=49  U+2295 CIRCLED PLUS (jis2004)
    (0x22, 0x52): '£',  # ten=50  U+2296 CIRCLED MINUS (jis2004)
    (0x22, 0x53): '％',  # ten=51  U+2297 CIRCLED TIMES (jis2004)
    (0x22, 0x54): '＃',  # ten=52  U+2225 PARALLEL TO (jis2004)
    (0x22, 0x55): '＆',  # ten=53  U+2226 NOT PARALLEL TO (jis2004)
    (0x22, 0x56): '＊',  # ten=54  U+2985 LEFT WHITE PARENTHESIS (jis2004)
    (0x22, 0x57): '＠',  # ten=55  U+2986 RIGHT WHITE PARENTHESIS (jis2004)
    (0x22, 0x58): '§',  # ten=56  U+3018 LEFT WHITE TORTOISE SHELL BRACKET (jis2004)
    (0x22, 0x59): '☆',  # ten=57  U+3019 RIGHT WHITE TORTOISE SHELL BRACKET (jis2004)
    (0x22, 0x5A): '★',  # ten=58  U+3016 LEFT WHITE LENTICULAR BRACKET (jis2004)
    (0x22, 0x5B): '○',  # ten=59  U+3017 RIGHT WHITE LENTICULAR BRACKET (jis2004)
    (0x22, 0x5C): '●',  # ten=60  U+2220 ANGLE 
    (0x22, 0x5D): '◎',  # ten=61  U+22A5 UP TACK 
    (0x22, 0x5E): '◇',  # ten=62  U+2312 ARC 
    (0x22, 0x5F): '▶',  # ten=63  U+2202 PARTIAL DIFFERENTIAL 
    (0x22, 0x60): '',  # ten=64  U+2207 NABLA 
    (0x22, 0x61): '◆',  # ten=65  U+2261 IDENTICAL TO 
    (0x22, 0x62): '□',  # ten=66  U+2252 APPROXIMATELY EQUAL TO OR THE IMAGE 
    (0x22, 0x63): '■',  # ten=67  U+226A MUCH LESS-THAN 
    (0x22, 0x64): '△',  # ten=68  U+226B MUCH GREATER-THAN 
    (0x22, 0x65): '▲',  # ten=69  U+221A SQUARE ROOT 
    (0x22, 0x66): '▽',  # ten=70  U+223D REVERSED TILDE 
    (0x22, 0x67): '▼',  # ten=71  U+221D PROPORTIONAL TO 
    (0x22, 0x68): '※',  # ten=72  U+2235 BECAUSE 
    (0x22, 0x69): '〒',  # ten=73  U+222B INTEGRAL 
    (0x22, 0x6A): '→',  # ten=74  U+222C DOUBLE INTEGRAL 
    (0x22, 0x6B): '←',  # ten=75  U+2262 NOT IDENTICAL TO (jis2004)
    (0x22, 0x6C): '↑',  # ten=76  U+2243 ASYMPTOTICALLY EQUAL TO (jis2004)
    (0x22, 0x6D): '↓',  # ten=77  U+2245 APPROXIMATELY EQUAL TO (jis2004)
    (0x22, 0x6E): '〓',  # ten=78  U+2248 ALMOST EQUAL TO (jis2004)
    (0x22, 0x6F): '㈱',  # ten=79  U+2276 LESS-THAN OR GREATER-THAN (jis2004)
    (0x22, 0x70): '㈲',  # ten=80  U+2277 GREATER-THAN OR LESS-THAN (jis2004)
    (0x22, 0x71): 'Ⅰ',  # ten=81  U+2194 LEFT RIGHT ARROW (jis2004)
    (0x22, 0x72): 'Ⅱ',  # ten=82  U+212B ANGSTROM SIGN 
    (0x22, 0x73): 'Ⅲ',  # ten=83  U+2030 PER MILLE SIGN 
    (0x22, 0x74): 'Ⅳ',  # ten=84  U+266F MUSIC SHARP SIGN 
    (0x22, 0x75): 'Ⅴ',  # ten=85  U+266D MUSIC FLAT SIGN 
    (0x22, 0x76): 'Ⅵ',  # ten=86  U+266A EIGHTH NOTE 
    (0x22, 0x77): 'Ⅶ',  # ten=87  U+2020 DAGGER 
    (0x22, 0x78): 'Ⅷ',  # ten=88  U+2021 DOUBLE DAGGER 
    (0x22, 0x79): 'Ⅸ',  # ten=89  U+00B6 PILCROW SIGN 
    (0x22, 0x7A): 'Ⅹ',  # ten=90  U+266E MUSIC NATURAL SIGN (jis2004)
    (0x22, 0x7B): '',  # ten=91  U+266B BEAMED EIGHTH NOTES (jis2004)
    (0x22, 0x7C): '',  # ten=92  U+266C BEAMED SIXTEENTH NOTES (jis2004)
    (0x22, 0x7D): '㎝',  # ten=93  U+2669 QUARTER NOTE (jis2004)
    (0x22, 0x7E): '㎜',  # ten=94  U+25EF LARGE CIRCLE 

    # ===== Row 3: 数字・記号 =====
    (0x23, 0x21): '◆',  # ten= 1  U+25B7 WHITE RIGHT-POINTING TRIANGLE (jis2004)
    (0x23, 0x22): '□',  # ten= 2  U+25B6 BLACK RIGHT-POINTING TRIANGLE (jis2004)
    (0x23, 0x23): '■',  # ten= 3  U+25C1 WHITE LEFT-POINTING TRIANGLE (jis2004)
    (0x23, 0x24): '△',  # ten= 4  U+25C0 BLACK LEFT-POINTING TRIANGLE (jis2004)
    (0x23, 0x25): '▲',  # ten= 5  U+2197 NORTH EAST ARROW (jis2004)
    (0x23, 0x26): '▽',  # ten= 6  U+2198 SOUTH EAST ARROW (jis2004)
    (0x23, 0x27): '▼',  # ten= 7  U+2196 NORTH WEST ARROW (jis2004)
    (0x23, 0x28): '※',  # ten= 8  U+2199 SOUTH WEST ARROW (jis2004)
    (0x23, 0x29): '〒',  # ten= 9  U+21C4 RIGHTWARDS ARROW OVER LEFTWARDS ARR (jis2004)
    (0x23, 0x2A): '→',  # ten=10  U+21E8 RIGHTWARDS WHITE ARROW (jis2004)
    (0x23, 0x2B): '←',  # ten=11  U+21E6 LEFTWARDS WHITE ARROW (jis2004)
    (0x23, 0x2C): '↑',  # ten=12  U+21E7 UPWARDS WHITE ARROW (jis2004)
    (0x23, 0x2D): '↓',  # ten=13  U+21E9 DOWNWARDS WHITE ARROW (jis2004)
    (0x23, 0x2E): '〓',  # ten=14  U+2934 ARROW POINTING RIGHTWARDS THEN CURV (jis2004)
    (0x23, 0x2F): '㈱',  # ten=15  U+2935 ARROW POINTING RIGHTWARDS THEN CURV (jis2004)
    (0x23, 0x30): '㈲',  # ten=16  U+FF10 FULLWIDTH DIGIT ZERO 
    (0x23, 0x31): 'Ⅰ',  # ten=17  U+FF11 FULLWIDTH DIGIT ONE 
    (0x23, 0x32): 'Ⅱ',  # ten=18  U+FF12 FULLWIDTH DIGIT TWO 
    (0x23, 0x33): 'Ⅲ',  # ten=19  U+FF13 FULLWIDTH DIGIT THREE 
    (0x23, 0x34): 'Ⅳ',  # ten=20  U+FF14 FULLWIDTH DIGIT FOUR 
    (0x23, 0x35): 'Ⅴ',  # ten=21  U+FF15 FULLWIDTH DIGIT FIVE 
    (0x23, 0x36): 'Ⅵ',  # ten=22  U+FF16 FULLWIDTH DIGIT SIX 
    (0x23, 0x37): 'Ⅶ',  # ten=23  U+FF17 FULLWIDTH DIGIT SEVEN 
    (0x23, 0x38): 'Ⅷ',  # ten=24  U+FF18 FULLWIDTH DIGIT EIGHT 
    (0x23, 0x39): 'Ⅸ',  # ten=25  U+FF19 FULLWIDTH DIGIT NINE 
    (0x23, 0x3A): 'Ⅹ',  # ten=26  U+29BF CIRCLED BULLET (jis2004)
    (0x23, 0x3B): '',  # ten=27  U+25C9 FISHEYE (jis2004)
    (0x23, 0x3C): '',  # ten=28  U+303D PART ALTERNATION MARK (jis2004)
    (0x23, 0x3D): '㎝',  # ten=29  U+FE46 WHITE SESAME DOT (jis2004)
    (0x23, 0x3E): '㎜',  # ten=30  U+FE45 SESAME DOT (jis2004)
    (0x23, 0x3F): '㎞',  # ten=31  U+25E6 WHITE BULLET (jis2004)
    (0x23, 0x40): '',  # ten=32  U+2022 BULLET (jis2004)
    (0x23, 0x41): '㎡',  # ten=33  U+FF21 FULLWIDTH LATIN CAPITAL LETTER A 
    (0x23, 0x42): '',  # ten=34  U+FF22 FULLWIDTH LATIN CAPITAL LETTER B 
    (0x23, 0x43): '㎎',  # ten=35  U+FF23 FULLWIDTH LATIN CAPITAL LETTER C 
    (0x23, 0x44): '㎏',  # ten=36  U+FF24 FULLWIDTH LATIN CAPITAL LETTER D 
    (0x23, 0x45): '',  # ten=37  U+FF25 FULLWIDTH LATIN CAPITAL LETTER E 
    (0x23, 0x46): '㈹',  # ten=38  U+FF26 FULLWIDTH LATIN CAPITAL LETTER F 
    (0x23, 0x47): '㏍',  # ten=39  U+FF27 FULLWIDTH LATIN CAPITAL LETTER G 
    (0x23, 0x48): '№',  # ten=40  U+FF28 FULLWIDTH LATIN CAPITAL LETTER H 
    (0x23, 0x49): '㌅',  # ten=41  U+FF29 FULLWIDTH LATIN CAPITAL LETTER I 
    (0x23, 0x4A): '㌘',  # ten=42  U+FF2A FULLWIDTH LATIN CAPITAL LETTER J 
    (0x23, 0x4C): '㍍',  # ten=44  U+FF2C FULLWIDTH LATIN CAPITAL LETTER L 
    (0x23, 0x4D): '㌢',  # ten=45  U+FF2D FULLWIDTH LATIN CAPITAL LETTER M 
    (0x23, 0x4E): '㍉',  # ten=46  U+FF2E FULLWIDTH LATIN CAPITAL LETTER N 
    (0x23, 0x4F): '㌶',  # ten=47  U+FF2F FULLWIDTH LATIN CAPITAL LETTER O 
    (0x23, 0x50): '㌃',  # ten=48  U+FF30 FULLWIDTH LATIN CAPITAL LETTER P 
    (0x23, 0x51): '㌦',  # ten=49  U+FF31 FULLWIDTH LATIN CAPITAL LETTER Q 
    (0x23, 0x52): '㌧',  # ten=50  U+FF32 FULLWIDTH LATIN CAPITAL LETTER R 
    (0x23, 0x53): '㌔',  # ten=51  U+FF33 FULLWIDTH LATIN CAPITAL LETTER S 
    (0x23, 0x54): '㌕',  # ten=52  U+FF34 FULLWIDTH LATIN CAPITAL LETTER T 
    (0x23, 0x55): '㌗',  # ten=53  U+FF35 FULLWIDTH LATIN CAPITAL LETTER U 
    (0x23, 0x56): '㍗',  # ten=54  U+FF36 FULLWIDTH LATIN CAPITAL LETTER V 
    (0x23, 0x57): '㍑',  # ten=55  U+FF37 FULLWIDTH LATIN CAPITAL LETTER W 
    (0x23, 0x58): '㌫',  # ten=56  U+FF38 FULLWIDTH LATIN CAPITAL LETTER X 
    (0x23, 0x59): '㌻',  # ten=57  U+FF39 FULLWIDTH LATIN CAPITAL LETTER Y 
    (0x23, 0x5A): '㍎',  # ten=58  U+FF3A FULLWIDTH LATIN CAPITAL LETTER Z 
    (0x23, 0x5B): '㌳',  # ten=59  U+2213 MINUS-OR-PLUS SIGN (jis2004)
    (0x23, 0x5C): '①',  # ten=60  U+2135 ALEF SYMBOL (jis2004)
    (0x23, 0x5D): '②',  # ten=61  U+210F PLANCK CONSTANT OVER TWO PI (jis2004)
    (0x23, 0x5E): '③',  # ten=62  U+33CB SQUARE HP (jis2004)
    (0x23, 0x5F): '④',  # ten=63  U+2113 SCRIPT SMALL L (jis2004)
    (0x23, 0x60): '⑤',  # ten=64  U+2127 INVERTED OHM SIGN (jis2004)
    (0x23, 0x61): '⑥',  # ten=65  U+FF41 FULLWIDTH LATIN SMALL LETTER A 
    (0x23, 0x62): '⑦',  # ten=66  U+FF42 FULLWIDTH LATIN SMALL LETTER B 
    (0x23, 0x63): '⑧',  # ten=67  U+FF43 FULLWIDTH LATIN SMALL LETTER C 
    (0x23, 0x64): '⑨',  # ten=68  U+FF44 FULLWIDTH LATIN SMALL LETTER D 
    (0x23, 0x65): '⑩',  # ten=69  U+FF45 FULLWIDTH LATIN SMALL LETTER E 
    (0x23, 0x66): '〖',  # ten=70  U+FF46 FULLWIDTH LATIN SMALL LETTER F 
    (0x23, 0x67): '〗',  # ten=71  U+FF47 FULLWIDTH LATIN SMALL LETTER G 
    (0x23, 0x68): '〠',  # ten=72  U+FF48 FULLWIDTH LATIN SMALL LETTER H 
    (0x23, 0x69): '☎',  # ten=73  U+FF49 FULLWIDTH LATIN SMALL LETTER I 
    (0x23, 0x6A): '',  # ten=74  U+FF4A FULLWIDTH LATIN SMALL LETTER J 
    (0x23, 0x6B): '∫',  # ten=75  U+FF4B FULLWIDTH LATIN SMALL LETTER K 
    (0x23, 0x6C): '√',  # ten=76  U+FF4C FULLWIDTH LATIN SMALL LETTER L 
    (0x23, 0x6D): '',  # ten=77  U+FF4D FULLWIDTH LATIN SMALL LETTER M 
    (0x23, 0x6E): '',  # ten=78  U+FF4E FULLWIDTH LATIN SMALL LETTER N 
    (0x23, 0x6F): '',  # ten=79  U+FF4F FULLWIDTH LATIN SMALL LETTER O 
    (0x23, 0x70): '',  # ten=80  U+FF50 FULLWIDTH LATIN SMALL LETTER P 
    (0x23, 0x71): '',  # ten=81  U+FF51 FULLWIDTH LATIN SMALL LETTER Q 
    (0x23, 0x72): '',  # ten=82  U+FF52 FULLWIDTH LATIN SMALL LETTER R 
    (0x23, 0x73): '',  # ten=83  U+FF53 FULLWIDTH LATIN SMALL LETTER S 
    (0x23, 0x74): '',  # ten=84  U+FF54 FULLWIDTH LATIN SMALL LETTER T 
    (0x23, 0x75): '',  # ten=85  U+FF55 FULLWIDTH LATIN SMALL LETTER U 
    (0x23, 0x76): '',  # ten=86  U+FF56 FULLWIDTH LATIN SMALL LETTER V 
    (0x23, 0x77): '',  # ten=87  U+FF57 FULLWIDTH LATIN SMALL LETTER W 
    (0x23, 0x78): '',  # ten=88  U+FF58 FULLWIDTH LATIN SMALL LETTER X 
    (0x23, 0x79): '',  # ten=89  U+FF59 FULLWIDTH LATIN SMALL LETTER Y 
    (0x23, 0x7A): '',  # ten=90  U+FF5A FULLWIDTH LATIN SMALL LETTER Z 
    (0x23, 0x7B): '',  # ten=91  U+30A0 KATAKANA-HIRAGANA DOUBLE HYPHEN (jis2004)
    (0x23, 0x7C): '',  # ten=92  U+2013 EN DASH (jis2004)
    (0x23, 0x7D): '',  # ten=93  U+29FA DOUBLE PLUS (jis2004)
    (0x23, 0x7E): '',  # ten=94  U+29FB TRIPLE PLUS (jis2004)

    # ===== Row 4: ひらがな =====
    (0x24, 0x21): '⑤',  # ten= 1  U+3041 HIRAGANA LETTER SMALL A 
    (0x24, 0x22): '⑥',  # ten= 2  U+3042 HIRAGANA LETTER A 
    (0x24, 0x23): '⑦',  # ten= 3  U+3043 HIRAGANA LETTER SMALL I 
    (0x24, 0x24): '⑧',  # ten= 4  U+3044 HIRAGANA LETTER I 
    (0x24, 0x25): '⑨',  # ten= 5  U+3045 HIRAGANA LETTER SMALL U 
    (0x24, 0x26): '⑩',  # ten= 6  U+3046 HIRAGANA LETTER U 
    (0x24, 0x27): '〖',  # ten= 7  U+3047 HIRAGANA LETTER SMALL E 
    (0x24, 0x28): '〗',  # ten= 8  U+3048 HIRAGANA LETTER E 
    (0x24, 0x29): '〠',  # ten= 9  U+3049 HIRAGANA LETTER SMALL O 
    (0x24, 0x2A): '☎',  # ten=10  U+304A HIRAGANA LETTER O 
    (0x24, 0x2B): '',  # ten=11  U+304B HIRAGANA LETTER KA 
    (0x24, 0x2C): '∫',  # ten=12  U+304C HIRAGANA LETTER GA 
    (0x24, 0x2D): '√',  # ten=13  U+304D HIRAGANA LETTER KI 
    (0x24, 0x2E): '',  # ten=14  U+304E HIRAGANA LETTER GI 
    (0x24, 0x2F): '',  # ten=15  U+304F HIRAGANA LETTER KU 
    (0x24, 0x30): '',  # ten=16  U+3050 HIRAGANA LETTER GU 
    (0x24, 0x31): '',  # ten=17  U+3051 HIRAGANA LETTER KE 
    (0x24, 0x32): '',  # ten=18  U+3052 HIRAGANA LETTER GE 
    (0x24, 0x33): '',  # ten=19  U+3053 HIRAGANA LETTER KO 
    (0x24, 0x34): '',  # ten=20  U+3054 HIRAGANA LETTER GO 
    (0x24, 0x35): '',  # ten=21  U+3055 HIRAGANA LETTER SA 
    (0x24, 0x36): '',  # ten=22  U+3056 HIRAGANA LETTER ZA 
    (0x24, 0x37): '',  # ten=23  U+3057 HIRAGANA LETTER SI 
    (0x24, 0x38): '',  # ten=24  U+3058 HIRAGANA LETTER ZI 
    (0x24, 0x39): '',  # ten=25  U+3059 HIRAGANA LETTER SU 
    (0x24, 0x3A): '',  # ten=26  U+305A HIRAGANA LETTER ZU 
    (0x24, 0x3B): '',  # ten=27  U+305B HIRAGANA LETTER SE 
    (0x24, 0x3C): '',  # ten=28  U+305C HIRAGANA LETTER ZE 
    (0x24, 0x3D): '',  # ten=29  U+305D HIRAGANA LETTER SO 
    (0x24, 0x3E): '',  # ten=30  U+305E HIRAGANA LETTER ZO 
    (0x24, 0x3F): '',  # ten=31  U+305F HIRAGANA LETTER TA 
    (0x24, 0x40): '',  # ten=32  U+3060 HIRAGANA LETTER DA 
    (0x24, 0x41): '',  # ten=33  U+3061 HIRAGANA LETTER TI 
    (0x24, 0x42): '',  # ten=34  U+3062 HIRAGANA LETTER DI 
    (0x24, 0x43): '',  # ten=35  U+3063 HIRAGANA LETTER SMALL TU 
    (0x24, 0x44): '',  # ten=36  U+3064 HIRAGANA LETTER TU 
    (0x24, 0x45): '',  # ten=37  U+3065 HIRAGANA LETTER DU 
    (0x24, 0x46): '',  # ten=38  U+3066 HIRAGANA LETTER TE 
    (0x24, 0x47): '',  # ten=39  U+3067 HIRAGANA LETTER DE 
    (0x24, 0x50): '０',  # ten=48  U+3070 HIRAGANA LETTER BA 
    (0x24, 0x51): '１',  # ten=49  U+3071 HIRAGANA LETTER PA 
    (0x24, 0x52): '２',  # ten=50  U+3072 HIRAGANA LETTER HI 
    (0x24, 0x53): '３',  # ten=51  U+3073 HIRAGANA LETTER BI 
    (0x24, 0x54): '４',  # ten=52  U+3074 HIRAGANA LETTER PI 
    (0x24, 0x55): '５',  # ten=53  U+3075 HIRAGANA LETTER HU 
    (0x24, 0x56): '６',  # ten=54  U+3076 HIRAGANA LETTER BU 
    (0x24, 0x57): '７',  # ten=55  U+3077 HIRAGANA LETTER PU 
    (0x24, 0x58): '８',  # ten=56  U+3078 HIRAGANA LETTER HE 
    (0x24, 0x59): '９',  # ten=57  U+3079 HIRAGANA LETTER BE 
    (0x24, 0x61): 'Ａ',  # ten=65  U+3081 HIRAGANA LETTER ME 
    (0x24, 0x62): 'Ｂ',  # ten=66  U+3082 HIRAGANA LETTER MO 
    (0x24, 0x63): 'Ｃ',  # ten=67  U+3083 HIRAGANA LETTER SMALL YA 
    (0x24, 0x64): 'Ｄ',  # ten=68  U+3084 HIRAGANA LETTER YA 
    (0x24, 0x65): 'Ｅ',  # ten=69  U+3085 HIRAGANA LETTER SMALL YU 
    (0x24, 0x66): 'Ｆ',  # ten=70  U+3086 HIRAGANA LETTER YU 
    (0x24, 0x67): 'Ｇ',  # ten=71  U+3087 HIRAGANA LETTER SMALL YO 
    (0x24, 0x68): 'Ｈ',  # ten=72  U+3088 HIRAGANA LETTER YO 
    (0x24, 0x69): 'Ｉ',  # ten=73  U+3089 HIRAGANA LETTER RA 
    (0x24, 0x6A): 'Ｊ',  # ten=74  U+308A HIRAGANA LETTER RI 
    (0x24, 0x6B): 'Ｌ',  # ten=75  U+308B HIRAGANA LETTER RU 
    (0x24, 0x6C): 'Ｍ',  # ten=76  U+308C HIRAGANA LETTER RE 
    (0x24, 0x6D): 'Ｎ',  # ten=77  U+308D HIRAGANA LETTER RO 
    (0x24, 0x6E): 'Ｏ',  # ten=78  U+308E HIRAGANA LETTER SMALL WA 
    (0x24, 0x6F): 'Ｐ',  # ten=79  U+308F HIRAGANA LETTER WA 
    (0x24, 0x70): 'Ｑ',  # ten=80  U+3090 HIRAGANA LETTER WI 
    (0x24, 0x71): 'Ｒ',  # ten=81  U+3091 HIRAGANA LETTER WE 
    (0x24, 0x72): 'Ｓ',  # ten=82  U+3092 HIRAGANA LETTER WO 
    (0x24, 0x73): 'Ｔ',  # ten=83  U+3093 HIRAGANA LETTER N 
    (0x24, 0x74): 'Ｕ',  # ten=84  U+3094 HIRAGANA LETTER VU (jis2004)
    (0x24, 0x75): 'Ｖ',  # ten=85  U+3095 HIRAGANA LETTER SMALL KA (jis2004)
    (0x24, 0x76): 'Ｗ',  # ten=86  U+3096 HIRAGANA LETTER SMALL KE (jis2004)
    (0x24, 0x77): 'Ｘ',  # ten=87  ERR(jis2004-multi) 正しい文字を入れてください
    (0x24, 0x78): 'Ｙ',  # ten=88  ERR(jis2004-multi) 正しい文字を入れてください
    (0x24, 0x79): 'Ｚ',  # ten=89  ERR(jis2004-multi) 正しい文字を入れてください
    (0x24, 0x7A): '',  # ten=90  ERR(jis2004-multi) 正しい文字を入れてください

    # ===== Row 5: カタカナ =====
    (0x25, 0x21): 'Ａ',  # ten= 1  U+30A1 KATAKANA LETTER SMALL A 
    (0x25, 0x22): 'Ｂ',  # ten= 2  U+30A2 KATAKANA LETTER A 
    (0x25, 0x23): 'Ｃ',  # ten= 3  U+30A3 KATAKANA LETTER SMALL I 
    (0x25, 0x24): 'Ｄ',  # ten= 4  U+30A4 KATAKANA LETTER I 
    (0x25, 0x25): 'Ｅ',  # ten= 5  U+30A5 KATAKANA LETTER SMALL U 
    (0x25, 0x26): 'Ｆ',  # ten= 6  U+30A6 KATAKANA LETTER U 
    (0x25, 0x27): 'Ｇ',  # ten= 7  U+30A7 KATAKANA LETTER SMALL E 
    (0x25, 0x28): 'Ｈ',  # ten= 8  U+30A8 KATAKANA LETTER E 
    (0x25, 0x29): 'Ｉ',  # ten= 9  U+30A9 KATAKANA LETTER SMALL O 
    (0x25, 0x2A): 'Ｊ',  # ten=10  U+30AA KATAKANA LETTER O 
    (0x25, 0x2B): 'Ｋ',  # ten=11  U+30AB KATAKANA LETTER KA 
    (0x25, 0x2C): 'Ｌ',  # ten=12  U+30AC KATAKANA LETTER GA 
    (0x25, 0x2D): 'Ｍ',  # ten=13  U+30AD KATAKANA LETTER KI 
    (0x25, 0x2E): 'Ｎ',  # ten=14  U+30AE KATAKANA LETTER GI 
    (0x25, 0x2F): 'Ｏ',  # ten=15  U+30AF KATAKANA LETTER KU 
    (0x25, 0x30): 'Ｐ',  # ten=16  U+30B0 KATAKANA LETTER GU 
    (0x25, 0x31): 'Ｑ',  # ten=17  U+30B1 KATAKANA LETTER KE 
    (0x25, 0x32): 'Ｒ',  # ten=18  U+30B2 KATAKANA LETTER GE 
    (0x25, 0x33): 'Ｓ',  # ten=19  U+30B3 KATAKANA LETTER KO 
    (0x25, 0x34): 'Ｔ',  # ten=20  U+30B4 KATAKANA LETTER GO 
    (0x25, 0x35): 'Ｕ',  # ten=21  U+30B5 KATAKANA LETTER SA 
    (0x25, 0x36): 'Ｖ',  # ten=22  U+30B6 KATAKANA LETTER ZA 
    (0x25, 0x37): 'Ｗ',  # ten=23  U+30B7 KATAKANA LETTER SI 
    (0x25, 0x38): 'Ｘ',  # ten=24  U+30B8 KATAKANA LETTER ZI 
    (0x25, 0x39): 'Ｙ',  # ten=25  U+30B9 KATAKANA LETTER SU 
    (0x25, 0x3A): 'Ｚ',  # ten=26  U+30BA KATAKANA LETTER ZU 
    (0x25, 0x41): 'ａ',  # ten=33  U+30C1 KATAKANA LETTER TI 
    (0x25, 0x42): 'ｂ',  # ten=34  U+30C2 KATAKANA LETTER DI 
    (0x25, 0x43): 'ｃ',  # ten=35  U+30C3 KATAKANA LETTER SMALL TU 
    (0x25, 0x44): 'ｄ',  # ten=36  U+30C4 KATAKANA LETTER TU 
    (0x25, 0x45): 'ｅ',  # ten=37  U+30C5 KATAKANA LETTER DU 
    (0x25, 0x46): 'ｆ',  # ten=38  U+30C6 KATAKANA LETTER TE 
    (0x25, 0x47): 'ｇ',  # ten=39  U+30C7 KATAKANA LETTER DE 
    (0x25, 0x48): 'ｈ',  # ten=40  U+30C8 KATAKANA LETTER TO 
    (0x25, 0x49): 'ｉ',  # ten=41  U+30C9 KATAKANA LETTER DO 
    (0x25, 0x4A): 'ｊ',  # ten=42  U+30CA KATAKANA LETTER NA 
    (0x25, 0x4B): 'ｋ',  # ten=43  U+30CB KATAKANA LETTER NI 
    (0x25, 0x4C): 'ｌ',  # ten=44  U+30CC KATAKANA LETTER NU 
    (0x25, 0x4D): 'ｍ',  # ten=45  U+30CD KATAKANA LETTER NE 
    (0x25, 0x4E): 'ｎ',  # ten=46  U+30CE KATAKANA LETTER NO 
    (0x25, 0x4F): 'ｏ',  # ten=47  U+30CF KATAKANA LETTER HA 
    (0x25, 0x50): 'ｐ',  # ten=48  U+30D0 KATAKANA LETTER BA 
    (0x25, 0x51): 'ｑ',  # ten=49  U+30D1 KATAKANA LETTER PA 
    (0x25, 0x52): 'ｒ',  # ten=50  U+30D2 KATAKANA LETTER HI 
    (0x25, 0x53): 'ｓ',  # ten=51  U+30D3 KATAKANA LETTER BI 
    (0x25, 0x54): 'ｔ',  # ten=52  U+30D4 KATAKANA LETTER PI 
    (0x25, 0x55): 'ｕ',  # ten=53  U+30D5 KATAKANA LETTER HU 
    (0x25, 0x56): 'ｖ',  # ten=54  U+30D6 KATAKANA LETTER BU 
    (0x25, 0x57): 'ｗ',  # ten=55  U+30D7 KATAKANA LETTER PU 
    (0x25, 0x58): 'ｘ',  # ten=56  U+30D8 KATAKANA LETTER HE 
    (0x25, 0x59): 'ｙ',  # ten=57  U+30D9 KATAKANA LETTER BE 
    (0x25, 0x5A): 'ｚ',  # ten=58  U+30DA KATAKANA LETTER PE 
    (0x25, 0x5F): '',  # ten=63  U+30DF KATAKANA LETTER MI 
    (0x25, 0x60): '',  # ten=64  U+30E0 KATAKANA LETTER MU 
    (0x25, 0x61): 'ぁ',  # ten=65  U+30E1 KATAKANA LETTER ME 
    (0x25, 0x62): 'あ',  # ten=66  U+30E2 KATAKANA LETTER MO 
    (0x25, 0x63): 'ぃ',  # ten=67  U+30E3 KATAKANA LETTER SMALL YA 
    (0x25, 0x64): 'い',  # ten=68  U+30E4 KATAKANA LETTER YA 
    (0x25, 0x65): 'ぅ',  # ten=69  U+30E5 KATAKANA LETTER SMALL YU 
    (0x25, 0x66): 'う',  # ten=70  U+30E6 KATAKANA LETTER YU 
    (0x25, 0x67): 'ぇ',  # ten=71  U+30E7 KATAKANA LETTER SMALL YO 
    (0x25, 0x68): 'え',  # ten=72  U+30E8 KATAKANA LETTER YO 
    (0x25, 0x69): 'ぉ',  # ten=73  U+30E9 KATAKANA LETTER RA 
    (0x25, 0x6A): 'お',  # ten=74  U+30EA KATAKANA LETTER RI 
    (0x25, 0x6B): 'か',  # ten=75  U+30EB KATAKANA LETTER RU 
    (0x25, 0x6C): 'が',  # ten=76  U+30EC KATAKANA LETTER RE 
    (0x25, 0x6D): 'き',  # ten=77  U+30ED KATAKANA LETTER RO 
    (0x25, 0x6E): 'ぎ',  # ten=78  U+30EE KATAKANA LETTER SMALL WA 
    (0x25, 0x6F): 'く',  # ten=79  U+30EF KATAKANA LETTER WA 
    (0x25, 0x70): 'ぐ',  # ten=80  U+30F0 KATAKANA LETTER WI 
    (0x25, 0x71): 'け',  # ten=81  U+30F1 KATAKANA LETTER WE 
    (0x25, 0x72): 'げ',  # ten=82  U+30F2 KATAKANA LETTER WO 
    (0x25, 0x73): 'こ',  # ten=83  U+30F3 KATAKANA LETTER N 
    (0x25, 0x74): 'ご',  # ten=84  U+30F4 KATAKANA LETTER VU 
    (0x25, 0x75): 'さ',  # ten=85  U+30F5 KATAKANA LETTER SMALL KA 
    (0x25, 0x76): 'ざ',  # ten=86  U+30F6 KATAKANA LETTER SMALL KE 
    (0x25, 0x77): 'し',  # ten=87  ERR(jis2004-multi) 正しい文字を入れてください
    (0x25, 0x78): 'じ',  # ten=88  ERR(jis2004-multi) 正しい文字を入れてください
    (0x25, 0x79): 'す',  # ten=89  ERR(jis2004-multi) 正しい文字を入れてください
    (0x25, 0x7A): 'ず',  # ten=90  ERR(jis2004-multi) 正しい文字を入れてください
    (0x25, 0x7B): 'せ',  # ten=91  ERR(jis2004-multi) 正しい文字を入れてください
    (0x25, 0x7C): 'ぜ',  # ten=92  ERR(jis2004-multi) 正しい文字を入れてください
    (0x25, 0x7D): 'そ',  # ten=93  ERR(jis2004-multi) 正しい文字を入れてください
    (0x25, 0x7E): 'ぞ',  # ten=94  ERR(jis2004-multi) 正しい文字を入れてください

    # ===== Row 6: ギリシャ文字 =====
    (0x26, 0x21): 'ぁ',  # ten= 1  U+0391 GREEK CAPITAL LETTER ALPHA 
    (0x26, 0x22): 'あ',  # ten= 2  U+0392 GREEK CAPITAL LETTER BETA 
    (0x26, 0x23): 'ぃ',  # ten= 3  U+0393 GREEK CAPITAL LETTER GAMMA 
    (0x26, 0x24): 'い',  # ten= 4  U+0394 GREEK CAPITAL LETTER DELTA 
    (0x26, 0x25): 'ぅ',  # ten= 5  U+0395 GREEK CAPITAL LETTER EPSILON 
    (0x26, 0x26): 'う',  # ten= 6  U+0396 GREEK CAPITAL LETTER ZETA 
    (0x26, 0x27): 'ぇ',  # ten= 7  U+0397 GREEK CAPITAL LETTER ETA 
    (0x26, 0x28): 'え',  # ten= 8  U+0398 GREEK CAPITAL LETTER THETA 
    (0x26, 0x29): 'ぉ',  # ten= 9  U+0399 GREEK CAPITAL LETTER IOTA 
    (0x26, 0x2A): 'お',  # ten=10  U+039A GREEK CAPITAL LETTER KAPPA 
    (0x26, 0x2B): 'か',  # ten=11  U+039B GREEK CAPITAL LETTER LAMDA 
    (0x26, 0x2C): 'が',  # ten=12  U+039C GREEK CAPITAL LETTER MU 
    (0x26, 0x2D): 'き',  # ten=13  U+039D GREEK CAPITAL LETTER NU 
    (0x26, 0x2E): 'ぎ',  # ten=14  U+039E GREEK CAPITAL LETTER XI 
    (0x26, 0x2F): 'く',  # ten=15  U+039F GREEK CAPITAL LETTER OMICRON 
    (0x26, 0x30): 'ぐ',  # ten=16  U+03A0 GREEK CAPITAL LETTER PI 
    (0x26, 0x31): 'け',  # ten=17  U+03A1 GREEK CAPITAL LETTER RHO 
    (0x26, 0x32): 'げ',  # ten=18  U+03A3 GREEK CAPITAL LETTER SIGMA 
    (0x26, 0x33): 'こ',  # ten=19  U+03A4 GREEK CAPITAL LETTER TAU 
    (0x26, 0x34): 'ご',  # ten=20  U+03A5 GREEK CAPITAL LETTER UPSILON 
    (0x26, 0x35): 'さ',  # ten=21  U+03A6 GREEK CAPITAL LETTER PHI 
    (0x26, 0x36): 'ざ',  # ten=22  U+03A7 GREEK CAPITAL LETTER CHI 
    (0x26, 0x37): 'し',  # ten=23  U+03A8 GREEK CAPITAL LETTER PSI 
    (0x26, 0x38): 'じ',  # ten=24  U+03A9 GREEK CAPITAL LETTER OMEGA 
    (0x26, 0x39): 'す',  # ten=25  U+2664 WHITE SPADE SUIT (jis2004)
    (0x26, 0x3A): 'ず',  # ten=26  U+2660 BLACK SPADE SUIT (jis2004)
    (0x26, 0x3B): 'せ',  # ten=27  U+2662 WHITE DIAMOND SUIT (jis2004)
    (0x26, 0x3C): 'ぜ',  # ten=28  U+2666 BLACK DIAMOND SUIT (jis2004)
    (0x26, 0x3D): 'そ',  # ten=29  U+2661 WHITE HEART SUIT (jis2004)
    (0x26, 0x3E): 'ぞ',  # ten=30  U+2665 BLACK HEART SUIT (jis2004)
    (0x26, 0x3F): 'た',  # ten=31  U+2667 WHITE CLUB SUIT (jis2004)
    (0x26, 0x40): 'だ',  # ten=32  U+2663 BLACK CLUB SUIT (jis2004)
    (0x26, 0x41): 'ち',  # ten=33  U+03B1 GREEK SMALL LETTER ALPHA 
    (0x26, 0x42): 'ぢ',  # ten=34  U+03B2 GREEK SMALL LETTER BETA 
    (0x26, 0x43): 'っ',  # ten=35  U+03B3 GREEK SMALL LETTER GAMMA 
    (0x26, 0x44): 'つ',  # ten=36  U+03B4 GREEK SMALL LETTER DELTA 
    (0x26, 0x45): 'づ',  # ten=37  U+03B5 GREEK SMALL LETTER EPSILON 
    (0x26, 0x46): 'て',  # ten=38  U+03B6 GREEK SMALL LETTER ZETA 
    (0x26, 0x47): 'で',  # ten=39  U+03B7 GREEK SMALL LETTER ETA 
    (0x26, 0x48): 'と',  # ten=40  U+03B8 GREEK SMALL LETTER THETA 
    (0x26, 0x49): 'ど',  # ten=41  U+03B9 GREEK SMALL LETTER IOTA 
    (0x26, 0x4A): 'な',  # ten=42  U+03BA GREEK SMALL LETTER KAPPA 
    (0x26, 0x4B): 'に',  # ten=43  U+03BB GREEK SMALL LETTER LAMDA 
    (0x26, 0x4C): 'ぬ',  # ten=44  U+03BC GREEK SMALL LETTER MU 
    (0x26, 0x4D): 'ね',  # ten=45  U+03BD GREEK SMALL LETTER NU 
    (0x26, 0x4E): 'の',  # ten=46  U+03BE GREEK SMALL LETTER XI 
    (0x26, 0x4F): 'は',  # ten=47  U+03BF GREEK SMALL LETTER OMICRON 
    (0x26, 0x50): 'ば',  # ten=48  U+03C0 GREEK SMALL LETTER PI 
    (0x26, 0x51): 'ぱ',  # ten=49  U+03C1 GREEK SMALL LETTER RHO 
    (0x26, 0x52): 'ひ',  # ten=50  U+03C3 GREEK SMALL LETTER SIGMA 
    (0x26, 0x53): 'び',  # ten=51  U+03C4 GREEK SMALL LETTER TAU 
    (0x26, 0x54): 'ぴ',  # ten=52  U+03C5 GREEK SMALL LETTER UPSILON 
    (0x26, 0x55): 'ふ',  # ten=53  U+03C6 GREEK SMALL LETTER PHI 
    (0x26, 0x56): 'ぶ',  # ten=54  U+03C7 GREEK SMALL LETTER CHI 
    (0x26, 0x57): 'ぷ',  # ten=55  U+03C8 GREEK SMALL LETTER PSI 
    (0x26, 0x58): 'へ',  # ten=56  U+03C9 GREEK SMALL LETTER OMEGA 
    (0x26, 0x59): 'べ',  # ten=57  U+03C2 GREEK SMALL LETTER FINAL SIGMA (jis2004)
    (0x26, 0x5A): 'ぺ',  # ten=58  U+24F5 DOUBLE CIRCLED DIGIT ONE (jis2004)
    (0x26, 0x5B): 'ほ',  # ten=59  U+24F6 DOUBLE CIRCLED DIGIT TWO (jis2004)
    (0x26, 0x5C): 'ぼ',  # ten=60  U+24F7 DOUBLE CIRCLED DIGIT THREE (jis2004)
    (0x26, 0x5D): 'ぽ',  # ten=61  U+24F8 DOUBLE CIRCLED DIGIT FOUR (jis2004)
    (0x26, 0x5E): 'ま',  # ten=62  U+24F9 DOUBLE CIRCLED DIGIT FIVE (jis2004)
    (0x26, 0x5F): 'み',  # ten=63  U+24FA DOUBLE CIRCLED DIGIT SIX (jis2004)
    (0x26, 0x60): 'む',  # ten=64  U+24FB DOUBLE CIRCLED DIGIT SEVEN (jis2004)
    (0x26, 0x61): 'め',  # ten=65  U+24FC DOUBLE CIRCLED DIGIT EIGHT (jis2004)
    (0x26, 0x62): 'も',  # ten=66  U+24FD DOUBLE CIRCLED DIGIT NINE (jis2004)
    (0x26, 0x63): 'ゃ',  # ten=67  U+24FE DOUBLE CIRCLED NUMBER TEN (jis2004)
    (0x26, 0x64): 'や',  # ten=68  U+2616 WHITE SHOGI PIECE (jis2004)
    (0x26, 0x65): 'ゅ',  # ten=69  U+2617 BLACK SHOGI PIECE (jis2004)
    (0x26, 0x66): 'ゆ',  # ten=70  U+3020 POSTAL MARK FACE (jis2004)
    (0x26, 0x67): 'ょ',  # ten=71  U+260E BLACK TELEPHONE (jis2004)
    (0x26, 0x68): 'よ',  # ten=72  U+2600 BLACK SUN WITH RAYS (jis2004)
    (0x26, 0x69): 'ら',  # ten=73  U+2601 CLOUD (jis2004)
    (0x26, 0x6A): 'り',  # ten=74  U+2602 UMBRELLA (jis2004)
    (0x26, 0x6B): 'る',  # ten=75  U+2603 SNOWMAN (jis2004)
    (0x26, 0x6C): 'れ',  # ten=76  U+2668 HOT SPRINGS (jis2004)
    (0x26, 0x6D): 'ろ',  # ten=77  U+25B1 WHITE PARALLELOGRAM (jis2004)
    (0x26, 0x6E): 'ゎ',  # ten=78  U+31F0 KATAKANA LETTER SMALL KU (jis2004)
    (0x26, 0x6F): 'わ',  # ten=79  U+31F1 KATAKANA LETTER SMALL SI (jis2004)
    (0x26, 0x70): 'ゐ',  # ten=80  U+31F2 KATAKANA LETTER SMALL SU (jis2004)
    (0x26, 0x71): 'ゑ',  # ten=81  U+31F3 KATAKANA LETTER SMALL TO (jis2004)
    (0x26, 0x72): 'を',  # ten=82  U+31F4 KATAKANA LETTER SMALL NU (jis2004)
    (0x26, 0x73): 'ん',  # ten=83  U+31F5 KATAKANA LETTER SMALL HA (jis2004)
    (0x26, 0x74): '',  # ten=84  U+31F6 KATAKANA LETTER SMALL HI (jis2004)
    (0x26, 0x75): '',  # ten=85  U+31F7 KATAKANA LETTER SMALL HU (jis2004)
    (0x26, 0x76): '',  # ten=86  U+31F8 KATAKANA LETTER SMALL HE (jis2004)
    (0x26, 0x77): '',  # ten=87  U+31F9 KATAKANA LETTER SMALL HO (jis2004)
    (0x26, 0x78): '',  # ten=88  ERR(jis2004-multi) 正しい文字を入れてください

    # ===== Row 7: キリル文字 =====
    (0x27, 0x21): 'め',  # ten= 1  U+0410 CYRILLIC CAPITAL LETTER A 
    (0x27, 0x22): 'も',  # ten= 2  U+0411 CYRILLIC CAPITAL LETTER BE 
    (0x27, 0x23): 'ゃ',  # ten= 3  U+0412 CYRILLIC CAPITAL LETTER VE 
    (0x27, 0x24): 'や',  # ten= 4  U+0413 CYRILLIC CAPITAL LETTER GHE 
    (0x27, 0x25): 'ゅ',  # ten= 5  U+0414 CYRILLIC CAPITAL LETTER DE 
    (0x27, 0x26): 'ゆ',  # ten= 6  U+0415 CYRILLIC CAPITAL LETTER IE 
    (0x27, 0x27): 'ょ',  # ten= 7  U+0401 CYRILLIC CAPITAL LETTER IO 
    (0x27, 0x28): 'よ',  # ten= 8  U+0416 CYRILLIC CAPITAL LETTER ZHE 
    (0x27, 0x29): 'ら',  # ten= 9  U+0417 CYRILLIC CAPITAL LETTER ZE 
    (0x27, 0x2A): 'り',  # ten=10  U+0418 CYRILLIC CAPITAL LETTER I 
    (0x27, 0x2B): 'る',  # ten=11  U+0419 CYRILLIC CAPITAL LETTER SHORT I 
    (0x27, 0x2C): 'れ',  # ten=12  U+041A CYRILLIC CAPITAL LETTER KA 
    (0x27, 0x2D): 'ろ',  # ten=13  U+041B CYRILLIC CAPITAL LETTER EL 
    (0x27, 0x2E): 'ゎ',  # ten=14  U+041C CYRILLIC CAPITAL LETTER EM 
    (0x27, 0x2F): 'わ',  # ten=15  U+041D CYRILLIC CAPITAL LETTER EN 
    (0x27, 0x30): 'ゐ',  # ten=16  U+041E CYRILLIC CAPITAL LETTER O 
    (0x27, 0x31): 'ゑ',  # ten=17  U+041F CYRILLIC CAPITAL LETTER PE 
    (0x27, 0x32): 'を',  # ten=18  U+0420 CYRILLIC CAPITAL LETTER ER 
    (0x27, 0x33): 'ん',  # ten=19  U+0421 CYRILLIC CAPITAL LETTER ES 
    (0x27, 0x34): '',  # ten=20  U+0422 CYRILLIC CAPITAL LETTER TE 
    (0x27, 0x35): '',  # ten=21  U+0423 CYRILLIC CAPITAL LETTER U 
    (0x27, 0x36): '',  # ten=22  U+0424 CYRILLIC CAPITAL LETTER EF 
    (0x27, 0x37): '',  # ten=23  U+0425 CYRILLIC CAPITAL LETTER HA 
    (0x27, 0x38): '',  # ten=24  U+0426 CYRILLIC CAPITAL LETTER TSE 
    (0x27, 0x3F): '',  # ten=31  U+042D CYRILLIC CAPITAL LETTER E 
    (0x27, 0x40): '',  # ten=32  U+042E CYRILLIC CAPITAL LETTER YU 
    (0x27, 0x41): 'ァ',  # ten=33  U+042F CYRILLIC CAPITAL LETTER YA 
    (0x27, 0x42): 'ア',  # ten=34  U+23BE DENTISTRY SYMBOL LIGHT VERTICAL AND (jis2004)
    (0x27, 0x43): 'ィ',  # ten=35  U+23BF DENTISTRY SYMBOL LIGHT VERTICAL AND (jis2004)
    (0x27, 0x44): 'イ',  # ten=36  U+23C0 DENTISTRY SYMBOL LIGHT VERTICAL WIT (jis2004)
    (0x27, 0x45): 'ゥ',  # ten=37  U+23C1 DENTISTRY SYMBOL LIGHT DOWN AND HOR (jis2004)
    (0x27, 0x46): 'ウ',  # ten=38  U+23C2 DENTISTRY SYMBOL LIGHT UP AND HORIZ (jis2004)
    (0x27, 0x47): 'ェ',  # ten=39  U+23C3 DENTISTRY SYMBOL LIGHT VERTICAL WIT (jis2004)
    (0x27, 0x48): 'エ',  # ten=40  U+23C4 DENTISTRY SYMBOL LIGHT DOWN AND HOR (jis2004)
    (0x27, 0x49): 'ォ',  # ten=41  U+23C5 DENTISTRY SYMBOL LIGHT UP AND HORIZ (jis2004)
    (0x27, 0x4A): 'オ',  # ten=42  U+23C6 DENTISTRY SYMBOL LIGHT VERTICAL AND (jis2004)
    (0x27, 0x4B): 'カ',  # ten=43  U+23C7 DENTISTRY SYMBOL LIGHT DOWN AND HOR (jis2004)
    (0x27, 0x4C): 'ガ',  # ten=44  U+23C8 DENTISTRY SYMBOL LIGHT UP AND HORIZ (jis2004)
    (0x27, 0x4D): 'キ',  # ten=45  U+23C9 DENTISTRY SYMBOL LIGHT DOWN AND HOR (jis2004)
    (0x27, 0x4E): 'ギ',  # ten=46  U+23CA DENTISTRY SYMBOL LIGHT UP AND HORIZ (jis2004)
    (0x27, 0x4F): 'ク',  # ten=47  U+23CB DENTISTRY SYMBOL LIGHT VERTICAL AND (jis2004)
    (0x27, 0x50): 'グ',  # ten=48  U+23CC DENTISTRY SYMBOL LIGHT VERTICAL AND (jis2004)
    (0x27, 0x51): 'ケ',  # ten=49  U+0430 CYRILLIC SMALL LETTER A 
    (0x27, 0x52): 'ゲ',  # ten=50  U+0431 CYRILLIC SMALL LETTER BE 
    (0x27, 0x53): 'コ',  # ten=51  U+0432 CYRILLIC SMALL LETTER VE 
    (0x27, 0x54): 'ゴ',  # ten=52  U+0433 CYRILLIC SMALL LETTER GHE 
    (0x27, 0x55): 'サ',  # ten=53  U+0434 CYRILLIC SMALL LETTER DE 
    (0x27, 0x56): 'ザ',  # ten=54  U+0435 CYRILLIC SMALL LETTER IE 
    (0x27, 0x57): 'シ',  # ten=55  U+0451 CYRILLIC SMALL LETTER IO 
    (0x27, 0x58): 'ジ',  # ten=56  U+0436 CYRILLIC SMALL LETTER ZHE 
    (0x27, 0x59): 'ス',  # ten=57  U+0437 CYRILLIC SMALL LETTER ZE 
    (0x27, 0x5A): 'ズ',  # ten=58  U+0438 CYRILLIC SMALL LETTER I 
    (0x27, 0x5B): 'セ',  # ten=59  U+0439 CYRILLIC SMALL LETTER SHORT I 
    (0x27, 0x5C): 'ゼ',  # ten=60  U+043A CYRILLIC SMALL LETTER KA 
    (0x27, 0x5D): 'ソ',  # ten=61  U+043B CYRILLIC SMALL LETTER EL 
    (0x27, 0x5E): 'ゾ',  # ten=62  U+043C CYRILLIC SMALL LETTER EM 
    (0x27, 0x5F): 'タ',  # ten=63  U+043D CYRILLIC SMALL LETTER EN 
    (0x27, 0x60): 'ダ',  # ten=64  U+043E CYRILLIC SMALL LETTER O 
    (0x27, 0x61): 'チ',  # ten=65  U+043F CYRILLIC SMALL LETTER PE 
    (0x27, 0x62): 'ヂ',  # ten=66  U+0440 CYRILLIC SMALL LETTER ER 
    (0x27, 0x63): 'ッ',  # ten=67  U+0441 CYRILLIC SMALL LETTER ES 
    (0x27, 0x64): 'ツ',  # ten=68  U+0442 CYRILLIC SMALL LETTER TE 
    (0x27, 0x65): 'ヅ',  # ten=69  U+0443 CYRILLIC SMALL LETTER U 
    (0x27, 0x66): 'テ',  # ten=70  U+0444 CYRILLIC SMALL LETTER EF 
    (0x27, 0x67): 'デ',  # ten=71  U+0445 CYRILLIC SMALL LETTER HA 
    (0x27, 0x68): 'ト',  # ten=72  U+0446 CYRILLIC SMALL LETTER TSE 
    (0x27, 0x69): 'ド',  # ten=73  U+0447 CYRILLIC SMALL LETTER CHE 
    (0x27, 0x6A): 'ナ',  # ten=74  U+0448 CYRILLIC SMALL LETTER SHA 
    (0x27, 0x6B): 'ニ',  # ten=75  U+0449 CYRILLIC SMALL LETTER SHCHA 
    (0x27, 0x6C): 'ヌ',  # ten=76  U+044A CYRILLIC SMALL LETTER HARD SIGN 
    (0x27, 0x6D): 'ネ',  # ten=77  U+044B CYRILLIC SMALL LETTER YERU 
    (0x27, 0x6E): 'ノ',  # ten=78  U+044C CYRILLIC SMALL LETTER SOFT SIGN 
    (0x27, 0x6F): 'ハ',  # ten=79  U+044D CYRILLIC SMALL LETTER E 
    (0x27, 0x70): 'バ',  # ten=80  U+044E CYRILLIC SMALL LETTER YU 
    (0x27, 0x71): 'パ',  # ten=81  U+044F CYRILLIC SMALL LETTER YA 
    (0x27, 0x72): 'ヒ',  # ten=82  U+30F7 KATAKANA LETTER VA (jis2004)
    (0x27, 0x73): 'ビ',  # ten=83  U+30F8 KATAKANA LETTER VI (jis2004)
    (0x27, 0x74): 'ピ',  # ten=84  U+30F9 KATAKANA LETTER VE (jis2004)
    (0x27, 0x75): 'フ',  # ten=85  U+30FA KATAKANA LETTER VO (jis2004)
    (0x27, 0x76): 'ブ',  # ten=86  U+22DA LESS-THAN EQUAL TO OR GREATER-THAN (jis2004)
    (0x27, 0x77): 'プ',  # ten=87  U+22DB GREATER-THAN EQUAL TO OR LESS-THAN (jis2004)
    (0x27, 0x78): 'ヘ',  # ten=88  U+2153 VULGAR FRACTION ONE THIRD (jis2004)
    (0x27, 0x79): 'ベ',  # ten=89  U+2154 VULGAR FRACTION TWO THIRDS (jis2004)
    (0x27, 0x7A): 'ペ',  # ten=90  U+2155 VULGAR FRACTION ONE FIFTH (jis2004)
    (0x27, 0x7B): 'ホ',  # ten=91  U+2713 CHECK MARK (jis2004)
    (0x27, 0x7C): 'ボ',  # ten=92  U+2318 PLACE OF INTEREST SIGN (jis2004)
    (0x27, 0x7D): 'ポ',  # ten=93  U+2423 OPEN BOX (jis2004)
    (0x27, 0x7E): 'マ',  # ten=94  U+23CE RETURN SYMBOL (jis2004)

    # ===== Row 8: その他 =====
    (0x28, 0x21): 'チ',  # ten= 1  U+2500 BOX DRAWINGS LIGHT HORIZONTAL 
    (0x28, 0x22): 'ヂ',  # ten= 2  U+2502 BOX DRAWINGS LIGHT VERTICAL 
    (0x28, 0x23): 'ッ',  # ten= 3  U+250C BOX DRAWINGS LIGHT DOWN AND RIGHT 
    (0x28, 0x24): 'ツ',  # ten= 4  U+2510 BOX DRAWINGS LIGHT DOWN AND LEFT 
    (0x28, 0x25): 'ヅ',  # ten= 5  U+2518 BOX DRAWINGS LIGHT UP AND LEFT 
    (0x28, 0x26): 'テ',  # ten= 6  U+2514 BOX DRAWINGS LIGHT UP AND RIGHT 
    (0x28, 0x27): 'デ',  # ten= 7  U+251C BOX DRAWINGS LIGHT VERTICAL AND RIG 
    (0x28, 0x28): 'ト',  # ten= 8  U+252C BOX DRAWINGS LIGHT DOWN AND HORIZON 
    (0x28, 0x29): 'ド',  # ten= 9  U+2524 BOX DRAWINGS LIGHT VERTICAL AND LEF 
    (0x28, 0x2A): 'ナ',  # ten=10  U+2534 BOX DRAWINGS LIGHT UP AND HORIZONTA 
    (0x28, 0x2B): 'ニ',  # ten=11  U+253C BOX DRAWINGS LIGHT VERTICAL AND HOR 
    (0x28, 0x2C): 'ヌ',  # ten=12  U+2501 BOX DRAWINGS HEAVY HORIZONTAL 
    (0x28, 0x2D): 'ネ',  # ten=13  U+2503 BOX DRAWINGS HEAVY VERTICAL 
    (0x28, 0x2E): 'ノ',  # ten=14  U+250F BOX DRAWINGS HEAVY DOWN AND RIGHT 
    (0x28, 0x2F): 'ハ',  # ten=15  U+2513 BOX DRAWINGS HEAVY DOWN AND LEFT 
    (0x28, 0x30): 'バ',  # ten=16  U+251B BOX DRAWINGS HEAVY UP AND LEFT 
    (0x28, 0x31): 'パ',  # ten=17  U+2517 BOX DRAWINGS HEAVY UP AND RIGHT 
    (0x28, 0x32): 'ヒ',  # ten=18  U+2523 BOX DRAWINGS HEAVY VERTICAL AND RIG 
    (0x28, 0x33): 'ビ',  # ten=19  U+2533 BOX DRAWINGS HEAVY DOWN AND HORIZON 
    (0x28, 0x34): 'ピ',  # ten=20  U+252B BOX DRAWINGS HEAVY VERTICAL AND LEF 
    (0x28, 0x35): 'フ',  # ten=21  U+253B BOX DRAWINGS HEAVY UP AND HORIZONTA 
    (0x28, 0x36): 'ブ',  # ten=22  U+254B BOX DRAWINGS HEAVY VERTICAL AND HOR 
    (0x28, 0x37): 'プ',  # ten=23  U+2520 BOX DRAWINGS VERTICAL HEAVY AND RIG 
    (0x28, 0x38): 'ヘ',  # ten=24  U+252F BOX DRAWINGS DOWN LIGHT AND HORIZON 
    (0x28, 0x39): 'ベ',  # ten=25  U+2528 BOX DRAWINGS VERTICAL HEAVY AND LEF 
    (0x28, 0x3A): 'ペ',  # ten=26  U+2537 BOX DRAWINGS UP LIGHT AND HORIZONTA 
    (0x28, 0x3B): 'ホ',  # ten=27  U+253F BOX DRAWINGS VERTICAL LIGHT AND HOR 
    (0x28, 0x3C): 'ボ',  # ten=28  U+251D BOX DRAWINGS VERTICAL LIGHT AND RIG 
    (0x28, 0x3D): 'ポ',  # ten=29  U+2530 BOX DRAWINGS DOWN HEAVY AND HORIZON 
    (0x28, 0x3E): 'マ',  # ten=30  U+2525 BOX DRAWINGS VERTICAL LIGHT AND LEF 
    (0x28, 0x3F): 'ミ',  # ten=31  U+2538 BOX DRAWINGS UP HEAVY AND HORIZONTA 
    (0x28, 0x40): 'ム',  # ten=32  U+2542 BOX DRAWINGS VERTICAL HEAVY AND HOR 
    (0x28, 0x41): 'メ',  # ten=33  U+3251 CIRCLED NUMBER TWENTY ONE (jis2004)
    (0x28, 0x42): 'モ',  # ten=34  U+3252 CIRCLED NUMBER TWENTY TWO (jis2004)
    (0x28, 0x43): 'ャ',  # ten=35  U+3253 CIRCLED NUMBER TWENTY THREE (jis2004)
    (0x28, 0x44): 'ヤ',  # ten=36  U+3254 CIRCLED NUMBER TWENTY FOUR (jis2004)
    (0x28, 0x45): 'ュ',  # ten=37  U+3255 CIRCLED NUMBER TWENTY FIVE (jis2004)
    (0x28, 0x46): 'ユ',  # ten=38  U+3256 CIRCLED NUMBER TWENTY SIX (jis2004)
    (0x28, 0x47): 'ョ',  # ten=39  U+3257 CIRCLED NUMBER TWENTY SEVEN (jis2004)
    (0x28, 0x48): 'ヨ',  # ten=40  U+3258 CIRCLED NUMBER TWENTY EIGHT (jis2004)
    (0x28, 0x49): 'ラ',  # ten=41  U+3259 CIRCLED NUMBER TWENTY NINE (jis2004)
    (0x28, 0x4A): 'リ',  # ten=42  U+325A CIRCLED NUMBER THIRTY (jis2004)
    (0x28, 0x4B): 'ル',  # ten=43  U+325B CIRCLED NUMBER THIRTY ONE (jis2004)
    (0x28, 0x4C): 'レ',  # ten=44  U+325C CIRCLED NUMBER THIRTY TWO (jis2004)
    (0x28, 0x4D): 'ロ',  # ten=45  U+325D CIRCLED NUMBER THIRTY THREE (jis2004)
    (0x28, 0x4E): 'ヮ',  # ten=46  U+325E CIRCLED NUMBER THIRTY FOUR (jis2004)
    (0x28, 0x4F): 'ワ',  # ten=47  U+325F CIRCLED NUMBER THIRTY FIVE (jis2004)
    (0x28, 0x50): 'ヰ',  # ten=48  U+32B1 CIRCLED NUMBER THIRTY SIX (jis2004)
    (0x28, 0x51): 'ヱ',  # ten=49  U+32B2 CIRCLED NUMBER THIRTY SEVEN (jis2004)
    (0x28, 0x52): 'ヲ',  # ten=50  U+32B3 CIRCLED NUMBER THIRTY EIGHT (jis2004)
    (0x28, 0x53): 'ン',  # ten=51  U+32B4 CIRCLED NUMBER THIRTY NINE (jis2004)
    (0x28, 0x54): 'ヴ',  # ten=52  U+32B5 CIRCLED NUMBER FORTY (jis2004)
    (0x28, 0x55): 'ヵ',  # ten=53  U+32B6 CIRCLED NUMBER FORTY ONE (jis2004)
    (0x28, 0x56): 'ヶ',  # ten=54  U+32B7 CIRCLED NUMBER FORTY TWO (jis2004)
    (0x28, 0x5F): '',  # ten=63  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x60): '',  # ten=64  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x61): 'Α',  # ten=65  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x62): 'Β',  # ten=66  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x63): 'Γ',  # ten=67  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x64): 'Δ',  # ten=68  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x65): 'Ε',  # ten=69  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x66): 'Ζ',  # ten=70  ERR(ERR) 正しい文字を入れてください
    (0x28, 0x67): 'Η',  # ten=71  U+25D0 CIRCLE WITH LEFT HALF BLACK (jis2004)
    (0x28, 0x68): 'Θ',  # ten=72  U+25D1 CIRCLE WITH RIGHT HALF BLACK (jis2004)
    (0x28, 0x69): 'Ι',  # ten=73  U+25D2 CIRCLE WITH LOWER HALF BLACK (jis2004)
    (0x28, 0x6A): 'Κ',  # ten=74  U+25D3 CIRCLE WITH UPPER HALF BLACK (jis2004)
    (0x28, 0x6B): 'Λ',  # ten=75  U+203C DOUBLE EXCLAMATION MARK (jis2004)
    (0x28, 0x6C): 'Μ',  # ten=76  U+2047 DOUBLE QUESTION MARK (jis2004)
    (0x28, 0x6D): 'Ν',  # ten=77  U+2048 QUESTION EXCLAMATION MARK (jis2004)
    (0x28, 0x6E): 'Ξ',  # ten=78  U+2049 EXCLAMATION QUESTION MARK (jis2004)
    (0x28, 0x6F): 'Ο',  # ten=79  U+01CD LATIN CAPITAL LETTER A WITH CARON (jis2004)
    (0x28, 0x70): 'Π',  # ten=80  U+01CE LATIN SMALL LETTER A WITH CARON (jis2004)
    (0x28, 0x71): 'Ρ',  # ten=81  U+01D0 LATIN SMALL LETTER I WITH CARON (jis2004)
    (0x28, 0x72): 'Σ',  # ten=82  U+1E3E LATIN CAPITAL LETTER M WITH ACUTE (jis2004)
    (0x28, 0x73): 'Τ',  # ten=83  U+1E3F LATIN SMALL LETTER M WITH ACUTE (jis2004)
    (0x28, 0x74): 'Υ',  # ten=84  U+01F8 LATIN CAPITAL LETTER N WITH GRAVE (jis2004)
    (0x28, 0x75): 'Φ',  # ten=85  U+01F9 LATIN SMALL LETTER N WITH GRAVE (jis2004)
    (0x28, 0x76): 'Χ',  # ten=86  U+01D1 LATIN CAPITAL LETTER O WITH CARON (jis2004)
    (0x28, 0x77): 'Ψ',  # ten=87  U+01D2 LATIN SMALL LETTER O WITH CARON (jis2004)
    (0x28, 0x78): 'Ω',  # ten=88  U+01D4 LATIN SMALL LETTER U WITH CARON (jis2004)

    # ===== 境界文字 (jis2=0x20, 0x7F) 各行先頭・末尾 - /tmp/msx_supplement.png 参照 =====
    (0x21, 0x20): '',  # Row1 jis2=0x20 [要確認]
    (0x21, 0x7F): '×',  # Row1 jis2=0x7F [要確認]
    (0x22, 0x20): '＼',  # Row2 jis2=0x20 [要確認]
    (0x22, 0x7F): '㎞',  # Row2 jis2=0x7F [要確認]
    (0x23, 0x20): '',  # Row3 jis2=0x20 [要確認]
    (0x23, 0x7F): '',  # Row3 jis2=0x7F [要確認]
    (0x24, 0x20): '④',  # Row4 jis2=0x20 [要確認]
    (0x25, 0x7F): 'た',  # Row5 jis2=0x7F [要確認]
    (0x26, 0x20): '',  # Row6 jis2=0x20 [要確認]
    (0x26, 0x7F): '＋',  # Row6 jis2=0x7F [要確認]
    (0x27, 0x20): 'む',  # Row7 jis2=0x20 [要確認]
    (0x27, 0x7F): 'ミ',  # Row7 jis2=0x7F [要確認]
    (0x28, 0x20): 'ダ',  # Row8 jis2=0x20 [要確認]

    # ===== Row 9: ギリシャ文字 (jis1=0x29) - /tmp/msx_supplement.png 参照 =====
    (0x29, 0x20): '',  # GREEK CAPITAL LETTER ALPHA
    (0x29, 0x21): 'Α',  # GREEK CAPITAL LETTER BETA
    (0x29, 0x22): 'Β',  # GREEK CAPITAL LETTER GAMMA
    (0x29, 0x23): 'Γ',  # GREEK CAPITAL LETTER DELTA
    (0x29, 0x24): 'Δ',  # GREEK CAPITAL LETTER EPSILON
    (0x29, 0x25): 'Ε',  # GREEK CAPITAL LETTER ZETA
    (0x29, 0x26): 'Ζ',  # GREEK CAPITAL LETTER ETA
    (0x29, 0x27): 'Η',  # GREEK CAPITAL LETTER THETA
    (0x29, 0x28): 'Θ',  # GREEK CAPITAL LETTER IOTA
    (0x29, 0x29): 'Ι',  # GREEK CAPITAL LETTER KAPPA
    (0x29, 0x2A): 'Κ',  # GREEK CAPITAL LETTER LAMDA
    (0x29, 0x2B): 'Λ',  # GREEK CAPITAL LETTER MU
    (0x29, 0x2C): 'Μ',  # GREEK CAPITAL LETTER NU
    (0x29, 0x2D): 'Ν',  # GREEK CAPITAL LETTER XI
    (0x29, 0x2E): 'Ξ',  # GREEK CAPITAL LETTER OMICRON
    (0x29, 0x2F): 'Ο',  # GREEK CAPITAL LETTER PI
    (0x29, 0x30): 'Π',  # GREEK CAPITAL LETTER RHO
    (0x29, 0x31): 'Ρ',  # GREEK CAPITAL LETTER SIGMA
    (0x29, 0x32): 'Σ',  # GREEK CAPITAL LETTER TAU
    (0x29, 0x33): 'Τ',  # GREEK CAPITAL LETTER UPSILON
    (0x29, 0x34): 'Υ',  # GREEK CAPITAL LETTER PHI
    (0x29, 0x35): 'Φ',  # GREEK CAPITAL LETTER CHI
    (0x29, 0x36): 'Χ',  # GREEK CAPITAL LETTER PSI
    (0x29, 0x37): 'Ψ',  # GREEK CAPITAL LETTER OMEGA
    (0x29, 0x38): 'Ω',   # [要確認] (ς GREEK SMALL LETTER FINAL SIGMA?)
    (0x29, 0x40): '',  # GREEK SMALL LETTER ALPHA
    (0x29, 0x41): 'α',  # GREEK SMALL LETTER BETA
    (0x29, 0x42): 'β',  # GREEK SMALL LETTER GAMMA
    (0x29, 0x43): 'γ',  # GREEK SMALL LETTER DELTA
    (0x29, 0x44): 'δ',  # GREEK SMALL LETTER EPSILON
    (0x29, 0x45): 'ε',  # GREEK SMALL LETTER ZETA
    (0x29, 0x46): 'ζ',  # GREEK SMALL LETTER ETA
    (0x29, 0x47): 'η',  # GREEK SMALL LETTER THETA
    (0x29, 0x48): 'θ',  # GREEK SMALL LETTER IOTA
    (0x29, 0x49): 'ι',  # GREEK SMALL LETTER KAPPA
    (0x29, 0x4A): 'κ',  # GREEK SMALL LETTER LAMDA
    (0x29, 0x4B): 'λ',  # GREEK SMALL LETTER MU
    (0x29, 0x4C): 'μ',  # GREEK SMALL LETTER NU
    (0x29, 0x4D): 'ν',  # GREEK SMALL LETTER XI
    (0x29, 0x4E): 'ξ',  # GREEK SMALL LETTER OMICRON
    (0x29, 0x4F): 'ο',  # GREEK SMALL LETTER PI
    (0x29, 0x50): 'π',  # GREEK SMALL LETTER RHO
    (0x29, 0x51): 'ρ',  # GREEK SMALL LETTER SIGMA
    (0x29, 0x52): 'σ',  # GREEK SMALL LETTER TAU
    (0x29, 0x53): 'τ',  # GREEK SMALL LETTER UPSILON
    (0x29, 0x54): 'υ',  # GREEK SMALL LETTER PHI
    (0x29, 0x55): 'φ',  # GREEK SMALL LETTER CHI
    (0x29, 0x56): 'χ',  # GREEK SMALL LETTER PSI
    (0x29, 0x57): 'ψ',  # GREEK SMALL LETTER OMEGA
    (0x29, 0x58): 'ω',   # [要確認]
    (0x29, 0x5F): '',   # [要確認] (▼ BLACK DOWN-POINTING TRIANGLE?)
    (0x29, 0x7F): '',   # [要確認]

    # ===== Row 10: キリル文字 (jis1=0x2A) - /tmp/msx_supplement.png 参照 =====
    (0x2A, 0x3F): '',   # [要確認] (← ?)
    (0x2A, 0x40): '',   # [要確認] (↑ ?)
    (0x2A, 0x41): 'А',  # CYRILLIC CAPITAL LETTER A
    (0x2A, 0x42): 'Б',  # CYRILLIC CAPITAL LETTER BE
    (0x2A, 0x43): 'В',  # CYRILLIC CAPITAL LETTER VE
    (0x2A, 0x44): 'Г',  # CYRILLIC CAPITAL LETTER GHE
    (0x2A, 0x45): 'Д',  # CYRILLIC CAPITAL LETTER DE
    (0x2A, 0x46): 'Е',  # CYRILLIC CAPITAL LETTER IE
    (0x2A, 0x47): 'Ё',  # CYRILLIC CAPITAL LETTER IO
    (0x2A, 0x48): 'Ж',  # CYRILLIC CAPITAL LETTER ZHE
    (0x2A, 0x49): 'З',  # CYRILLIC CAPITAL LETTER ZE
    (0x2A, 0x4A): 'И',  # CYRILLIC CAPITAL LETTER I
    (0x2A, 0x4B): 'Й',  # CYRILLIC CAPITAL LETTER SHORT I
    (0x2A, 0x4C): 'К',  # CYRILLIC CAPITAL LETTER KA
    (0x2A, 0x4D): 'Л',  # CYRILLIC CAPITAL LETTER EL
    (0x2A, 0x4E): 'М',  # CYRILLIC CAPITAL LETTER EM
    (0x2A, 0x4F): 'Н',  # CYRILLIC CAPITAL LETTER EN
    (0x2A, 0x50): 'О',  # CYRILLIC CAPITAL LETTER O
    (0x2A, 0x51): 'П',  # CYRILLIC CAPITAL LETTER PE
    (0x2A, 0x52): 'Р',  # CYRILLIC CAPITAL LETTER ER
    (0x2A, 0x53): 'С',  # CYRILLIC CAPITAL LETTER ES
    (0x2A, 0x54): 'Т',  # CYRILLIC CAPITAL LETTER TE
    (0x2A, 0x55): 'У',  # CYRILLIC CAPITAL LETTER U
    (0x2A, 0x56): 'Ф',  # CYRILLIC CAPITAL LETTER EF
    (0x2A, 0x57): 'Х',  # CYRILLIC CAPITAL LETTER HA
    (0x2A, 0x58): 'Ц',  # CYRILLIC CAPITAL LETTER TSE
    (0x2A, 0x59): 'Ч',  # CYRILLIC CAPITAL LETTER CHE
    (0x2A, 0x5A): 'Ш',  # CYRILLIC CAPITAL LETTER SHA
    (0x2A, 0x5B): 'Щ',  # CYRILLIC CAPITAL LETTER SHCHA
    (0x2A, 0x5C): 'Ъ',  # CYRILLIC CAPITAL LETTER HARD SIGN
    (0x2A, 0x5D): 'Ы',  # CYRILLIC CAPITAL LETTER YERU
    (0x2A, 0x5E): 'Ь',  # CYRILLIC CAPITAL LETTER SOFT SIGN
    (0x2A, 0x5F): 'Э',  # CYRILLIC CAPITAL LETTER E
    (0x2A, 0x60): 'Ю',  # CYRILLIC CAPITAL LETTER YU
    (0x2A, 0x61): 'Я',  # CYRILLIC CAPITAL LETTER YA
    (0x2A, 0x71): 'а',  # CYRILLIC SMALL LETTER A
    (0x2A, 0x72): 'б',  # CYRILLIC SMALL LETTER BE
    (0x2A, 0x73): 'в',  # CYRILLIC SMALL LETTER VE
    (0x2A, 0x74): 'г',  # CYRILLIC SMALL LETTER GHE
    (0x2A, 0x75): 'д',  # CYRILLIC SMALL LETTER DE
    (0x2A, 0x76): 'е',  # CYRILLIC SMALL LETTER IE
    (0x2A, 0x77): 'ё',  # CYRILLIC SMALL LETTER IO
    (0x2A, 0x78): 'ж',  # CYRILLIC SMALL LETTER ZHE
    (0x2A, 0x79): 'з',  # CYRILLIC SMALL LETTER ZE
    (0x2A, 0x7A): 'и',  # CYRILLIC SMALL LETTER I
    (0x2A, 0x7B): 'й',  # CYRILLIC SMALL LETTER SHORT I
    (0x2A, 0x7C): 'к',  # CYRILLIC SMALL LETTER KA
    (0x2A, 0x7D): 'л',  # CYRILLIC SMALL LETTER EL
    (0x2A, 0x7E): 'м',  # CYRILLIC SMALL LETTER EM
    (0x2A, 0x7F): 'н',  # CYRILLIC SMALL LETTER EN
}

# ===== ANK 低域 0x01-0x1F + 拡張 0x80-0x9F (JAPANESE.FNT): 半角拡張文字 =====
# 確認画像: /tmp/msx_supplement.png (ANK 0x00-0x1F セクション)
ANK_EXT_OVERRIDES = {
    # ANK 0x01-0x0F: 日本語カレンダー/単位記号（標準MSX）
    0x01: '月',  # Monday / month kanji
    0x02: '火',  # Tuesday / fire kanji
    0x03: '水',  # Wednesday / water kanji
    0x04: '木',  # Thursday / wood kanji
    0x05: '金',  # Friday / gold kanji
    0x06: '土',  # Saturday / earth kanji
    0x07: '日',  # Sunday / day kanji
    0x08: '年',  # year
    0x09: '円',  # yen
    0x0A: '時',  # hour
    0x0B: '分',  # minute
    0x0C: '秒',  # second
    0x0D: '百',  # hundred
    0x0E: '千',  # thousand
    0x0F: '万',  # ten-thousand
    # ANK 0x10-0x1F: 要視覚確認 (/tmp/msx_supplement.png)
    0x10: 'π',  # ANK code=0x10 [要確認]
    0x11: '┴',  # ANK code=0x11 [要確認]
    0x12: '┬',  # ANK code=0x12 [要確認]
    0x13: '┤',  # ANK code=0x13 [要確認]
    0x14: '├',  # ANK code=0x14 [要確認]
    0x15: '┼',  # ANK code=0x15 [要確認]
    0x16: '│',  # ANK code=0x16 [要確認]
    0x17: '─',  # ANK code=0x17 [要確認]
    0x18: '┌',  # ANK code=0x18 [要確認]
    0x19: '┐',  # ANK code=0x19 [要確認]
    0x1A: '└',  # ANK code=0x1A [要確認]
    0x1B: '┘',  # ANK code=0x1B [要確認]
    0x1C: '×',  # ANK code=0x1C [要確認]
    0x1D: '大',  # ANK code=0x1D [要確認]
    0x1E: '中',  # ANK code=0x1E [要確認]
    0x1F: '小',  # ANK code=0x1F [要確認]
    # ANK 0x80-0x9F: 拡張文字
    0x80: '',  # ANK code=0x80
    0x81: '',  # ANK code=0x81
    0x82: '',  # ANK code=0x82
    0x83: '',  # ANK code=0x83
    0x84: '',  # ANK code=0x84
    0x85: '',  # ANK code=0x85
    0x86: '',  # ANK code=0x86
    0x87: '',  # ANK code=0x87
    0x88: '',  # ANK code=0x88
    0x89: '',  # ANK code=0x89
    0x8A: '',  # ANK code=0x8A
    0x8B: '',  # ANK code=0x8B
    0x8C: '',  # ANK code=0x8C
    0x8D: '',  # ANK code=0x8D
    0x8E: '',  # ANK code=0x8E
    0x8F: '',  # ANK code=0x8F
    0x91: '',  # ANK code=0x91
    0x92: '',  # ANK code=0x92
    0x93: '',  # ANK code=0x93
    0x94: '',  # ANK code=0x94
    0x95: '',  # ANK code=0x95
    0x96: '',  # ANK code=0x96
    0x97: '',  # ANK code=0x97
    0x98: '',  # ANK code=0x98
    0x99: '',  # ANK code=0x99
    0x9A: '',  # ANK code=0x9A
    0x9B: '',  # ANK code=0x9B
    0x9C: '',  # ANK code=0x9C
    0x9D: '',  # ANK code=0x9D
    0x9E: '',  # ANK code=0x9E
    0x9F: '',  # ANK code=0x9F
}
