from unittest.mock import patch
from main_window import MainWindow
from controller import Controller

def test_main_window_init_and_pagination(qtbot, tmp_path):
    ctrl = Controller(str(tmp_path / "db.db"))
    for i in range(5):
        ctrl.add_client(f"T{i}", "1", "A", "1", "2")
        
    window = MainWindow(ctrl)
    qtbot.addWidget(window)
    
    window.spin_page_size.setValue(2)
    window.btn_next.click()
    assert ctrl.current_page == 2
    window.btn_prev.click()
    assert ctrl.current_page == 1
    window.btn_last.click()
    assert ctrl.current_page == 3
    window.btn_first.click()
    assert ctrl.current_page == 1

def test_main_window_actions(qtbot, tmp_path):
    ctrl = Controller(str(tmp_path / "db.db"))
    window = MainWindow(ctrl)
    qtbot.addWidget(window)
    
    with patch('PyQt6.QtWidgets.QMessageBox.question') as mock_question:
        mock_question.return_value = mock_question.return_value.Yes
        window.clear_data()
        
    with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("dummy.xml", "")):
        with patch.object(ctrl, 'load_from_xml'):
            with patch('PyQt6.QtWidgets.QMessageBox.information'):
                window.load_xml()

    with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("dummy.xml", "")):
        with patch.object(ctrl, 'save_to_xml'):
            with patch('PyQt6.QtWidgets.QMessageBox.information'):
                window.save_xml()