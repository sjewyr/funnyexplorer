from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit


class RenameWindow(QWidget):
    def __init__(self, name, requester, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Rename {name}")
        self.requester = requester
        self.name_label = QLabel(f"Current Name: {name}", self)
        self.new_name_label = QLabel("New Name:", self)
        self.new_name_edit = QLineEdit(self)
        self.rename_button = QPushButton("Rename", self)
        self.cancel_button = QPushButton("Cancel", self)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.new_name_label)
        layout.addWidget(self.new_name_edit)
        layout.addWidget(self.rename_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        self.rename_button.clicked.connect(self.rename)
        self.cancel_button.clicked.connect(self.close)

    def rename(self):
        new_name = self.new_name_edit.text()
        print(f"Renamed {self.name_label.text()} to {new_name}")
        self.requester.rename(new_name)
        self.close()
