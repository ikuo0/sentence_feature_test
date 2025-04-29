"""

区切り統一（Punctuation unification）

文頭・文末マーク付加（Boundary marking）


# 文字の正規化（Normalization）
## **全角化（Zenkaku normalization）**  
文字幅を揃えて、データのばらつきを防ぐ。

## **連続空白を1つに正規化（Whitespace normalization）**  
半角/全角の連続スペースやタブを1個の普通の空白にする。

## **連続改行を1つに正規化（Newline normalization）**  
→ 複数改行を1つの改行にまとめ、文区切りを安定させる。

# 記号統一
## 区切り記号の統一（Punctuation normalization）**  
「、」「，」「。」「．」「\r\n」などを、すべて「．」に統一。

## 括弧記号の統一（Parentheses normalization）
「（」「〔」「【」「《」などの開き括弧を「（」に統一し、「）」「〕」「】」「》」などの閉じ括弧を「）」に統一する。  
異なる種類の括弧が混在すると、同じ意味の文構造であっても異なるベクトル特徴になってしまうため、統一することで解析の一貫性を保つ。

## 伸ばし棒の統一（Long vowel normalization）**  
半角ハイフン・長音符（例：「－」「ー」）を「ー」に統一する。

# 文末の記号を付与
## 文頭の区切りを作成する
文末を $ とする
区切り記号（．）、改行が文末となる
文頭記号は無い、文末の次が文頭となるため改めて記号を設定する必要が無い

"""

import unicodedata
import re
from typing import List

class WidthNormalizer:
    @classmethod
    def standardize_full_width(cls, text) -> str:
        full_width_chars = []
        col_count = 1
        line_no = 1
        for i, c in enumerate(text):
            try:
                normalized = unicodedata.normalize('NFKC', c)
                if len(normalized) != 1: # ３点リーダー等が複数文字にされてしまう
                    normalized = "？"
                elif normalized == " ":
                    # 半角スペースは全角スペースに変換
                    normalized = "　"
                elif '!' <= normalized <= '~':
                    # ASCII範囲なら全角対応を手動で追加
                    normalized = chr(ord(normalized) + 0xFEE0)
                full_width_chars.append(normalized)
            except Exception as e:
                print(f"Error normalizing character {c}: {e} in {line_no}. {col_count}")
                full_width_chars.append("？")
            col_count += 1
            if c == "\n":
                col_count = 1
                line_no += 1
        return ''.join(full_width_chars)


    @classmethod
    def make_full_width_alphabet_upper_case(cls, text: str) -> str:
        """
        全角文字列のａ～ｚをＡ～Ｚに変換する
        """
        normalized = []
        for c in text:
            code = ord(c)
            if 0xFF41 <= code <= 0xFF5A:
                normalized.append(chr(code - 0x20))
            else:
                normalized.append(c)
        return "".join(normalized)


    @classmethod
    def make_full_width_number_zero(cls, text: str) -> str:
        """
        全角数字０～９を全て０に変換する
        """
        normalized = []
        for c in text:
            code = ord(c)
            if 0xFF10 <= code <= 0xFF19:
                normalized.append(chr(0xFF10))
            else:
                normalized.append(c)
        return "".join(normalized)


    def standardize_crlf(text: str) -> str:
        """
        改行コードを統一する関数。
        Windows系の \r\n、古いMacの \r、Unix系の \n をすべて \n に統一する。
        """
        # まず \r\n を \n に置き換え
        text = text.replace('\r\n', '\n')
        # 次に単独の \r を \n に置き換え
        text = text.replace('\r', '\n')
        return text

    @classmethod
    def merge_repeated_chars(cls, text: str, targets: List[str], replace_with: str) -> str:
        """
        指定した文字（複数指定可）の連続を1個の指定文字にまとめる関数。

        Args:
            text (str): 対象の文字列
            targets (List[str]): まとめたい文字のリスト
            replace_with (str): まとめた後の1文字

        Returns:
            str: まとめた後の文字列
        """
        if not targets:
            return text

        # 正規表現パターン作成
        pattern = "[" + re.escape(''.join(targets)) + "]+"

        # 正規表現で置換
        return re.sub(pattern, replace_with, text)

    @classmethod
    def merge_duplicate_crlf(cls, text: str) -> str:
        """
        連続する改行を1つにまとめる関数。
        """
        return cls.merge_repeated_chars(text, ["\r", "\n"], "\n")

    @classmethod
    def merge_duplicate_space(cls, text: str) -> str:
        """
        連続する空白を1つにまとめる関数。
        """
        return cls.merge_repeated_chars(text, [" ", "　", "\t"], "　")

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        文字列を正規化する関数。
        """
        text = cls.standardize_full_width(text)
        text = cls.make_full_width_alphabet_upper_case(text)
        text = cls.make_full_width_number_zero(text)
        text = cls.standardize_crlf(text)
        text = cls.merge_duplicate_space(text)
        text = cls.merge_duplicate_crlf(text)
        return text


class SymbolNomalizer:
    """
    WidthNormalizer で全角変換等を適用後の文字列に対して記号統一を行う
    """
    @classmethod
    def normalize_punctuation(cls, text) -> str:
        # 句読点の統一
        punctutation = ["、", "。", "，"]
        unified_paren = "．"
        normalized_chars = []
        for c in text:
            if c in punctutation:
                normalized_chars.append(unified_paren)
            else:
                normalized_chars.append(c)
        return ''.join(normalized_chars)
        

    @classmethod
    def normalize_start_parentheses(cls, text: str) -> str:
        start_paren_variants = ["（", "〔", "【", "《", "〈", "『", "「", "｛", "＜", "《", "≪", "〖", "［", "”"]
        unified_paren = "（"
        normalized_chars = []
        for c in text:
            if c in start_paren_variants:
                normalized_chars.append(unified_paren)
            else:
                normalized_chars.append(c)
        return ''.join(normalized_chars)

    @classmethod
    def normalize_end_parentheses(cls, text: str) -> str:
        end_paren_variants = ["）", "〕", "】", "》", "〉", "』", "」", "｝", "＞", "》", "≫", "〗", "］", "“"]
        unified_paren = "）"
        normalized_chars = []
        for c in text:
            if c in end_paren_variants:
                normalized_chars.append(unified_paren)
            else:
                normalized_chars.append(c)
        return ''.join(normalized_chars)

    @classmethod
    def normalize_horizontal_bars(cls, text: str) -> str:
        """
        伸ばし棒のように見える横棒記号をすべて全角ハイフンマイナス（－）に統一する
        """
        targets = [
            '-',
            'ー',  # カタカナ長音符
            '−',  # マイナス記号
            '―',  # 水平線（ダッシュ）
            '‐',  # ハイフン
            'ｰ',  # 半角カタカナ長音符
            '–',  # エヌダッシュ
            '—',  # エムダッシュ
        ]
        for char in targets:
            text = text.replace(char, '－')
        return text

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        文字列を正規化する関数。
        """
        text = cls.normalize_punctuation(text)
        text = cls.normalize_start_parentheses(text)
        text = cls.normalize_end_parentheses(text)
        text = cls.normalize_horizontal_bars(text)
        return text


class MarkBoundary:
    @classmethod
    def trim_full_width_space(cls, text: str) -> str:
        """
        文頭文末の全角スペースの連続をトリミングする
        """
        text = text.strip()
        # 文頭文末の全角スペースをトリミング
        text = re.sub(r'^[　]+', '', text)
        text = re.sub(r'[　]+$', '', text)
        return text

    @classmethod
    def mark_end_of_sentence(cls, text: str) -> str:
        """
            "．" を $ に変換する
            \n を $ に変換する
        """
        text = text.strip()
        end_mark = ["．", "\n"]
        for mark in end_mark:
            text = text.replace(mark, "$")

        texts = text.split("$")
        texts_striped = []
        for text in texts:
            text = cls.trim_full_width_space(text)
            if len(text) < 1:
                continue
            texts_striped.append(text)

        result = "$" + "$".join(texts_striped) + "$"

        return result

    @classmethod
    def mark_boundary(cls, text: str) -> str:
        # 文末のマーク付加
        marked_text = cls.mark_end_of_sentence(text)
        # marked_text = cls.mark_start_of_sentence(marked_text)
        # $ の連続を１つにする
        marked_text = WidthNormalizer.merge_repeated_chars(marked_text, ["$"], "$")
        return marked_text


def normalize(text) -> str:
    """
    文字列を正規化する関数。
    """
    text = WidthNormalizer.normalize(text)
    text = SymbolNomalizer.normalize(text)
    text = MarkBoundary.mark_boundary(text)
    return text
