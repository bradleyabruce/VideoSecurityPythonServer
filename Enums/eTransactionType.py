from enum import Enum


class eTransactionType(Enum):
    SimpleQuery = 1
    Update = 2
    Insert = 3
    Delete = 4
    MultiSelectQuery = 5
