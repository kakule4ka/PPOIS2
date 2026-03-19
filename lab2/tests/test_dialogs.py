from unittest.mock import patch
from dialogs import AddDialog, SearchDialog, DeleteDialog
from controller import Controller

def test_add_dialog(qtbot):
    dialog = AddDialog()
    qtbot.addWidget(dialog)
    dialog.fio_input.setText("Тест")
    dialog.account_input.setText("123")
    dialog.address_input.setText("Адрес")
    dialog.mobile_input.setText("111")
    dialog.home_input.setText("222")
    assert dialog.get_data() == ("Тест", "123", "Адрес", "111", "222")

def test_search_dialog(qtbot, tmp_path):
    ctrl = Controller(str(tmp_path / "db.db"))
    for i in range(15):
        ctrl.add_client(f"A{i}", "1", "2", "3", "4")
        
    dialog = SearchDialog(ctrl)
    qtbot.addWidget(dialog)
    
    dialog.condition_combo.setCurrentIndex(1)
    assert dialog.param1_label.text() == "Номер счета:"
    dialog.condition_combo.setCurrentIndex(2)
    assert dialog.param1_label.text() == "ФИО (часть):"
    dialog.condition_combo.setCurrentIndex(0)
    
    dialog.param2_input.setText("A")
    dialog.btn_search.click()
    assert len(dialog.results) == 15
    
    dialog.btn_next.click()
    assert dialog.current_page == 2
    dialog.btn_next.click()
    
    dialog.btn_prev.click()
    assert dialog.current_page == 1
    dialog.btn_prev.click()

def test_delete_dialog(qtbot, tmp_path):
    ctrl = Controller(str(tmp_path / "db.db"))
    ctrl.add_client("Тест", "123", "Адрес", "111", "222")
    dialog = DeleteDialog(ctrl)
    qtbot.addWidget(dialog)
    
    dialog.condition_combo.setCurrentIndex(1)
    assert dialog.param2_label.text() == "Адрес:"
    dialog.condition_combo.setCurrentIndex(2)
    dialog.condition_combo.setCurrentIndex(0)
    
    dialog.param2_input.setText("Тест")
    with patch('PyQt6.QtWidgets.QMessageBox.information'):
        dialog.btn_delete.click()
        
    dialog.param2_input.setText("Неизвестный")
    with patch('PyQt6.QtWidgets.QMessageBox.warning'):
        dialog.btn_delete.click()