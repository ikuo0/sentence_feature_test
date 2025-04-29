
from word_boundary.preprocessing import normalize_text

class TestWidthNormalizer:
    def test_standardize_full_width(self):
        text = "abc"
        expected = "ａｂｃ"
        result = normalize_text.WidthNormalizer.standardize_full_width(text)
        assert result == expected

    def test_standardize_full_width_with_special_characters(self):
        text = "abc！＠＃＄％＾＆＊（）＿＋－＝"
        expected = "ａｂｃ！＠＃＄％＾＆＊（）＿＋－＝"
        result = normalize_text.WidthNormalizer.standardize_full_width(text)
        assert result == expected

    def test_make_full_width_alphabet_upper_case(self):
        text = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
        expected = "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
        result = normalize_text.WidthNormalizer.make_full_width_alphabet_upper_case(text)
        assert result == expected

    def test_make_full_width_number_zero(self):
        text = "０１２３４５６７８９"
        expected = "０" * len(text)
        result = normalize_text.WidthNormalizer.make_full_width_number_zero(text)
        assert result == expected

    def test_standardize_full_width_with_unicode(self):
        text = "abc!@# "
        expected = "ａｂｃ！＠＃　"
        result = normalize_text.WidthNormalizer.standardize_full_width(text)
        assert result == expected

    def test_standardize_crlf(self):
        text = "abc\r\n"
        expected = "abc\n"
        result = normalize_text.WidthNormalizer.standardize_crlf(text)
        assert result == expected

    def test_standardize_crlf_with_multiple_types(self):
        text = "abc\r\ndef\rghi\njkl"
        expected = "abc\ndef\nghi\njkl"
        result = normalize_text.WidthNormalizer.standardize_crlf(text)
        assert result == expected


class TestSymbolNormalizer:
    def test_normalize_punctuation(self):
        text = "abc、def。ghi"
        expected = "abc．def．ghi"
        result = normalize_text.SymbolNomalizer.normalize_punctuation(text)
        assert result == expected

    def test_normalize_start_parentheses(self):
        text = "abc（def〔ghi【jkl《mno"
        expected = "abc（def（ghi（jkl（mno"
        result = normalize_text.SymbolNomalizer.normalize_start_parentheses(text)
        assert result == expected

    def test_normalize_end_parentheses(self):
        text = "abc）def〕ghi】jkl》mno"
        expected = "abc）def）ghi）jkl）mno"
        result = normalize_text.SymbolNomalizer.normalize_end_parentheses(text)
        assert result == expected

    def test_normalize_horizontal_bars(self):
        text = "abc-def-ghi"
        expected = "abc－def－ghi"
        result = normalize_text.SymbolNomalizer.normalize_horizontal_bars(text)
        assert result == expected

    def test_normalize_horizontal_bars_check_all(self):
        text = "a-bーc−d―e‐fｰg–h—i"
        expected = "a－b－c－d－e－f－g－h－i"
        result = normalize_text.SymbolNomalizer.normalize_horizontal_bars(text)
        assert result == expected


class TestMarkBoundary:
    def test_mark_end_of_sentence(self):
        text = "ａｂｃ．ｄｅｆ\nｇｈｉｊ．"
        expected = "$ａｂｃ$ｄｅｆ$ｇｈｉｊ$"
        result = normalize_text.MarkBoundary.mark_end_of_sentence(text)
        assert result == expected

    def test_mark_boundary(self):
        text = "ａｂｃ．ｄｅｆ\nｇｈｉｊ．"
        expected = "$ａｂｃ$ｄｅｆ$ｇｈｉｊ$"
        result = normalize_text.MarkBoundary.mark_boundary(text)
        assert result == expected


class TestIntegrationTest:
    def test_integration(self):
        text = "abc、def。ghi\nabc-def-ghi"
        expected = "$ａｂｃ$ｄｅｆ$ｇｈｉ$ａｂｃ－ｄｅｆ－ｇｈｉ$"
        result = normalize_text.normalize(text)
        assert result == expected
