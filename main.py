from __future__ import print_function
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QLabel, QMessageBox


from get_auth import auth
from get_docs import get_data
from data_parser import convert_google_document_to_json
from data_reducer import reducer
from add_sheets import create_sheet, add_data_to_sheet

doc_id = ""


class Form(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        hbox = QVBoxLayout(self)
        self.lbl = QLabel("Enter Google Docs URL", self)
        self.qle = QLineEdit(self)
        self.btn = QPushButton("Submit")

        self.qle.returnPressed.connect(self.convert)
        self.btn.clicked.connect(self.convert)

        hbox.addWidget(self.lbl)
        hbox.addSpacing(20)
        hbox.addWidget(self.qle)
        hbox.addWidget(self.btn)

        self.setGeometry(400, 400, 350, 300)
        self.setWindowTitle('Accessibility Docs to Sheets')
        self.show()

    def convert(self):
        url = self.qle.text()
        doc_id = url[url.index("d/") +
                     2:url.index("/", url.index("d/") + 2)]
        creds = auth()
        document = get_data(creds, doc_id)
        qmb = QMessageBox()
        if document is not None:
            parsed_arr = convert_google_document_to_json(document)
            data = reducer(parsed_arr)
            title = document["title"]
            sp_id = create_sheet(creds, title)
            if add_data_to_sheet(sp_id, creds, data):
                qmb.setWindowTitle("Success")
                qmb.setText("Finished successfully!")
            else:
                qmb.setWindowTitle("Error")
                qmb.setText("Error")
        else:
            qmb.setWindowTitle("Error")
            qmb.setText("Error")
        qmb.exec()


def main():
    app = QApplication([])
    window = Form()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
