from enum import Enum
class OrderStatus(Enum):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    DELIVERED = 'DELIVERED'