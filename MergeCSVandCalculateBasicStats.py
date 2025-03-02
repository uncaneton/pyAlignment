import sys
import os
import glob
import pandas as pd

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

def read_csv_fallback(path, nrows=None):
    """
    複数のエンコードを試してCSVを読み込むヘルパー関数。
    - 'utf-8-sig' -> 'shift_jis' の順にトライ
    - 読み込みに成功したらDataFrameを返す
    - すべて失敗したら例外を送出
    """
    encodings_to_try = ["utf-8-sig", "shift_jis"]
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(path, encoding=enc, nrows=nrows)
            return df
        except Exception as e:
            pass
    raise ValueError(f"{os.path.basename(path)} をutf-8-sig/shift_jisで読み込めませんでした。")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV結合＆統計計算アプリ (混在エンコード対応)")

        # UI部品
        self.folder_path_edit = QLineEdit()  # CSVフォルダのパス表示
        self.col_list_widget = QListWidget()  # 列一覧の表示
        self.col_list_widget.setSelectionMode(self.col_list_widget.SelectionMode.MultiSelection)

        # レイアウト作成
        layout = QVBoxLayout()

        # (1) フォルダ選択
        folder_layout = QHBoxLayout()
        folder_label = QLabel("CSVフォルダ:")
        folder_btn = QPushButton("参照...")
        folder_btn.clicked.connect(self.on_browse_folder)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)

        # (2) 列情報取得ボタン
        get_cols_btn = QPushButton("列リストを取得")
        get_cols_btn.clicked.connect(self.on_get_columns)
        layout.addWidget(get_cols_btn)

        # (3) 列リスト表示
        layout.addWidget(QLabel("統計を計算する列 (複数選択可):"))
        layout.addWidget(self.col_list_widget)

        # (4) 実行ボタン
        run_btn = QPushButton("実行")
        run_btn.clicked.connect(self.on_run)
        layout.addWidget(run_btn)

        self.setLayout(layout)
        self.resize(600, 500)

        # 内部変数
        self.csv_files = []  # フォルダ内にあるCSVファイルのリスト
        self.all_columns = []  # CSV結合時の列名一覧

    def on_browse_folder(self):
        """フォルダ選択"""
        folder_selected = QFileDialog.getExistingDirectory(self, "CSVフォルダを選択")
        if folder_selected:
            self.folder_path_edit.setText(folder_selected)

    def on_get_columns(self):
        """
        指定フォルダ内の全CSVを先頭行(nrows=0)だけ読み、列名を総合的に取得（重複含む→union）
        """
        folder_path = self.folder_path_edit.text().strip()
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "エラー", "有効なCSVフォルダを指定してください。")
            return

        # .csvファイル収集
        self.csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
        if not self.csv_files:
            QMessageBox.information(self, "情報", "フォルダ内にCSVファイルがありません。")
            return

        # 重複をまとめるためのセット
        all_cols_set = set()
        for csv_file in self.csv_files:
            try:
                tmp_df = read_csv_fallback(csv_file, nrows=0)
                # nrows=0 で列名だけ読み込み
                for c in tmp_df.columns:
                    all_cols_set.add(c)
            except Exception as e:
                QMessageBox.warning(self, "エラー", f"{os.path.basename(csv_file)} の列情報取得失敗:\n{e}")
                # 失敗した場合はスキップ or ここでreturn するか方針次第
                # ここではとりあえずスキップ
                continue

        self.all_columns = sorted(list(all_cols_set))

        # ListWidgetに表示
        self.col_list_widget.clear()
        for col in self.all_columns:
            item = QListWidgetItem(col)
            self.col_list_widget.addItem(item)

        QMessageBox.information(self, "成功", "列リストを更新しました。")

    def on_run(self):
        """
        1) CSVをすべて読み込み(混在文字コード対応)、縦方向に結合 -> merged.csv
        2) ユーザーが選んだ列に対して統計計算 -> stats.csv
        """
        folder_path = self.folder_path_edit.text().strip()
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "エラー", "有効なフォルダが指定されていません。")
            return

        if not self.csv_files:
            QMessageBox.warning(self, "エラー", "CSVファイルが見つかりません。先に『列リストを取得』を押してください。")
            return

        selected_cols_idx = self.col_list_widget.selectedIndexes()
        selected_cols = [self.col_list_widget.item(i.row()).text() for i in selected_cols_idx]

        # (1) CSV結合
        df_list = []
        for csv_file in self.csv_files:
            try:
                # 混在文字コード対応
                tmp_df = read_csv_fallback(csv_file)
                df_list.append(tmp_df)
            except Exception as e:
                QMessageBox.warning(self, "エラー", f"{os.path.basename(csv_file)} の読み込みに失敗:\n{e}")
                # 失敗したら処理中断するか、スキップするかは要件次第。ここでは中断
                return

        if not df_list:
            QMessageBox.information(self, "情報", "結合するCSVがありませんでした。")
            return

        merged_df = pd.concat(df_list, ignore_index=True)
        merged_csv_path = os.path.join(folder_path, "merged.csv")
        try:
            merged_df.to_csv(merged_csv_path, index=False, encoding="utf-8-sig")
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"merged.csv の保存に失敗:\n{e}")
            return

        # (2) 統計: 選択された列だけ
        if not selected_cols:
            # 統計列が1つも選ばれていないなら merged.csv だけ作って終了
            QMessageBox.information(self, "完了", f"結合が完了しました。\n{merged_csv_path} に保存。")
            return

        stats_rows = []
        for col in selected_cols:
            if col not in merged_df.columns:
                # 存在しない列
                stats_rows.append({
                    "column": col,
                    "statistic": "ERROR",
                    "value": f"列 '{col}' は存在しません"
                })
                continue

            col_series = merged_df[col].dropna()
            if len(col_series) == 0:
                # すべてNaN
                stats_rows.append({
                    "column": col,
                    "statistic": "NO_DATA",
                    "value": "非空データがありません"
                })
                continue

            # 数値への変換トライ
            numeric_col = None
            try:
                numeric_col = pd.to_numeric(col_series)
            except:
                pass

            if numeric_col is not None:
                # 数値列
                stats_mean = numeric_col.mean()
                stats_min  = numeric_col.min()
                stats_max  = numeric_col.max()
                stats_std  = numeric_col.std()

                stats_rows.append({"column": col, "statistic": "mean", "value": stats_mean})
                stats_rows.append({"column": col, "statistic": "min",  "value": stats_min})
                stats_rows.append({"column": col, "statistic": "max",  "value": stats_max})
                stats_rows.append({"column": col, "statistic": "std",  "value": stats_std})
            else:
                # 非数値列として扱う
                stats_rows.append({"column": col, "statistic": "mean", "value": "非数値列"})
                stats_rows.append({"column": col, "statistic": "min",  "value": "非数値列"})
                stats_rows.append({"column": col, "statistic": "max",  "value": "非数値列"})
                stats_rows.append({"column": col, "statistic": "std",  "value": "非数値列"})

            # 各ユニーク値の count, ratio
            vc = col_series.value_counts(dropna=False)
            total_count = vc.sum()
            for val_name, cnt in vc.items():
                ratio = cnt / total_count
                stats_rows.append({
                    "column": col,
                    "value": val_name,
                    "count": cnt,
                    "ratio": ratio
                })

        stats_df = pd.DataFrame(stats_rows)
        stats_csv_path = os.path.join(folder_path, "stats.csv")
        try:
            stats_df.to_csv(stats_csv_path, index=False, encoding="utf-8-sig")
        except Exception as e:
            QMessageBox.warning(self, "エラー", f"stats.csv の保存に失敗:\n{e}")
            return

        QMessageBox.information(
            self,
            "完了",
            f"結合と統計計算が完了しました。\n\n"
            f"結合データ: {merged_csv_path}\n"
            f"統計データ: {stats_csv_path}"
        )

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
