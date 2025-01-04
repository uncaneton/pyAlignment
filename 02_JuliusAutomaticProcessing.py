import os
import shutil
import subprocess

def process_files(folder_a, folder_b, folder_c, batch_size, pl_script_path):
    wav_dir = os.path.join(folder_b, 'wav')
    if not os.path.exists(wav_dir):
        os.makedirs(wav_dir)

    while True:
        files = [f for f in os.listdir(folder_a) if os.path.isfile(os.path.join(folder_a, f))]
        
        # WAVファイルと対応するTXTファイルをペアで抽出
        pairs = []
        for file in files:
            if file.endswith('.wav'):
                txt_file = file.replace('.wav', '.txt')
                if txt_file in files:
                    pairs.append((file, txt_file))
        
        # バッチサイズ分のペアを取り出す
        batch = pairs[:batch_size]
        if not batch:  # ファイルがなくなったら終了
            print("No more files to process.")
            break

        # バッチのファイルをフォルダーBの./wavにコピー
        for wav_file, txt_file in batch:
            shutil.copy(os.path.join(folder_a, wav_file), os.path.join(wav_dir, wav_file))
            shutil.copy(os.path.join(folder_a, txt_file), os.path.join(wav_dir, txt_file))

        print(f"Copied {len(batch)} files to ./wav directory.")

        # .pl スクリプトを実行
        print(f"Running Perl script: {pl_script_path}")
        try:
            subprocess.run(['perl', pl_script_path], cwd=folder_b, check=True, text=True, capture_output=True)
            print("Perl script executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running Perl script: {e.stderr}")
            break

        # フォルダーBのファイルをフォルダーCに移動
        for file in os.listdir(wav_dir):
            shutil.move(os.path.join(wav_dir, file), folder_c)

        print("Moved files from ./wav directory to folder C.")

        # フォルダーAから使用済みのファイルを削除
        for wav_file, txt_file in batch:
            os.remove(os.path.join(folder_a, wav_file))
            os.remove(os.path.join(folder_a, txt_file))

        print(f"Processed {len(batch)} files. Moving to next batch...")

# 設定
folder_a = "C:/Users/batt7/Desktop/sokuon_txt_wav/"
folder_b = "C:/Users/batt7/Documents/segmentation-kit-4.3.1/"
folder_c = "C:/Users/batt7/Desktop/sokuon_result/"
batch_size = 96
pl_script_path = "C:/Users/batt7/Documents/segmentation-kit-4.3.1/segment_julius.pl"
process_files(folder_a, folder_b, folder_c, batch_size, pl_script_path)
