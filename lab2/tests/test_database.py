import pytest
from database import Database
from client import Client

@pytest.fixture
def db(tmp_path):
    db_path = tmp_path / "test.db"
    return Database(str(db_path))

def test_add_and_get_count(db):
    client = Client("А", "1", "М", "2", "3")
    db.add_client(client)
    assert db.get_total_count() == 1

def test_get_clients_paginated(db):
    for i in range(15):
        db.add_client(Client(f"N{i}", "A", "M", "P", "H"))
    page = db.get_clients_paginated(10, 0)
    assert len(page) == 10
    page2 = db.get_clients_paginated(10, 10)
    assert len(page2) == 5

def test_search_condition_1(db):
    db.add_client(Client("Иванов", "1", "М", "+37529123", "8017123"))
    db.add_client(Client("Петров", "2", "М", "+37544000", "8017000"))
    
    res1 = db.search_condition_1("123", None)
    assert len(res1) == 1

    res2 = db.search_condition_1(None, "Петров")
    assert len(res2) == 1

    res3 = db.search_condition_1(None, None)
    assert len(res3) == 0

def test_search_condition_2(db):
    db.add_client(Client("Иванов", "ACC123", "Минск", "1", "2"))
    
    res1 = db.search_condition_2("123", None)
    assert len(res1) == 1

    res2 = db.search_condition_2(None, "Минск")
    assert len(res2) == 1

    res3 = db.search_condition_2(None, None)
    assert len(res3) == 0

def test_search_condition_3(db):
    db.add_client(Client("Смирнов", "1", "М", "777", "888"))
    
    res1 = db.search_condition_3("Смирнов", "77")
    assert len(res1) == 1

    res2 = db.search_condition_3("Смирнов", "00")
    assert len(res2) == 0

    res3 = db.search_condition_3(None, None)
    assert len(res3) == 0

def test_delete_conditions(db):
    db.add_client(Client("Иванов", "1", "М", "111", "222"))
    db.add_client(Client("Петров", "2", "М", "333", "444"))
    db.add_client(Client("Сидоров", "3", "Г", "555", "666"))
    
    db.delete_condition_1(None, "Иванов")
    assert db.get_total_count() == 2

    db.delete_condition_2("2", None)
    assert db.get_total_count() == 1

    db.delete_condition_3("Сидоров", "55")
    assert db.get_total_count() == 0

    assert db.delete_condition_1(None, None) == 0
    assert db.delete_condition_2(None, None) == 0
    assert db.delete_condition_3(None, None) == 0

def test_clear_all(db):
    db.add_client(Client("А", "1", "М", "2", "3"))
    db.clear_all()
    assert db.get_total_count() == 0