from database import Database
from xml_parser import XMLReader, XMLWriter
from client import Client
from constants import ConditionType, DEFAULT_PAGE_SIZE

class Controller:
    def __init__(self, db_path="data/clients.db"):
        self.db = Database(db_path)
        self.page_size = DEFAULT_PAGE_SIZE
        self.current_page = 1
        self.total_records = 0
        self.total_pages = 1

    def update_pagination_info(self):
        self.total_records = self.db.get_total_count()
        self.total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.total_pages == 0:
            self.total_pages = 1
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages

    def get_current_page_data(self):
        self.update_pagination_info()
        offset = (self.current_page - 1) * self.page_size
        return self.db.get_clients_paginated(self.page_size, offset)

    def set_page_size(self, size):
        self.page_size = size
        self.current_page = 1

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1

    def first_page(self):
        self.current_page = 1

    def last_page(self):
        self.current_page = self.total_pages

    def add_client(self, full_name, account_number, address, mobile_phone, home_phone):
        client = Client(full_name, account_number, address, mobile_phone, home_phone)
        self.db.add_client(client)

    def search_clients(self, condition_type, param1, param2):
        if condition_type == ConditionType.PHONE_OR_LASTNAME:
            return self.db.search_condition_1(param1, param2)
        elif condition_type == ConditionType.ACCOUNT_OR_ADDRESS:
            return self.db.search_condition_2(param1, param2)
        elif condition_type == ConditionType.FULLNAME_AND_DIGITS:
            return self.db.search_condition_3(param1, param2)
        return []

    def delete_clients(self, condition_type, param1, param2):
        if condition_type == ConditionType.PHONE_OR_LASTNAME:
            return self.db.delete_condition_1(param1, param2)
        elif condition_type == ConditionType.ACCOUNT_OR_ADDRESS:
            return self.db.delete_condition_2(param1, param2)
        elif condition_type == ConditionType.FULLNAME_AND_DIGITS:
            return self.db.delete_condition_3(param1, param2)
        return 0

    def load_from_xml(self, filepath):
        reader = XMLReader(filepath)
        clients = reader.read()
        for client in clients:
            self.db.add_client(client)

    def save_to_xml(self, filepath):
        self.update_pagination_info()
        all_clients_data = self.db.get_clients_paginated(self.total_records, 0)
        clients = []
        for row in all_clients_data:
            client = Client(row[1], row[2], row[3], row[4], row[5], row[0])
            clients.append(client)
        writer = XMLWriter(filepath)
        writer.write(clients)

    def clear_all(self):
        self.db.clear_all()
        self.current_page = 1