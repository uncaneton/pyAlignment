import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel,
    QPushButton, QLineEdit, QVBoxLayout, QWidget, QComboBox,
    QListWidget, QAbstractItemView, QMessageBox
)

class FilterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TSV/CSV Filter Tool")
        self.resize(600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input file selection
        self.file_label = QLabel("Input TSV/CSV File:")
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)

        # Column selection
        self.column_label = QLabel("Select Column for Filtering:")
        self.column_combobox = QComboBox()
        self.column_combobox.currentTextChanged.connect(self.load_values)

        # Value selection
        self.value_label = QLabel("Select Values to Exclude:")
        self.value_list = QListWidget()
        self.value_list.setSelectionMode(QAbstractItemView.MultiSelection)

        # Output button
        self.output_button = QPushButton("Save Filtered TSV")
        self.output_button.setEnabled(False)
        self.output_button.clicked.connect(self.save_filtered_tsv)

        # Adding widgets to layout
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.file_button)
        layout.addWidget(self.column_label)
        layout.addWidget(self.column_combobox)
        layout.addWidget(self.value_label)
        layout.addWidget(self.value_list)
        layout.addWidget(self.output_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Dataframe for storing input file data
        self.df = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select TSV/CSV File", "", "TSV/CSV Files (*.tsv *.csv)")
        if file_path:
            self.file_input.setText(file_path)
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            if file_path.endswith(".tsv"):
                self.df = pd.read_csv(file_path, sep="\t")
            elif file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            else:
                raise ValueError("Unsupported file format! Please select a TSV or CSV file.")
            
            # Populate column combobox
            self.column_combobox.clear()
            self.column_combobox.addItems(self.df.columns)
            self.value_list.clear()
            self.output_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading file: {e}")

    def load_values(self):
        # Load unique values from selected column
        column = self.column_combobox.currentText()
        if self.df is not None and column:
            unique_values = self.df[column].dropna().unique()
            self.value_list.clear()
            self.value_list.addItems(map(str, unique_values))

    def save_filtered_tsv(self):
        # Get selected column and values to exclude
        column = self.column_combobox.currentText()
        selected_values = [item.text() for item in self.value_list.selectedItems()]
        
        if not selected_values:
            QMessageBox.warning(self, "No Values Selected", "Please select values to exclude.")
            return

        # Filter the dataframe
        filtered_df = self.df[~self.df[column].astype(str).isin(selected_values)]

        # Save the filtered dataframe as TSV
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Filtered TSV File", "", "TSV Files (*.tsv)")
        if output_path:
            filtered_df.to_csv(output_path, sep="\t", index=False)
            QMessageBox.information(self, "Success", f"Filtered TSV saved to:\n{output_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilterApp()
    window.show()
    app.exec_()
