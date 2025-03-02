import os

def add_txt_extension_to_files(folder_path):
    # フォルダ内のすべてのファイルを取得
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        # ファイルかどうかを確認
        if os.path.isfile(file_path):
            # すでに .txt 拡張子がない場合にのみ追加
            if not file_name.endswith('.txt'):
                new_file_name = file_name + '.txt'
                new_file_path = os.path.join(folder_path, new_file_name)
                os.rename(file_path, new_file_path)
                print(f"Renamed: {file_name} -> {new_file_name}")

# 実行するフォルダのパスを指定
folder_path = "/Users/chuyu/Library/CloudStorage/Dropbox/research/2021_Taiwanese_downstep_with_Kevin/202409 exp/part1_3_txt"  # ここを実際のフォルダパスに置き換える
add_txt_extension_to_files(folder_path)
