# devcontainer
https://mcr.microsoft.com/v2/devcontainers/anaconda/tags/list


# history
conda create -n py313 python=3.13
conda activate py313

# 前処理手順

1.  **全角化（Zenkaku normalization）**  
    　→ 文字幅を揃えて、データのばらつきを防ぐ。
    
2.  **連続空白を1つに正規化（Whitespace normalization）**  
    　→ 半角/全角の連続スペースやタブを1個の普通の空白にする。
    
3.  **連続改行を1つに正規化（Newline normalization）**  
    　→ 複数改行を1つの改行にまとめ、文区切りを安定させる。
    
4.  **伸ばし棒の統一（Long vowel normalization）**  
    　→ 半角ハイフン・長音符（例：「－」「ー」）を「ー」に統一する。
    
5.  **区切り記号の統一（Punctuation normalization）**  
    　→ 「、」「，」「。」「．」「\r\n」などを、すべて「．」に統一。
    
6.  **文頭文末に特殊記号を付与（Sentence boundary marking）**  
    → 各文章を `^文章$` の形式に変換（．も文末記号と認識）。
    
7.  **改行単位で配列化（Segmentation）**  
    　→ 各文（＝1行）を要素とする配列データへ変換。

