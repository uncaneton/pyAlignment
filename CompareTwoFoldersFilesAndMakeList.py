# 比較兩個資料夾的檔案，並列出只存在於一方的檔案為TXT

import os

# 比較するフォルダのパス
folder1 = "C:/Users/batt7/Desktop/SpeakLD3_osaka_output/textgrid/"
folder2 = "C:/Users/batt7/Desktop/SpeakLD3_osaka_output/wav/"

# 去掉副檔名，獲取主文件名的函數
def get_base_names(folder):
    return {os.path.splitext(filename)[0] for filename in os.listdir(folder)}

# 獲取主文件名集合
base_names_in_folder1 = get_base_names(folder1)
base_names_in_folder2 = get_base_names(folder2)

# 只存在於 folder1 的文件名（忽略副檔名）
only_in_folder1 = base_names_in_folder1 - base_names_in_folder2

# 只存在於 folder2 的文件名（忽略副檔名）
only_in_folder2 = base_names_in_folder2 - base_names_in_folder1

# 將結果保存到檔案中
with open("only_in_folder1.txt", "w") as f1:
    for base_name in sorted(only_in_folder1):
        f1.write(base_name + "\n")

with open("only_in_folder2.txt", "w") as f2:
    for base_name in sorted(only_in_folder2):
        f2.write(base_name + "\n")




# 結果輸出
print("Files only in folder1 (ignoring extensions):")
print("\n".join(sorted(only_in_folder1)))

print("\nFiles only in folder2 (ignoring extensions):")
print("\n".join(sorted(only_in_folder2)))