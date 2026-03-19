import pytest
from controller import Controller
from constants import ConditionType

@pytest.fixture
def controller(tmp_path):
    db_path = tmp_path / "test_ctrl.db"
    return Controller(str(db_path))

def test_controller_pagination_logic(controller):
    for i in range(15):
        controller.add_client(f"N{i}", "A", "M", "P", "H")
    
    controller.set_page_size(10)
    assert len(controller.get_current_page_data()) == 10
    
    controller.next_page()
    assert controller.current_page == 2
    
    controller.next_page()
    assert controller.current_page == 2 
    
    controller.prev_page()
    assert controller.current_page == 1
    
    controller.prev_page()
    assert controller.current_page == 1
    
    controller.last_page()
    assert controller.current_page == 2
    
    controller.first_page()
    assert controller.current_page == 1

def test_controller_search_delete(controller):
    controller.add_client("Иванов", "123", "Минск", "111", "222")
    
    res1 = controller.search_clients(ConditionType.PHONE_OR_LASTNAME, None, "Иванов")
    assert len(res1) == 1
    res2 = controller.search_clients(ConditionType.ACCOUNT_OR_ADDRESS, "123", None)
    assert len(res2) == 1
    res3 = controller.search_clients(ConditionType.FULLNAME_AND_DIGITS, "Иванов", "11")
    assert len(res3) == 1
    res4 = controller.search_clients(None, None, None)
    assert res4 == []

    assert controller.delete_clients(ConditionType.PHONE_OR_LASTNAME, None, "Иванов") == 1
    
    controller.add_client("А", "1", "М", "2", "3")
    assert controller.delete_clients(ConditionType.ACCOUNT_OR_ADDRESS, "1", None) == 1
    
    controller.add_client("А", "1", "М", "2", "3")
    assert controller.delete_clients(ConditionType.FULLNAME_AND_DIGITS, "А", "2") == 1

    assert controller.delete_clients(None, None, None) == 0

def test_controller_xml_operations(controller, tmp_path):
    controller.add_client("Иванов", "123", "Минск", "111", "222")
    xml_file = tmp_path / "data.xml"
    
    controller.save_to_xml(str(xml_file))
    controller.clear_all()
    controller.update_pagination_info()
    assert controller.total_records == 0
    
    controller.load_from_xml(str(xml_file))
    controller.update_pagination_info()
    assert controller.total_records == 1