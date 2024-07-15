import os
import sys
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QListWidget, QTextEdit, QMessageBox, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
import qtmodern.styles
import qtmodern.windows
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
import time

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

icon_path = os.path.join(application_path, 'format.ico')

class CopyThread(QThread):
    finished = pyqtSignal()
    progress_changed = pyqtSignal(int, str)

    total_files = 0
    copied_files = 0

    def __init__(self, src_directory, dest_directory, keywords, target_folder_names):
        QThread.__init__(self)
        self.src_directory = src_directory
        self.dest_directory = dest_directory
        self.keywords = keywords
        self.target_folder_names = target_folder_names

    def ensure_dir_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def copy_files_to_destination(self, src_folder, dest_folder):
        for root, _, files in os.walk(src_folder):
            for file in files:
                if file.lower().endswith((".jpeg", ".jpg", ".png")):
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(dest_folder, file)
                    shutil.copy2(src_path, dest_path)
                    self.copied_files += 1
                    progress_value = int(self.copied_files / self.total_files * 100)
                    self.progress_changed.emit(progress_value, "")

    def run(self):
        target_folder_names = [name.lower() for name in self.target_folder_names]
        all_files = []

        for directory, dirs, _ in os.walk(self.src_directory):
            if any(keyword in directory for keyword in self.keywords):
                if "VM" in directory.upper():
                    continue
                for dir_name in dirs:
                    if dir_name.lower() in target_folder_names:
                        src_folder = os.path.join(directory, dir_name)
                        dest_folder = os.path.join(self.dest_directory, dir_name)
                        self.ensure_dir_exists(dest_folder)

                        for root, _, files in os.walk(src_folder):
                            for file in files:
                                if file.lower().endswith((".jpeg", ".jpg", ".png")):
                                    all_files.append((os.path.join(root, file), os.path.join(dest_folder, file)))

        self.total_files = len(all_files)
        self.copied_files = 0
        total_copy_time = 0.0  # 總複製時間
        start_time = time.time()

        for src, dest in all_files:
            start_copy_time = time.time()
            shutil.copy2(src, dest)
            end_copy_time = time.time()
            copy_time = end_copy_time - start_copy_time
            total_copy_time += copy_time

            self.copied_files += 1
            progress_value = int(self.copied_files / self.total_files * 100)

            if self.copied_files > 0:
                average_copy_time = total_copy_time / self.copied_files
                remaining_files = self.total_files - self.copied_files
                remaining_time = average_copy_time * remaining_files

                hours = int(remaining_time / 3600)
                minutes = int((remaining_time % 3600) / 60)
                seconds = int(remaining_time % 60)

                remaining_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.progress_changed.emit(progress_value, remaining_time_str)
            else:
                self.progress_changed.emit(progress_value, "")

        self.finished.emit()

class PhotocopyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADC Photocopy")
        app.setWindowIcon(QIcon(icon_path))

        self.layout = QVBoxLayout()

        self.src_dir_label = QLabel('原始路徑:')
        self.src_dir_entry = QLineEdit()
        self.src_dir_entry.setText('K:\TPAS_AVI_PHOTO_REVIEW\AVI_Image_Copy')
        self.src_dir_update_button = QPushButton('更新')
        self.src_dir_update_button.clicked.connect(self.update_src_directory)

        self.dest_dir_label = QLabel('目標路徑:')
        self.dest_dir_entry = QLineEdit()
        self.dest_dir_entry.setText('H:\資料備份區\測試區(01)')
        self.dest_dir_update_button = QPushButton('更新')
        self.dest_dir_update_button.clicked.connect(self.update_dest_directory)

        self.keywords_label = QLabel('PRODUCT GROUP:')
        self.keywords_listbox = QListWidget()
        self.keywords_listbox.addItem("BN59")

        self.new_keyword_entry = QLineEdit()
        self.add_button = QPushButton('新增GROUP')
        self.add_button.clicked.connect(self.add_keyword)
        self.delete_button = QPushButton('刪除GROUP')
        self.delete_button.clicked.connect(self.delete_selected_keyword)

        self.target_folder_names_label = QLabel('複製的資料夾項目:')
        self.target_folder_names_text = QTextEdit()
        self.target_folder_names_text.setText("\n".join(["10_Probe Mark Shift", "15_Overkill", "2D_Ugly Die", "09_Foreign Material", "16_Particle", "07_process defect","1B_Pad discoloration","18_Al particle","0F_Al particle out of PAD"]))

        self.update_button = QPushButton('更新參數(如有變更任一參數，需在執行前點擊)')
        self.update_button.clicked.connect(self.update_values)
        self.start_button = QPushButton('開始執行')
        self.start_button.clicked.connect(self.start_program)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)

        self.progress_label = QLabel("預估剩餘時間: 00:00:00")

        self.layout.addWidget(self.src_dir_label)
        self.layout.addWidget(self.src_dir_entry)
        self.layout.addWidget(self.src_dir_update_button)
        self.layout.addWidget(self.dest_dir_label)
        self.layout.addWidget(self.dest_dir_entry)
        self.layout.addWidget(self.dest_dir_update_button)
        self.layout.addWidget(self.keywords_label)
        self.layout.addWidget(self.keywords_listbox)
        self.layout.addWidget(self.new_keyword_entry)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.target_folder_names_label)
        self.layout.addWidget(self.target_folder_names_text)
        self.layout.addWidget(self.update_button)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.progress_label)

        self.setLayout(self.layout)

    def update_src_directory(self):
        src_directory = QFileDialog.getExistingDirectory()
        self.src_dir_entry.setText(src_directory)

    def update_dest_directory(self):
        dest_directory = QFileDialog.getExistingDirectory()
        self.dest_dir_entry.setText(dest_directory)

    def add_keyword(self):
        keyword = self.new_keyword_entry.text().strip()
        if keyword:
            if any(c.isspace() for c in keyword) or not keyword:
                QMessageBox.warning(self, " ", "請輸入正確數值(不包含特殊符號含空格)")
            else:
                if keyword in [self.keywords_listbox.item(i).text() for i in range(self.keywords_listbox.count())]:
                    QMessageBox.information(self, " ", "輸入的Group已存在")
                else:
                    self.keywords_listbox.addItem(keyword)
                    self.new_keyword_entry.clear()

    def delete_selected_keyword(self):
        for item in self.keywords_listbox.selectedItems():
            self.keywords_listbox.takeItem(self.keywords_listbox.row(item))

    def update_values(self):
        try:
            self.src_directory = self.src_dir_entry.text()
            self.dest_directory = self.dest_dir_entry.text()
            self.keywords = [self.keywords_listbox.item(i).text() for i in range(self.keywords_listbox.count())]
            self.target_folder_names = self.target_folder_names_text.toPlainText().strip().split('\n')
            QMessageBox.information(self, " ", "更新成功")
        except Exception as e:
            print(f"An error occurred: {e}")
            QMessageBox.critical(self, " ", f"更新失敗：{e}")

    def start_program(self):
        try:
            self.src_directory = self.src_dir_entry.text()
            self.dest_directory = self.dest_dir_entry.text()
            self.keywords = [self.keywords_listbox.item(i).text() for i in range(self.keywords_listbox.count())]
            self.target_folder_names = self.target_folder_names_text.toPlainText().strip().split('\n')
            self.thread = CopyThread(self.src_directory, self.dest_directory, self.keywords, self.target_folder_names)
            self.thread.finished.connect(self.show_completion_message)
            self.thread.progress_changed.connect(self.update_progress)
            self.thread.start()
            self.start_button.setEnabled(False)  # 禁用"開始執行"按鈕
            QMessageBox.information(self, " ", "程式執行中...點擊'OK'關閉視窗 ; 請勿關閉exe執行檔")
        except Exception as e:
            QMessageBox.critical(self, " ", "執行失敗：" + str(e))

    def update_progress(self, progress_value, remaining_time_str):
        self.progress.setValue(progress_value)
        self.progress_label.setText(f"預估剩餘時間: {remaining_time_str}")

    def show_completion_message(self):
        QMessageBox.information(self, " ", "所有圖片已被複製")

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 新增設定字體和大小的程式碼
    font = QFont("微軟正黑體", 9)
    app.setFont(font)

    qtmodern.styles.dark(app)
    ex = PhotocopyApp()
    mw = qtmodern.windows.ModernWindow(ex)

    mw.setWindowTitle("ADC Photo copy")
    mw.setGeometry(350, 70, 1100, 880)

    app.setStyleSheet("QProgressBar { color: red; background-color: yellow; }")
    button_style = "QPushButton { min-width: 250px; min-height: 40px; }"
    app.setStyleSheet("QPushButton { min-width: 250px; min-height: 40px; }")
    ex.src_dir_update_button.setStyleSheet(button_style)
    ex.dest_dir_update_button.setStyleSheet(button_style)
    ex.add_button.setStyleSheet(button_style)
    ex.delete_button.setStyleSheet(button_style)
    ex.update_button.setStyleSheet(button_style)
    ex.start_button.setStyleSheet(button_style)

    mw.show()
    sys.exit(app.exec_())
