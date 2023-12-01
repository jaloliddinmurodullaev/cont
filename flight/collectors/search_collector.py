import random
import asyncio
import uuid

from flight.additions.cache_operations import check_status
from flight.additions.cache_operations import check_search_existance
from flight.additions.cache_operations import set_search_data
from flight.additions.cache_operations import check_if_direction_was_searched
from flight.models import get_system_name

from flight.integrations import INTEGRATIONS


CABIN_TYPES = {
    'economy' : 'Economy',
    'business': 'Business'
}

class SearchCollector:

    ''' A class that routes search request according to provider id '''

    def __init__(self, data) -> None: # Constructor
        self.request_id = None
        self.data = data

    async def collector(self): # Router
        trip_type = "RT" if len(self.data.get('directions')) == 2 else ("OW" if len(self.data.get('directions')) == 1 else "MC")
        self.request_id = str(uuid.uuid1())
        
        result = {
            "code": "100",
            "status": None,
            "request_id": None,
        }

        request_check = await asyncio.create_task(check_if_direction_was_searched(data=self.data, request_id=self.request_id))
        if request_check['has']:
            result["request_id"] = request_check['request_id']
            result["status"] = "success"

            for provider in self.data.get('providers'):
                offers = await asyncio.create_task(check_search_existance(provider_id=provider['provider_id'], data=self.data, request_id=request_check['request_id']))
                if offers:
                    result['status'] = 'error'
                    result['code'] = "404"
            
            return result
        
        await asyncio.create_task(set_search_data(data=self.data, request_id=self.request_id, trip_type=trip_type, currency="USD"))
        
        result['request_id'] = self.request_id

        providerList = []
        for provider in self.data.get('providers'):
            offers = await asyncio.create_task(check_search_existance(provider_id=provider['provider_id'], data=self.data, request_id=self.request_id))
            
            if not offers:
                system_name = await asyncio.create_task(get_system_name(system_id=provider['system_id']))
                if system_name is not None and system_name in INTEGRATIONS:
                    integration = INTEGRATIONS[system_name](provider['auth_data'], self.data)
                    data = {
                        'integration'  : integration,
                        'provider_id'  : provider['provider_id'],
                        'provider_name': provider['provider_name'],
                        'system_id'    : provider['system_id']
                    }
                    providerList.append(data)
                else:
                    result['code'] = "404"
            
        try:
            search_response = await asyncio.gather(*[task['integration'].search(task['system_id'], task['provider_id'], task['provider_name'], self.request_id) for task in providerList])
            cnt_404 = 0
            for srd in search_response:
                if len(srd['data']) == 0:
                    cnt_404 += 1
            if cnt_404 == len(search_response):
                result['code'] = '404'
        except Exception as e:
            result['code'] = "404"
            raise e

        result['status'] = await asyncio.create_task(check_status(request_id=self.request_id))
        
        return result

