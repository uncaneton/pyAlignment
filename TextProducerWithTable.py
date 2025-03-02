import os
import pandas as pd

# CSV からファイル名と中身を読み込む
df = pd.read_csv("/Users/chuyu/Library/CloudStorage/Dropbox/research/2021_Taiwanese_downstep_with_Kevin/202409 exp/juliusPart2.csv", encoding="utf-8")


# Directory where you want to create files
output_dir = "/Users/chuyu/Library/CloudStorage/Dropbox/research/2021_Taiwanese_downstep_with_Kevin/202409 exp/txt/"

# Make sure the directory exists (optional)
os.makedirs(output_dir, exist_ok=True)

for i, row in df.iterrows():
    # row["filename"] might be something like "test1.txt"
    fname = row["filename"]
    text_content = row["julius"]
    
    # Construct the full path: /path/to/output_directory/test1.txt
    filepath = os.path.join(output_dir, fname)
    
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(text_content)
    
    print(f"成功啦! {filepath}")
