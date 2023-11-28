import json
import asyncio

from flight.additions.cache_operations import get_search_data
from flight.additions.cache_operations import get_single_offer

from flight.integrations import INTEGRATIONS
from flight.models import get_system_name

class RefundCollector:
    
    ''' A class that returns the rule of a ticket '''

    def __init__(self, data) -> None:
        self.order_number = data['order_number']
        self.payment_type = data['payment_type']
        self.data       = data

    async def collector(self):
        pass