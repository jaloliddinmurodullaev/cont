
from flight.additions.cache_operations import check_status
from flight.additions.cache_operations import get_search_data
from flight.additions.cache_operations import get_single_offer

class UpsellCollector:

    ''' A class that routes search request according to provider id '''

    def __init__(self, data) -> None: # Constructor
        self.request_id = data['request_id']
        self.offer_id   = data['offer_id']

    async def collector(self): # Router 
        result = {
            "request_id": self.request_id,
            "status": None,
            "code": "",
            "trip_type": "",
            "currency": "USD",
            "offers": []
        }

        res = await get_single_offer(request_id=self.request_id, offer_id=self.offer_id)

        provider_id   = res['provider_id']
        provider_name = res['provider_name']
        system_id     = res['system_id'] 

        search_data = await get_search_data(request_id=self.request_id)

        if res['status'] == 'success':
            result['status'] = 'success'
            result['code'] = '100'
            result['trip_type'] = search_data['trip_type']
            result['offers'] = []
            return result   
        else:
            result['status'] = 'error'
            result['code'] = '404'
            return result 

