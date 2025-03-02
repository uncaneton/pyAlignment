import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel,
    QPushButton, QVBoxLayout, QWidget, QMessageBox
)

class CsvTsvMerger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV/TSV to TSV Merger")
        self.resize(400, 200)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # ラベル
        self.info_label = QLabel("Select CSV/TSV files to merge into a TSV file:")
        layout.addWidget(self.info_label)

        # ボタン：CSV/TSV選択
        self.select_files_button = QPushButton("Select CSV/TSV Files")
        self.select_files_button.clicked.connect(self.select_files)
        layout.addWidget(self.select_files_button)

        # ボタン：保存
        self.save_button = QPushButton("Save Merged TSV")
        self.save_button.clicked.connect(self.save_tsv)
        self.save_button.setEnabled(False)  # CSV/TSV選択前は無効
        layout.addWidget(self.save_button)

        # メインウィジェットとレイアウト
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 選択したファイルを保持するリスト
        self.selected_files = []

    def select_files(self):
        # 複数のCSV/TSVファイルを選択
        files, _ = QFileDialog.getOpenFileNames(self, "Select CSV/TSV Files", "", "CSV/TSV Files (*.csv *.tsv)")
        if files:
            self.selected_files = files
            self.info_label.setText(f"{len(files)} files selected.")
            self.save_button.setEnabled(True)

    def save_tsv(self):
        if not self.selected_files:
            QMessageBox.warning(self, "No Files Selected", "Please select CSV or TSV files first.")
            return

        # 保存するTSVファイルのパスを選択
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Merged TSV File", "", "TSV Files (*.tsv)")
        if not output_path:
            return

        # CSV/TSVファイルを読み込み、結合してTSVとして保存
        try:
            dataframes = []
            for file in self.selected_files:
                if file.endswith(".csv"):
                    df = pd.read_csv(file)
                elif file.endswith(".tsv"):
                    df = pd.read_csv(file, sep="\t")
                else:
                    continue  # 対応外のファイルはスキップ
                dataframes.append(df)
            
            merged_df = pd.concat(dataframes, ignore_index=True)
            merged_df.to_csv(output_path, sep="\t", index=False)
            QMessageBox.information(self, "Success", f"Merged TSV saved to:\n{output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication([])
    window = CsvTsvMerger()
    window.show()
    app.exec_()
