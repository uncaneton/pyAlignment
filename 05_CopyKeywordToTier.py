# Tierに指定のキーワードがあれば、あらたにTargetWordのTierにそのまま移す

import os
from praatio import textgrid

# 入力ディレクトリと出力ディレクトリを指定
input_dir = '/Users'  # TextGridファイルが保存されているフォルダ
output_dir = '/Users'  # 更新されたファイルの保存先


# 検索するキーワードのリスト
keywords = [
    "songwriter", "sweet", "dry", "director", "child",
    "trailer", "green", "operator", "hate", "dryer",
    "seller", "pull", "south", "manager", "time",
    "go", "flow", "float", "teacher"
]

# 出力ディレクトリが存在しない場合は作成
os.makedirs(output_dir, exist_ok=True)

# 新しいTargetWord Tierを作成する関数
def add_targetword_tier_with_keywords(textgrid_path, output_path):
    # TextGridファイルを読み込む
    tg = textgrid.openTextgrid(textgrid_path, includeEmptyIntervals=True)
    
    # words Tierを取得
    words_tier = None
    for tier in tg.tiers:
        if tier.name == "words":  # Tier名を"words"に変更
            words_tier = tier
            break

    if words_tier is None:
        print(f"words Tier not found in {textgrid_path}. Skipping.")
        return

    # キーワードに一致するインターバルを収集
    target_intervals = [
        (start, end, label)
        for start, end, label in words_tier.entries
        if label in keywords
    ]

    if not target_intervals:
        print(f"No keywords found in {textgrid_path}. Skipping.")
        return

    # 新しいTargetWord Tierを作成
    new_tier_name = "TargetWord"
    new_tier = textgrid.IntervalTier(new_tier_name, target_intervals, minT=tg.minTimestamp, maxT=tg.maxTimestamp)

    # 既存のTargetWord Tierを削除（もし存在する場合）
    try:
        tg.removeTier(new_tier_name)
    except KeyError:
        pass  # Tierが存在しない場合は何もしない

    # 新しいTierをTextGridに追加
    tg.addTier(new_tier)

    # 更新されたTextGridを保存
    tg.save(output_path, format="short_textgrid", includeBlankSpaces=True)
    print(f"Updated TextGrid saved: {output_path}")

# 全てのTextGridファイルに適用
for filename in os.listdir(input_dir):
    if filename.endswith(".TextGrid"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        add_targetword_tier_with_keywords(input_path, output_path)

print("All applicable TextGrid files have been updated.")
