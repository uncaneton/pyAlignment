import os
from praatio import textgrid

# 入力ディレクトリと出力ディレクトリを指定
input_dir = '/Users/chuyu/Library/CloudStorage/Dropbox/research/2024_dvandva_coordinate_TCP/2024dvandvaExp/intermediateResultFiles/TextGridAddTargetTier/'  # TextGridファイルが保存されているフォルダ
output_dir = '/Users/chuyu/Library/CloudStorage/Dropbox/research/2024_dvandva_coordinate_TCP/2024dvandvaExp/intermediateResultFiles/TextGridAddTargetTier/'  # 更新されたファイルの保存先

# 出力ディレクトリが存在しない場合は作成
os.makedirs(output_dir, exist_ok=True)


# 新しいInterval Tierを作成する関数
def add_targetword_tier_at_bottom(textgrid_path, output_path):
    # TextGridファイルを読み込む
    tg = textgrid.openTextgrid(textgrid_path, includeEmptyIntervals=True)
    
    # TextGridの最小・最大時間を取得
    min_time = tg.minTimestamp
    max_time = tg.maxTimestamp

    # 新しいTierの名前
    new_tier_name = "TargetWord"

    # Tierがすでに存在しているかを確認
    tier_names = [tier.name for tier in tg.tiers]
    if new_tier_name in tier_names:
        print(f"Tier '{new_tier_name}' already exists in {textgrid_path}. Skipping.")
        return

    # 新しいTierを作成 (例: 空のインターバルを1つ含む)
    new_tier = textgrid.IntervalTier(new_tier_name, [(min_time, max_time, "")], minT=min_time, maxT=max_time)

    # TextGridに新しいTierを追加
    tg.addTier(new_tier)

    # 更新されたTextGridを保存
    tg.save(output_path, format="short_textgrid", includeBlankSpaces=True)
    print(f"Updated TextGrid saved: {output_path}")

# 全てのTextGridファイルに適用
for filename in os.listdir(input_dir):
    if filename.endswith(".TextGrid"):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        add_targetword_tier_at_bottom(input_path, output_path)

print("All applicable TextGrid files have been updated.")