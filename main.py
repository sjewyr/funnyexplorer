import os
import shutil
from PyQt6.QtWidgets import (
    QPushButton,
    QApplication,
    QListWidget,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox,
    QMenu,
    QInputDialog,
    QStyle,
    QScrollArea,
    QFrame,
)

from PyQt6 import QtCore
import rename_window


class ScrollMessageBox(QMessageBox):
    def __init__(self, lst, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        self.content = QWidget()
        scroll.setWidget(self.content)
        lay = QVBoxLayout(self.content)
        scroll.setMinimumWidth(500) if len(
            max(lst, key=lambda x: len(x))
        ) < 88 else scroll.setMinimumWidth(900)
        scroll.setMinimumHeight(300) if len(lst) < 50 else scroll.setMinimumHeight(600)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        for item in lst:
            lay.addWidget(QLabel(item))
        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Explorer")
        self.setGeometry(100, 100, 800, 600)

        self.initgui()
        # Connect the button click event to a callback function
        self.dir = os.curdir
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.menu = QMenu(self)
        action = self.menu.addAction("Create File")
        action.triggered.connect(self.create_file)
        action2 = self.menu.addAction("Create Directory")
        action2.triggered.connect(self.create_directory)

    def initgui(self):
        self.setLayout(QVBoxLayout())
        self.button = QPushButton("Get Directory Contents", self)
        # Add additional GUI elements here if needed
        self.list_widget = QListWidget(self)
        self.layout().addWidget(self.list_widget)
        self.layout().addWidget(self.button)
        self.button.clicked.connect(self.on_button_clicked)
        self.list_widget.itemDoubleClicked.connect(self.on_list_double_click)

    def on_list_double_click(self, item: QListWidgetItem):
        if item.data(26):
            self.dir = os.path.join(self.dir, item.data(25))
            self.on_button_clicked()
        else:
            with open(os.path.join(self.dir, item.data(25)), "r") as f:
                try:
                    _ = ScrollMessageBox(f.readlines(), self)
                    _.setWindowTitle(item.data(25))
                    _.exec()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to read file. {str(e)}")

    def get_directory_contents(self):
        res = [
            (x, x, os.path.isdir(os.path.join(self.dir, x)))
            for x in os.listdir(self.dir)
        ]
        res.append(("..", os.path.abspath(os.path.join(self.dir, "..")), True))
        return sorted(res, key=lambda x: x[0])

    def show_context_menu(self, position):
        self.menu.exec(self.list_widget.viewport().mapToGlobal(position))

    def create_file(self):
        file_name, _ = QInputDialog.getText(self, "Create File", "Enter file name:")
        if file_name:
            file_path = os.path.join(self.dir, file_name)
            open(file_path, "w").close()
            self.on_button_clicked()

    def create_directory(self):
        dir_name, _ = QInputDialog.getText(
            self, "Create Directory", "Enter directory name:"
        )
        if dir_name:
            dir_path = os.path.join(self.dir, dir_name)
            os.mkdir(dir_path)
            self.on_button_clicked()

    def on_button_clicked(self):
        self.list_widget.clear()
        res = self.get_directory_contents()
        for label_name, name, is_dir in res:
            item = QListWidgetItem(self.list_widget)
            widget = ExplorerItem(
                label_name, self.dir, self.list_widget, item, name, is_dir
            )
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)


class ExplorerItem(QWidget):
    def __init__(
        self, label_name, _dir, list_widget, list_item, name, is_dir, parent=None
    ):
        super().__init__(parent)
        self.dir = _dir
        self.label_name = label_name
        self.list_widget: QListWidget = list_widget
        self.setLayout(QHBoxLayout())
        self.list_item: QListWidgetItem = list_item
        self.is_dir = is_dir
        self.list_item.setData(26, self.is_dir)

        self.name = name
        self.icon = (
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
            if self.is_dir
            else self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        )
        self.list_item.setData(25, self.name)
        self.label = QLabel(label_name, self)
        self.list_item.setIcon(self.icon)

        self.layout().addWidget(self.label)
        if self.label_name != "..":
            self.delete_button = QPushButton(text="Delete", parent=self)
            self.rename_button = QPushButton(text="Rename", parent=self)
            self.delete_button.clicked.connect(self.delete)
            self.rename_button.clicked.connect(self._rename)
            self.layout().addWidget(self.delete_button)
            self.layout().addWidget(self.rename_button)

    def _rename(self, *args):
        # Implement renaming functionality here
        self.rename_window = rename_window.RenameWindow(self.name, self)
        self.rename_window.show()

    def delete(self, *args):
        dialog = QMessageBox(self)
        dialog.setWindowTitle(self.name)
        dialog.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )
        dialog.setText(f"Are you sure you want to delete {self.name}?")
        button = dialog.exec()
        if button == QMessageBox.StandardButton.Cancel:
            return
        try:
            os.remove(os.path.join(self.dir, self.name))
        except Exception:
            shutil.rmtree(os.path.join(self.dir, self.name))
        # Implement deleting functionality here
        self.list_widget.takeItem(self.list_widget.row(self.list_item))

    def rename(self, name):
        os.rename(os.path.join(self.dir, self.name), name)
        self.name = name
        self.label.setText(name)
        self.list_item.setData(25, self.name)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
