import json
import asyncio

from flight.additions.cache_operations import check_status
from flight.additions.cache_operations import check_offers_existance, get_search_data

class OfferCollector:
    
    def __init__(self, data: dict) -> None: # Constructor
        self.request_id = data.get('request_id', None)
        self.next_token = data.get('next_token', None)
        self.limit      = data.get('limit', None)
        self.sort_type  = data.get('sort_type', None)
        self.currency   = data.get('currency', None)

    async def collector(self): # Router
        result = {
            "request_id": None,
            "status": None,
            "code": "",
            "trip_type": "",
            "sort_type": "",
            "currency": "USD",
            "count": 0,
            "next_token": None,
            "offers": []
        }

        search_data = await asyncio.create_task(get_search_data(request_id=self.request_id))

        if search_data != None:
            search_data = json.loads(search_data)
            result['status']     = await asyncio.create_task(check_status(request_id=self.request_id))
            result['request_id'] = self.request_id
            result['trip_type']  = search_data['trip_type']
            result['currency']   = search_data['currency']
            result['sort_type']  = self.sort_type

            offers = await asyncio.create_task(check_offers_existance(request_id=self.request_id))
            if offers: 
                result['offers'] = offers
                result['code'] = 100
            else:
                result['status'] = 'error'
                result['code'] = 404           
        else:
            result['status'] = 'error'
            result['code'] = 404

        if self.sort_type == 'price':
            result['offers'] = await asyncio.create_task(self.sort_by_price(offers))

        result['count'] = len(result['offers'])

        if self.limit != None:
            result['offers'] = result['offers'][:10]
        
        if self.currency != None:
            pass

        return result
    
    async def sort_by_price(self, offers):
        return sorted(offers, key=lambda offer: offer["price_info"]["price"])
    
    async def currency_converter(self, offers, currFrom, currTo):
        pass
