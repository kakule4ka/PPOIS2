from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox, 
                             QTableView, QLabel, QHeaderView)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from constants import ConditionType

class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить клиента")
        self.layout = QFormLayout(self)

        self.fio_input = QLineEdit()
        self.account_input = QLineEdit()
        self.address_input = QLineEdit()
        self.mobile_input = QLineEdit()
        self.home_input = QLineEdit()

        self.layout.addRow("ФИО:", self.fio_input)
        self.layout.addRow("Номер счета:", self.account_input)
        self.layout.addRow("Адрес прописки:", self.address_input)
        self.layout.addRow("Моб. телефон:", self.mobile_input)
        self.layout.addRow("Дом. телефон:", self.home_input)

        self.btn_submit = QPushButton("Сохранить")
        self.btn_submit.clicked.connect(self.accept)
        self.layout.addRow(self.btn_submit)

    def get_data(self):
        return (
            self.fio_input.text(),
            self.account_input.text(),
            self.address_input.text(),
            self.mobile_input.text(),
            self.home_input.text()
        )

class SearchDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Поиск клиентов")
        self.resize(700, 500)
        self.results = []
        self.current_page = 1
        self.page_size = 10

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.condition_combo = QComboBox()
        self.condition_combo.addItem("По номеру телефона или фамилии", ConditionType.PHONE_OR_LASTNAME)
        self.condition_combo.addItem("По номеру счета или адресу", ConditionType.ACCOUNT_OR_ADDRESS)
        self.condition_combo.addItem("По ФИО и цифрам в номере", ConditionType.FULLNAME_AND_DIGITS)
        self.condition_combo.currentIndexChanged.connect(self.update_labels)

        self.param1_input = QLineEdit()
        self.param2_input = QLineEdit()
        
        self.param1_label = QLabel("Телефон:")
        self.param2_label = QLabel("Фамилия:")

        self.form_layout.addRow("Условие:", self.condition_combo)
        self.form_layout.addRow(self.param1_label, self.param1_input)
        self.form_layout.addRow(self.param2_label, self.param2_input)

        self.btn_search = QPushButton("Искать")
        self.btn_search.clicked.connect(self.perform_search)
        self.form_layout.addRow(self.btn_search)

        self.layout.addLayout(self.form_layout)

        self.table_view = QTableView()
        self.layout.addWidget(self.table_view)

        self.pagination_layout = QHBoxLayout()
        self.btn_prev = QPushButton("< Пред")
        self.lbl_page = QLabel("Страница: 1/1")
        self.btn_next = QPushButton("След >")
        
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)

        self.pagination_layout.addWidget(self.btn_prev)
        self.pagination_layout.addWidget(self.lbl_page)
        self.pagination_layout.addWidget(self.btn_next)
        
        self.layout.addLayout(self.pagination_layout)

    def update_labels(self):
        self.param1_input.clear()
        self.param2_input.clear()
        cond = self.condition_combo.currentData()
        if cond == ConditionType.PHONE_OR_LASTNAME:
            self.param1_label.setText("Телефон:")
            self.param2_label.setText("Фамилия:")
        elif cond == ConditionType.ACCOUNT_OR_ADDRESS:
            self.param1_label.setText("Номер счета:")
            self.param2_label.setText("Адрес:")
        elif cond == ConditionType.FULLNAME_AND_DIGITS:
            self.param1_label.setText("ФИО (часть):")
            self.param2_label.setText("Цифры из номера:")

    def perform_search(self):
        cond = self.condition_combo.currentData()
        p1 = self.param1_input.text()
        p2 = self.param2_input.text()
        self.results = self.controller.search_clients(cond, p1, p2)
        self.current_page = 1
        self.update_table()

    def update_table(self):
        total_pages = max(1, (len(self.results) + self.page_size - 1) // self.page_size)
        self.lbl_page.setText(f"Страница: {self.current_page}/{total_pages} | Найдено: {len(self.results)}")

        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_data = self.results[start_idx:end_idx]

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ID", "ФИО", "Счет", "Адрес", "Моб. тел", "Дом. тел"])
        
        for row in page_data:
            model.appendRow([QStandardItem(str(item)) for item in row])
        self.table_view.setModel(model)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.setColumnWidth(1, 150)
        self.table_view.setColumnWidth(2, 160)
        self.table_view.setColumnWidth(3, 200)
        self.table_view.setColumnWidth(4, 130)
        self.table_view.setColumnWidth(5, 130)
        header.setStretchLastSection(True)

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        total_pages = max(1, (len(self.results) + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_table()

class DeleteDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Удаление клиентов")
        self.layout = QFormLayout(self)

        self.condition_combo = QComboBox()
        self.condition_combo.addItem("По номеру телефона или фамилии", ConditionType.PHONE_OR_LASTNAME)
        self.condition_combo.addItem("По номеру счета или адресу", ConditionType.ACCOUNT_OR_ADDRESS)
        self.condition_combo.addItem("По ФИО и цифрам в номере", ConditionType.FULLNAME_AND_DIGITS)
        self.condition_combo.currentIndexChanged.connect(self.update_labels)

        self.param1_input = QLineEdit()
        self.param2_input = QLineEdit()
        
        self.param1_label = QLabel("Телефон:")
        self.param2_label = QLabel("Фамилия:")

        self.layout.addRow("Условие:", self.condition_combo)
        self.layout.addRow(self.param1_label, self.param1_input)
        self.layout.addRow(self.param2_label, self.param2_input)

        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self.perform_delete)
        self.layout.addRow(self.btn_delete)

    def update_labels(self):
        self.param1_input.clear()
        self.param2_input.clear()
        cond = self.condition_combo.currentData()
        if cond == ConditionType.PHONE_OR_LASTNAME:
            self.param1_label.setText("Телефон:")
            self.param2_label.setText("Фамилия:")
        elif cond == ConditionType.ACCOUNT_OR_ADDRESS:
            self.param1_label.setText("Номер счета:")
            self.param2_label.setText("Адрес:")
        elif cond == ConditionType.FULLNAME_AND_DIGITS:
            self.param1_label.setText("ФИО (часть):")
            self.param2_label.setText("Цифры из номера:")

    def perform_delete(self):
        cond = self.condition_combo.currentData()
        p1 = self.param1_input.text()
        p2 = self.param2_input.text()
        deleted_count = self.controller.delete_clients(cond, p1, p2)
        
        if deleted_count > 0:
            QMessageBox.information(self, "Результат", f"Успешно удалено записей: {deleted_count}")
            self.accept()
        else:
            QMessageBox.warning(self, "Результат", "Записей по данным условиям не найдено.")