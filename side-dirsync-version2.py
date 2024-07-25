import os
import filecmp
import shutil
import hashlib
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QFileDialog,
    QMessageBox, QStyleFactory
)
from PySide6.QtCore import Qt, QThread, Signal

class SyncThread(QThread):
    update_progress = Signal(str)
    sync_completed = Signal()
    sync_error = Signal(str)

    def __init__(self, source, dest, verbose, purge, forcecopy, use_content, two_way, hverify):
        super().__init__()
        self.source = source
        self.dest = dest
        self.verbose = verbose
        self.purge = purge
        self.forcecopy = forcecopy
        self.use_content = use_content
        self.two_way = two_way
        self.hverify = hverify

    def run(self):
        try:
            self.synchronize_directories(self.source, self.dest, self.verbose, self.purge, self.forcecopy, False, self.use_content, self.two_way, self.hverify, self.log)
            self.sync_completed.emit()
        except Exception as e:
            self.sync_error.emit(str(e))

    def log(self, message):
        self.update_progress.emit(message)

    def synchronize_directories(self, source, dest, verbose, purge, forcecopy, use_ctime, use_content, two_way, hverify, log_func):
        if not os.path.exists(dest):
            os.makedirs(dest)
            if verbose:
                log_func(f"Created target directory: {dest}")

        def compare_and_copy(src, dst, reverse=False):
            comparison = filecmp.dircmp(src, dst)
            copy_files(comparison, src, dst, reverse)
            if purge:
                delete_files(comparison, dst)

        def copy_files(comp, src, dst, reverse):
            for name in comp.left_only:
                srcpath = os.path.join(src, name)
                dstpath = os.path.join(dst, name)
                if os.path.isdir(srcpath):
                    shutil.copytree(srcpath, dstpath)
                    if verbose:
                        log_func(f"Copied directory: {srcpath} to {dstpath}")
                else:
                    shutil.copy2(srcpath, dstpath)
                    if verbose:
                        log_func(f"Copied file: {srcpath} to {dstpath}")

            for name in comp.common_files:
                srcpath = os.path.join(src, name)
                dstpath = os.path.join(dst, name)
                if forcecopy or not filecmp.cmp(srcpath, dstpath, shallow=not use_content):
                    if reverse:
                        shutil.copy2(dstpath, srcpath)
                        if verbose:
                            log_func(f"Updated file: {dstpath} to {srcpath}")
                    else:
                        shutil.copy2(srcpath, dstpath)
                        if verbose:
                            log_func(f"Updated file: {srcpath} to {dstpath}")

            for subdir in comp.common_dirs:
                compare_and_copy(os.path.join(src, subdir), os.path.join(dst, subdir), reverse)

        def delete_files(comp, dst):
            for name in comp.right_only:
                dstpath = os.path.join(dst, name)
                if os.path.isdir(dstpath):
                    shutil.rmtree(dstpath)
                    if verbose:
                        log_func(f"Deleted directory: {dstpath}")
                else:
                    os.remove(dstpath)
                    if verbose:
                        log_func(f"Deleted file: {dstpath}")

        def compute_file_md5(file_path):
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
            return md5_hash.hexdigest()

        def verify_md5(src, dst):
            src_files = []
            dst_files = []

            for root, _, files in os.walk(src):
                for name in files:
                    src_files.append(os.path.relpath(os.path.join(root, name), src))

            for root, _, files in os.walk(dst):
                for name in files:
                    dst_files.append(os.path.relpath(os.path.join(root, name), dst))

            all_files = set(src_files + dst_files)
            match = True

            for file in all_files:
                src_file = os.path.join(src, file)
                dst_file = os.path.join(dst, file)

                if os.path.exists(src_file) and os.path.exists(dst_file):
                    src_md5 = compute_file_md5(src_file)
                    dst_md5 = compute_file_md5(dst_file)
                    if src_md5 != dst_md5:
                        match = False
                        log_func(f"MD5 mismatch for {file}: {src_md5} (source) vs {dst_md5} (destination)")
                    else:
                        log_func(f"MD5 match for {file}: {src_md5}")
                else:
                    match = False
                    log_func(f"File {file} is not present in both source and destination")

            if match:
                log_func("All files are synchronized (MD5 hashes match).")
            else:
                log_func("Some files are not synchronized (MD5 hashes do not match).")

        compare_and_copy(source, dest)
        if two_way:
            compare_and_copy(dest, source, reverse=True)

        if hverify:
            verify_md5(source, dest)

class SyncApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Directory Synchronizer')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.source_label = QLabel("Source Directory:")
        self.source_input = QLineEdit()
        self.source_button = QPushButton("Browse...")

        self.dest_label = QLabel("Destination Directory:")
        self.dest_input = QLineEdit()
        self.dest_button = QPushButton("Browse...")

        self.verbose_check = QCheckBox("Verbose")
        self.verbose_check.setChecked(True)
        self.purge_check = QCheckBox("Purge")
        self.forcecopy_check = QCheckBox("Force Copy")
        self.use_content_check = QCheckBox("Use Content")
        self.two_way_check = QCheckBox("Two-Way Sync")
        self.hverify_check = QCheckBox("Hash Verify")
        self.hverify_check.setChecked(True)

        self.sync_button = QPushButton("Synchronize")

        self.progress_text = QTextEdit()
        self.progress_text.setReadOnly(True)

        source_layout = QVBoxLayout()
        source_layout.addWidget(self.source_label)
        source_layout.addWidget(self.source_input)
        source_layout.addWidget(self.source_button)

        dest_layout = QVBoxLayout()
        dest_layout.addWidget(self.dest_label)
        dest_layout.addWidget(self.dest_input)
        dest_layout.addWidget(self.dest_button)

        checkboxes_layout = QHBoxLayout()
        checkboxes_layout_left = QVBoxLayout()
        checkboxes_layout_right = QVBoxLayout()

        checkboxes = [
            self.verbose_check, self.purge_check,
            self.forcecopy_check, self.use_content_check,
            self.two_way_check, self.hverify_check
        ]

        for i, checkbox in enumerate(checkboxes):
            checkbox.setStyleSheet("QCheckBox {font-size: 16px;}")  # Increase checkbox size
            if i % 2 == 0:
                checkboxes_layout_left.addWidget(checkbox)
            else:
                checkboxes_layout_right.addWidget(checkbox)

        checkboxes_layout.addLayout(checkboxes_layout_left)
        checkboxes_layout.addLayout(checkboxes_layout_right)

        self.layout.addLayout(source_layout)
        self.layout.addLayout(dest_layout)
        self.layout.addLayout(checkboxes_layout)
        self.layout.addWidget(self.sync_button)
        self.layout.addWidget(self.progress_text)

        self.source_button.clicked.connect(self.on_browse_source)
        self.dest_button.clicked.connect(self.on_browse_dest)
        self.sync_button.clicked.connect(self.on_sync)

        # Set a better theme for visibility
        QApplication.setStyle(QStyleFactory.create("Windows"))
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        palette.setColor(self.foregroundRole(), Qt.black)
        self.setPalette(palette)

    def on_browse_source(self):
        self.browse_directory(self.source_input)

    def on_browse_dest(self):
        self.browse_directory(self.dest_input)

    def browse_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, "Choose a directory")
        if directory:
            line_edit.setText(directory)

    def on_sync(self):
        source = self.source_input.text()
        dest = self.dest_input.text()
        verbose = self.verbose_check.isChecked()
        purge = self.purge_check.isChecked()
        forcecopy = self.forcecopy_check.isChecked()
        use_content = self.use_content_check.isChecked()
        two_way = self.two_way_check.isChecked()
        hverify = self.hverify_check.isChecked()

        if not source or not dest:
            QMessageBox.critical(self, "Error", "Please select both source and destination directories.")
            return

        self.progress_text.clear()
        self.sync_button.setDisabled(True)

        self.sync_thread = SyncThread(source, dest, verbose, purge, forcecopy, use_content, two_way, hverify)
        self.sync_thread.update_progress.connect(self.append_progress_text)
        self.sync_thread.sync_completed.connect(self.sync_completed)
        self.sync_thread.sync_error.connect(self.sync_error)
        self.sync_thread.start()

    def append_progress_text(self, message):
        self.progress_text.append(message)

    def sync_completed(self):
        QMessageBox.information(self, "Success", "Synchronization completed successfully!")
        self.sync_button.setDisabled(False)

    def sync_error(self, error_message):
        QMessageBox.critical(self, "Error", f"Synchronization failed: {error_message}")
        self.sync_button.setDisabled(False)

if __name__ == "__main__":
    app = QApplication([])
    window = SyncApp()
    window.show()
    app.exec()