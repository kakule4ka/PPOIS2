class Client:
    def __init__(self, full_name, account_number, address, mobile_phone, home_phone, client_id=None):
        self.client_id = client_id
        self.full_name = full_name
        self.account_number = account_number
        self.address = address
        self.mobile_phone = mobile_phone
        self.home_phone = home_phone