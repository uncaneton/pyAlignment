import os
import tkinter as tk
from tkinter import filedialog

def remove_dot_zero_in_filenames():
    # Hide the root Tkinter window (we only want the dialog)
    root = tk.Tk()
    root.withdraw()

    # Ask user to select a directory
    folder_path = filedialog.askdirectory(title="Select folder to rename files")

    # If no folder was selected, exit
    if not folder_path:
        print("No folder selected. Exiting...")
        return

    # Go through each file in the selected folder
    for filename in os.listdir(folder_path):
        if ".0" in filename:
            old_path = os.path.join(folder_path, filename)
            new_filename = filename.replace(".0", "")
            new_path = os.path.join(folder_path, new_filename)

            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: {filename} -> {new_filename}")

if __name__ == "__main__":
    remove_dot_zero_in_filenames()
