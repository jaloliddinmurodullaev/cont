import json
import asyncio

from flight.additions.cache_operations import get_search_data
from flight.additions.cache_operations import get_single_offer

from flight.integrations import INTEGRATIONS
from flight.models import get_system_name

class BookingCollector:
    
    ''' A class that returns the rule of a ticket '''

    def __init__(self, data) -> None:
        self.request_id = data['request_id']
        self.offer_id   = data['offer_id']
        self.data       = data

    async def collector(self):
        pass