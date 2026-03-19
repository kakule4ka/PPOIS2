from xml_parser import XMLWriter, XMLReader
from client import Client

def test_xml_read_write(tmp_path):
    file_path = tmp_path / "clients.xml"
    clients_to_save = [
        Client("Иванов", "123", "Минск", "111", "222", 1),
        Client("Петров", "456", "Брест", "333", "444", 2)
    ]
    
    writer = XMLWriter(str(file_path))
    writer.write(clients_to_save)
    
    reader = XMLReader(str(file_path))
    loaded = reader.read()
    
    assert len(loaded) == 2
    assert loaded[0].full_name == "Иванов"
    assert loaded[1].address == "Брест"