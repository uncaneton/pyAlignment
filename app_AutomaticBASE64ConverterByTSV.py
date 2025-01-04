# - This app assumes that you have conducted recording experiments on platforms like jsPsych. "
# It automatically converts Base64-encoded audio data in your CSV or TSV experiment files into WAV files.\n"
# - Some forced alignment tools require audio files to be in 16kHz mono format. You can check the option for conversion if needed.\n"
# - If your experiment files already include text for alignment, this app can help generate UTF-8 encoded TXT files. "
# After processing, you'll have WAV files along with their corresponding TXT files, ready for alignment.\n"
# 
# 20250104 by Chuyu Huang"


import sys
import os
import base64
import pandas as pd
from ffmpy import FFmpeg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel,
    QPushButton, QLineEdit, QVBoxLayout, QWidget, QComboBox,
    QProgressBar, QListWidget, QListWidgetItem, QAbstractItemView, QCheckBox, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt

class Base64ToWavApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Base64 to WAV Converter")
        self.resize(600, 800)  # window size
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Input file selection
        self.file_label = QLabel("Input TSV/CSV File:")
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_button = QPushButton("Select File")
        self.file_button.clicked.connect(self.select_file)

        # Help button
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_help)

        # Base64 column selection
        self.base64_label = QLabel("Select the Column Containing:")
        self.base64_combobox = QComboBox()

        # File naming columns (multiple selection)
        self.naming_label = QLabel("Select Columns for File Naming:")
        self.naming_list = QListWidget()
        self.naming_list.setSelectionMode(QAbstractItemView.MultiSelection)

        # Include index checkbox
        self.index_checkbox = QCheckBox("Include index in file name")
        self.index_checkbox.setChecked(True)

        # Convert to 16kHz mono checkbox
        self.convert_checkbox = QCheckBox("Convert WAV to 16kHz Mono (for automatic forced alignment)")
        self.convert_checkbox.setChecked(False)

        # File list options group
        file_list_group = QGroupBox("File List Options")
        file_list_layout = QVBoxLayout()

        # Generate file list checkbox
        self.file_list_checkbox = QCheckBox("Generate file list (CSV)")
        self.file_list_checkbox.setChecked(False)
        self.file_list_checkbox.toggled.connect(self.toggle_content_option)

        # Content column options
        self.content_checkbox = QCheckBox("Column to write in the 'content' of TXT")
        self.content_checkbox.setChecked(False)
        self.content_checkbox.setEnabled(False)
        self.content_combobox = QComboBox()
        self.content_combobox.setEnabled(False)

        # Generate TXT files checkbox
        self.txt_checkbox = QCheckBox("Generate corresponding TXT files")
        self.txt_checkbox.setChecked(False)

        file_list_layout.addWidget(self.file_list_checkbox)
        file_list_layout.addWidget(self.content_checkbox)
        file_list_layout.addWidget(self.content_combobox)
        file_list_layout.addWidget(self.txt_checkbox)
        file_list_group.setLayout(file_list_layout)

        # Output folder selection
        self.output_label = QLabel("Output Folder:")
        self.output_input = QLineEdit()
        self.output_input.setReadOnly(True)
        self.output_button = QPushButton("Select Output Folder")
        self.output_button.clicked.connect(self.select_output_folder)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # Process button
        self.process_button = QPushButton("Start to Process Files")
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold;
                font-size: 16px;  /* fontsize */
                padding: 10px 20px;  /* interval */
            }
            QPushButton:hover {
                background-color: #45A049;  /* color when clicked */
            }
        """)
        self.process_button.setFixedSize(200, 50)  # button size (width height)
        self.process_button.clicked.connect(self.process_files)

        # Adding widgets to layout
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.file_button)
        layout.addWidget(self.help_button) 
        layout.addWidget(self.base64_label)
        layout.addWidget(self.base64_combobox)
        layout.addWidget(self.naming_label)
        layout.addWidget(self.naming_list)
        layout.addWidget(self.index_checkbox)
        layout.addWidget(self.convert_checkbox)
        layout.addWidget(file_list_group)
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_input)
        layout.addWidget(self.output_button)
        layout.addWidget(self.progress_bar)
  #     layout.addWidget(self.process_button) # 與下方重複
        layout.addWidget(self.process_button, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_help(self):
        """Show help information."""
        help_text = (
            "- This app assumes that you have conducted recording experiments on platforms like jsPsych. "
            "It automatically converts Base64-encoded audio data in your CSV or TSV experiment files into WAV files.\n"
            "- Some forced alignment tools require audio files to be in 16kHz mono format. You can check the option for conversion if needed.\n"
            "- If your experiment files already include text for alignment, this app can help generate UTF-8 encoded TXT files. "
            "After processing, you'll have WAV files along with their corresponding TXT files, ready for alignment.\n"
            "    - 2025 by Chuyu Huang"
        )
        QMessageBox.information(self, "Help", help_text)

    # (Rest of your methods remain unchanged...)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "TSV/CSV Files (*.tsv *.csv)")
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
            
            # Populate column selectors
            self.base64_combobox.clear()
            self.naming_list.clear()
            self.content_combobox.clear()
            self.base64_combobox.addItems(self.df.columns)
            self.content_combobox.addItems(self.df.columns)
            for col in self.df.columns:
                item = QListWidgetItem(col)
                item.setCheckState(0)
                self.naming_list.addItem(item)
        except Exception as e:
            print(f"Error loading file: {e}")

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_input.setText(folder_path)

    def toggle_content_option(self):
        """Enable or disable content column options based on file list checkbox."""
        self.content_checkbox.setEnabled(self.file_list_checkbox.isChecked())
        self.content_combobox.setEnabled(self.file_list_checkbox.isChecked() and self.content_checkbox.isChecked())
        self.content_checkbox.toggled.connect(lambda: self.content_combobox.setEnabled(self.content_checkbox.isChecked()))

    def get_selected_columns(self):
        """Retrieve the selected columns for file naming."""
        selected_columns = []
        for i in range(self.naming_list.count()):
            item = self.naming_list.item(i)
            if item.checkState():
                selected_columns.append(item.text())
        return selected_columns

    def process_files(self):
        base64_col = self.base64_combobox.currentText()
        selected_columns = self.get_selected_columns()
        output_dir = self.output_input.text()

        # Ensure the wav and txt directories exist
        wav_dir = os.path.join(output_dir, "wav")
        txt_dir = os.path.join(output_dir, "txt")
        os.makedirs(wav_dir, exist_ok=True)
        os.makedirs(txt_dir, exist_ok=True)

        total_rows = len(self.df)
        self.progress_bar.setMaximum(total_rows)

        converted_files = []  # Store successfully converted file names
        content_values = []   # Store content values if applicable

        for index, row in self.df.iterrows():
            try:
                # Generate file name using selected columns
                file_base = "_".join([str(row[col]) for col in selected_columns])
                if self.index_checkbox.isChecked():
                    file_base += f"_index{index}"  # Add index if checkbox is checked
                webm_file = os.path.join(wav_dir, f"{file_base}.webm")
                wav_file = os.path.join(wav_dir, f"{file_base}.wav")

                # Decode Base64 to WebM
                s = str(row[base64_col]).strip()
                s += '=' * (-len(s) % 4)  # Padding Base64 string
                decoded_data = base64.b64decode(s)
                with open(webm_file, 'wb') as f:
                    f.write(decoded_data)

                # Convert webm to WAV using FFmpeg
                ff = FFmpeg(
                    inputs={webm_file: None},
                    outputs={wav_file: '-c:a pcm_f32le'}
                )
                ff.run()

                # If "Convert WAV to 16kHz Mono" is checked
                if self.convert_checkbox.isChecked():
                    temp_wav = os.path.join(wav_dir, f"{file_base}_16khz_mono.wav")
                    ff_convert = FFmpeg(
                        inputs={wav_file: None},
                        outputs={temp_wav: '-ar 16000 -ac 1'}
                    )
                    ff_convert.run()
                    os.replace(temp_wav, wav_file)  # Replace original WAV file

                # Add to converted files list
                converted_files.append(f"{file_base}.wav")

                # If content column is selected, store content values
                if self.content_checkbox.isChecked():
                    content_values.append(row[self.content_combobox.currentText()])
                else:
                    content_values.append("")  # Empty content

                # Update progress bar
                self.progress_bar.setValue(index + 1)

            except Exception as e:
                print(f"Error processing row {index}: {e}")

        # Generate file list if checkbox is checked
        if self.file_list_checkbox.isChecked():
            file_list_path = os.path.join(output_dir, "file_list.csv")
            file_list_df = pd.DataFrame({"filename": converted_files, "content": content_values})
            file_list_df.to_csv(file_list_path, index=False)

            # Generate TXT files if checkbox is checked
            if self.txt_checkbox.isChecked():
                for fname, content in zip(file_list_df["filename"], file_list_df["content"]):
                    txt_file = os.path.join(txt_dir, f"{os.path.splitext(fname)[0]}.txt")
                    with open(txt_file, "w", encoding="utf-8") as f:
                        f.write(str(content) if pd.notna(content) else "")

        # Show completion message
        QMessageBox.information(self, "Completed", "Process completed successfully!")

# Start the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Base64ToWavApp()
    window.show()
    sys.exit(app.exec_())

