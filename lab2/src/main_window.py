from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSpinBox, QTableView, QTreeView, 
                             QToolBar, QTabWidget, QFileDialog, QMessageBox, QMenu,
                             QHeaderView)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QAction
from PyQt6.QtCore import Qt
from dialogs import AddDialog, SearchDialog, DeleteDialog

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
        self.update_view()

    def init_ui(self):
        self.setWindowTitle("Управление клиентами банка")
        self.resize(850, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.table_view = QTableView()
        self.tree_view = QTreeView()
        
        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        
        self.tabs.addTab(self.table_view, "Табличный вид")
        self.tabs.addTab(self.tree_view, "Древовидный вид")
        self.main_layout.addWidget(self.tabs)

        self.pagination_layout = QHBoxLayout()
        self.btn_first = QPushButton("<< Первая")
        self.btn_prev = QPushButton("< Пред")
        self.lbl_page_info = QLabel("Страница: 1/1 | Записей: 0")
        self.btn_next = QPushButton("След >")
        self.btn_last = QPushButton("Последняя >>")
        
        self.spin_page_size = QSpinBox()
        self.spin_page_size.setRange(1, 100)
        self.spin_page_size.setValue(self.controller.page_size)

        self.pagination_layout.addWidget(self.btn_first)
        self.pagination_layout.addWidget(self.btn_prev)
        self.pagination_layout.addWidget(self.lbl_page_info)
        self.pagination_layout.addWidget(self.btn_next)
        self.pagination_layout.addWidget(self.btn_last)
        self.pagination_layout.addWidget(QLabel("Записей на странице:"))
        self.pagination_layout.addWidget(self.spin_page_size)

        self.main_layout.addLayout(self.pagination_layout)

        self.create_actions()
        self.create_menus()
        self.create_toolbar()
        self.connect_signals()

    def create_actions(self):
        self.action_add = QAction("Добавить", self)
        self.action_search = QAction("Поиск", self)
        self.action_delete = QAction("Удалить", self)
        self.action_clear = QAction("Очистить базу", self)
        self.action_load = QAction("Загрузить XML", self)
        self.action_save = QAction("Сохранить XML", self)

    def create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction(self.action_load)
        file_menu.addAction(self.action_save)

        edit_menu = menubar.addMenu("Правка")
        edit_menu.addAction(self.action_add)
        edit_menu.addAction(self.action_search)
        edit_menu.addAction(self.action_delete)
        edit_menu.addSeparator()
        edit_menu.addAction(self.action_clear)

    def create_toolbar(self):
        toolbar = QToolBar("Главная панель")
        self.addToolBar(toolbar)
        toolbar.addAction(self.action_add)
        toolbar.addAction(self.action_search)
        toolbar.addAction(self.action_delete)
        toolbar.addAction(self.action_clear)
        toolbar.addSeparator()
        toolbar.addAction(self.action_load)
        toolbar.addAction(self.action_save)

    def show_context_menu(self, position):
        menu = QMenu()
        menu.addAction(self.action_add)
        menu.addAction(self.action_search)
        menu.addAction(self.action_delete)
        menu.exec(self.table_view.viewport().mapToGlobal(position))

    def connect_signals(self):
        self.btn_first.clicked.connect(self.on_first_page)
        self.btn_prev.clicked.connect(self.on_prev_page)
        self.btn_next.clicked.connect(self.on_next_page)
        self.btn_last.clicked.connect(self.on_last_page)
        self.spin_page_size.valueChanged.connect(self.on_page_size_changed)

        self.action_add.triggered.connect(self.open_add_dialog)
        self.action_search.triggered.connect(self.open_search_dialog)
        self.action_delete.triggered.connect(self.open_delete_dialog)
        self.action_clear.triggered.connect(self.clear_data)
        self.action_load.triggered.connect(self.load_xml)
        self.action_save.triggered.connect(self.save_xml)

    def update_view(self):
        data = self.controller.get_current_page_data()
        headers = ["ID", "ФИО", "Счет", "Адрес", "Моб. тел", "Дом. тел"]

        table_model = QStandardItemModel()
        table_model.setHorizontalHeaderLabels(headers)
        
        tree_model = QStandardItemModel()
        tree_model.setHorizontalHeaderLabels(["Структура записей"])

        for row in data:
            table_row = [QStandardItem(str(item)) for item in row]
            table_model.appendRow(table_row)

            client_node = QStandardItem(f"{row[1]} (ID: {row[0]})")
            client_node.appendRow([QStandardItem(f"Номер счета: {row[2]}")])
            client_node.appendRow([QStandardItem(f"Адрес прописки: {row[3]}")])
            client_node.appendRow([QStandardItem(f"Моб. телефон: {row[4]}")])
            client_node.appendRow([QStandardItem(f"Дом. телефон: {row[5]}")])
            
            tree_model.appendRow(client_node)

        self.table_view.setModel(table_model)
        self.tree_view.setModel(tree_model)

        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.setColumnWidth(1, 150)
        self.table_view.setColumnWidth(2, 160)
        self.table_view.setColumnWidth(3, 200)
        self.table_view.setColumnWidth(4, 130)
        self.table_view.setColumnWidth(5, 130)
        header.setStretchLastSection(True)

        self.lbl_page_info.setText(
            f"Страница: {self.controller.current_page}/{self.controller.total_pages} | "
            f"Всего записей: {self.controller.total_records}"
        )

    def on_first_page(self):
        self.controller.first_page()
        self.update_view()

    def on_prev_page(self):
        self.controller.prev_page()
        self.update_view()

    def on_next_page(self):
        self.controller.next_page()
        self.update_view()

    def on_last_page(self):
        self.controller.last_page()
        self.update_view()

    def on_page_size_changed(self, value):
        self.controller.set_page_size(value)
        self.update_view()

    def open_add_dialog(self):
        dialog = AddDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.controller.add_client(*data)
            self.update_view()

    def open_search_dialog(self):
        dialog = SearchDialog(self.controller, self)
        dialog.exec()

    def open_delete_dialog(self):
        dialog = DeleteDialog(self.controller, self)
        if dialog.exec():
            self.update_view()

    def clear_data(self):
        reply = QMessageBox.question(self, 'Подтверждение', 'Удалить все записи из базы данных?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.clear_all()
            self.update_view()

    def load_xml(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Загрузить XML", "", "XML Files (*.xml);;All Files (*)")
        if file_name:
            self.controller.load_from_xml(file_name)
            self.update_view()
            QMessageBox.information(self, "Успешно", "Данные загружены.")

    def save_xml(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить XML", "", "XML Files (*.xml);;All Files (*)")
        if file_name:
            self.controller.save_to_xml(file_name)
            QMessageBox.information(self, "Успешно", "Данные сохранены.")