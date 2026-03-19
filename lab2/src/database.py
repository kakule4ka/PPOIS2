import sqlite3
import os

class Database:
    def __init__(self, db_path="data/clients.db"):
        self.db_path = db_path
        self.clean_sql = "REPLACE(REPLACE(REPLACE(REPLACE(REPLACE({}, ' ', ''), '(', ''), ')', ''), '-', ''), '+', '')"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    address TEXT NOT NULL,
                    mobile_phone TEXT,
                    home_phone TEXT
                )
            ''')
            conn.commit()

    def _format_phone_search(self, phone):
        cleaned = ''.join(filter(str.isdigit, phone))
        return f'%{cleaned}%'

    def add_client(self, client):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO clients (full_name, account_number, address, mobile_phone, home_phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (client.full_name, client.account_number, client.address, client.mobile_phone, client.home_phone))
            conn.commit()

    def get_clients_paginated(self, limit, offset):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients LIMIT ? OFFSET ?', (limit, offset))
            return cursor.fetchall()

    def get_total_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM clients')
            return cursor.fetchone()[0]

    def search_condition_1(self, phone, last_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM clients WHERE "
            conditions = []
            params = []
            
            if phone:
                phone_like = self._format_phone_search(phone)
                m_clean = self.clean_sql.format("mobile_phone")
                h_clean = self.clean_sql.format("home_phone")
                conditions.append(f"({m_clean} LIKE ? OR {h_clean} LIKE ?)")
                params.extend([phone_like, phone_like])
                
            if last_name:
                conditions.append("full_name LIKE ?")
                params.append(f'%{last_name}%')
                
            if not conditions:
                return []
                
            query += " OR ".join(conditions)
            cursor.execute(query, params)
            return cursor.fetchall()

    def search_condition_2(self, account, address):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM clients WHERE "
            conditions = []
            params = []
            
            if account:
                conditions.append("account_number LIKE ?")
                params.append(f'%{account}%')
                
            if address:
                conditions.append("address LIKE ?")
                params.append(f'%{address}%')
                
            if not conditions:
                return []
                
            query += " OR ".join(conditions)
            cursor.execute(query, params)
            return cursor.fetchall()

    def search_condition_3(self, name_part, digits):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM clients WHERE "
            conditions = []
            params = []
            
            if name_part:
                conditions.append("full_name LIKE ?")
                params.append(f'%{name_part}%')
                
            if digits:
                phone_like = self._format_phone_search(digits)
                m_clean = self.clean_sql.format("mobile_phone")
                h_clean = self.clean_sql.format("home_phone")
                conditions.append(f"({m_clean} LIKE ? OR {h_clean} LIKE ?)")
                params.extend([phone_like, phone_like])
                
            if not conditions:
                return []
                
            query += " AND ".join(conditions)
            cursor.execute(query, params)
            return cursor.fetchall()

    def delete_condition_1(self, phone, last_name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "DELETE FROM clients WHERE "
            conditions = []
            params = []
            
            if phone:
                phone_like = self._format_phone_search(phone)
                m_clean = self.clean_sql.format("mobile_phone")
                h_clean = self.clean_sql.format("home_phone")
                conditions.append(f"({m_clean} LIKE ? OR {h_clean} LIKE ?)")
                params.extend([phone_like, phone_like])
                
            if last_name:
                conditions.append("full_name LIKE ?")
                params.append(f'%{last_name}%')
                
            if not conditions:
                return 0
                
            query += " OR ".join(conditions)
            cursor.execute(query, params)
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def delete_condition_2(self, account, address):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "DELETE FROM clients WHERE "
            conditions = []
            params = []
            
            if account:
                conditions.append("account_number LIKE ?")
                params.append(f'%{account}%')
                
            if address:
                conditions.append("address LIKE ?")
                params.append(f'%{address}%')
                
            if not conditions:
                return 0
                
            query += " OR ".join(conditions)
            cursor.execute(query, params)
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def delete_condition_3(self, name_part, digits):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "DELETE FROM clients WHERE "
            conditions = []
            params = []
            
            if name_part:
                conditions.append("full_name LIKE ?")
                params.append(f'%{name_part}%')
                
            if digits:
                phone_like = self._format_phone_search(digits)
                m_clean = self.clean_sql.format("mobile_phone")
                h_clean = self.clean_sql.format("home_phone")
                conditions.append(f"({m_clean} LIKE ? OR {h_clean} LIKE ?)")
                params.extend([phone_like, phone_like])
                
            if not conditions:
                return 0
                
            query += " AND ".join(conditions)
            cursor.execute(query, params)
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM clients')
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='clients'")
            conn.commit()
        
    def close(self):
        pass