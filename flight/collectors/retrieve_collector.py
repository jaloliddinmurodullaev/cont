import json
import copy
import asyncio

from flight.additions.cache_operations import get_search_data
from flight.additions.cache_operations import get_single_offer
from flight.additions.cache_operations import update_offer

from flight.integrations import INTEGRATIONS
from flight.models import get_system_name
from flight.models import get_order

class RetrieveCollector:
    
    ''' A class that returns the rule of a ticket '''

    def __init__(self, data) -> None:
        self.order_number = data['order_number']
        self.request_id = data['request_id']
        self.data       = data

    async def collector(self):
        
        try:
            print(self.order_number)
            order = await get_order(order_number=self.order_number)
        except Exception as e:
            return {
                'status'    : 'error',
                'request_id': self.request_id,
                'code'      : 502
            }

        if order is not None:
            result = {
                'status': 'success',
                'code'  : 100,
                'order' : order
            }
        else:
            result = {
                'status'    : 'error',
                'request_id': self.order_number,
                'code'      : -100
            }

        return result