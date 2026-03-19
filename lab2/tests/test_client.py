from client import Client

def test_client_initialization():
    client = Client("Иванов И.И.", "12345", "Минск", "+37529111", "8017111", 1)
    assert client.client_id == 1
    assert client.full_name == "Иванов И.И."
    assert client.account_number == "12345"
    assert client.address == "Минск"
    assert client.mobile_phone == "+37529111"
    assert client.home_phone == "8017111"