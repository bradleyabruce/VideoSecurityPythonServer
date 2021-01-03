from enum import Enum

class eTransactionType(Enum):
    Query = 1
    Update = 2
    Insert = 3
    Delete = 4
