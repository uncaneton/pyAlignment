import os
import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QComboBox, QMessageBox
)

class BatchTextFileGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("バッチテキストファイル生成ツール")
        self.setGeometry(100, 100, 600, 300)
        layout = QVBoxLayout()

        # 入力ファイル選択
        self.input_label = QLabel("入力ファイル: 未選択")
        self.btn_select_input = QPushButton("ファイルを選択")
        self.btn_select_input.clicked.connect(self.select_input_file)
        layout.addWidget(self.input_label)
        layout.addWidget(self.btn_select_input)

        # 出力ディレクトリ選択
        self.output_label = QLabel("出力ディレクトリ: 未選択")
        self.btn_select_output = QPushButton("フォルダを選択")
        self.btn_select_output.clicked.connect(self.select_output_dir)
        layout.addWidget(self.output_label)
        layout.addWidget(self.btn_select_output)

        # 列選択
        self.filename_dropdown = QComboBox()
        self.content_dropdown = QComboBox()
        layout.addWidget(QLabel("ファイル名にする列:"))
        layout.addWidget(self.filename_dropdown)
        layout.addWidget(QLabel("内容にする列:"))
        layout.addWidget(self.content_dropdown)

        # 生成ボタン
        self.btn_generate = QPushButton("テキストファイルを生成")
        self.btn_generate.clicked.connect(self.generate_text_files)
        layout.addWidget(self.btn_generate)

        self.setLayout(layout)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "ファイルを選択", "", "CSV, TSV, TXT, XLSX (*.csv *.tsv *.txt *.xlsx)")
        if file_path:
            self.input_label.setText(f"入力ファイル: {file_path}")
            self.load_columns(file_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "フォルダを選択")
        if dir_path:
            self.output_label.setText(f"出力ディレクトリ: {dir_path}")

    def load_columns(self, file_path):
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".tsv") or file_path.endswith(".txt"):
                df = pd.read_csv(file_path, sep='\t')
            elif file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                QMessageBox.critical(self, "エラー", "対応していないファイル形式です")
                return
            
            column_names = df.columns.tolist()
            self.filename_dropdown.clear()
            self.content_dropdown.clear()
            self.filename_dropdown.addItems(column_names)
            self.content_dropdown.addItems(column_names)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"ファイルの読み込みに失敗しました: {e}")

    def generate_text_files(self):
        input_path = self.input_label.text().replace("入力ファイル: ", "")
        output_dir = self.output_label.text().replace("出力ディレクトリ: ", "")
        filename_col = self.filename_dropdown.currentText()
        content_col = self.content_dropdown.currentText()
        
        if not os.path.exists(input_path) or not os.path.isdir(output_dir):
            QMessageBox.critical(self, "エラー", "入力ファイルまたは出力ディレクトリが無効です")
            return
        
        try:
            if input_path.endswith(".csv"):
                df = pd.read_csv(input_path)
            elif input_path.endswith(".tsv") or input_path.endswith(".txt"):
                df = pd.read_csv(input_path, sep='\t')
            elif input_path.endswith(".xlsx"):
                df = pd.read_excel(input_path)
            else:
                QMessageBox.critical(self, "エラー", "対応していないファイル形式です")
                return
            
            for _, row in df.iterrows():
                filename = row[filename_col]
                content = row[content_col]
                file_path = os.path.join(output_dir, f"{filename}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(str(content))
            
            QMessageBox.information(self, "完了", "テキストファイルの生成が完了しました！")
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"テキストファイルの生成に失敗しました: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BatchTextFileGenerator()
    window.show()
    sys.exit(app.exec())
