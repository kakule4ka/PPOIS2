from enum import Enum

class ConditionType(Enum):
    PHONE_OR_LASTNAME = 1
    ACCOUNT_OR_ADDRESS = 2
    FULLNAME_AND_DIGITS = 3

DEFAULT_PAGE_SIZE = 10