import os

# 対象フォルダーのパス
folder_path = "/Users/chuyu/Desktop/part3"

# フォルダー内のファイルを取得
for filename in os.listdir(folder_path):
    # フォルダー内のファイルの完全パスを取得
    old_file_path = os.path.join(folder_path, filename)
    
    # ファイルであるか確認（フォルダーを除外）
    if os.path.isfile(old_file_path):
        # 新しいファイル名を作成 !!! 這裡放要加在前面的東西
        new_filename = f"sub3_{filename}"
        new_file_path = os.path.join(folder_path, new_filename)
        
        # ファイル名を変更
        os.rename(old_file_path, new_file_path)
        print(f"Renamed: {filename} -> {new_filename}")
