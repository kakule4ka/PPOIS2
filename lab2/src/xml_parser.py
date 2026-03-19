import xml.dom.minidom
import xml.sax
from client import Client

class XMLWriter:
    def __init__(self, filename):
        self.filename = filename

    def write(self, clients):
        doc = xml.dom.minidom.Document()
        root = doc.createElement('clients')
        doc.appendChild(root)

        for client in clients:
            client_elem = doc.createElement('client')
            
            for key, value in client.__dict__.items():
                if key == 'client_id':
                    continue
                elem = doc.createElement(key)
                text = doc.createTextNode(str(value) if value else "")
                elem.appendChild(text)
                client_elem.appendChild(elem)
            
            root.appendChild(client_elem)

        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(doc.toprettyxml(indent="  "))


class ClientHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.clients = []
        self.current_data = ""
        self.client_data = {}

    def startElement(self, tag, attributes):
        self.current_data = tag
        if tag == "client":
            self.client_data = {}

    def characters(self, content):
        if self.current_data:
            text = content.strip()
            if text:
                self.client_data[self.current_data] = self.client_data.get(self.current_data, "") + text

    def endElement(self, tag):
        if tag == "client":
            client = Client(
                full_name=self.client_data.get('full_name', ''),
                account_number=self.client_data.get('account_number', ''),
                address=self.client_data.get('address', ''),
                mobile_phone=self.client_data.get('mobile_phone', ''),
                home_phone=self.client_data.get('home_phone', '')
            )
            self.clients.append(client)
        self.current_data = ""


class XMLReader:
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        handler = ClientHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(self.filename)
        return handler.clients