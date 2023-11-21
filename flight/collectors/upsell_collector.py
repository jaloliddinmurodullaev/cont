import json
import asyncio

from flight.additions.cache_operations import get_search_data
from flight.additions.cache_operations import get_single_offer

from flight.integrations import INTEGRATIONS
from flight.models import get_system_name

class UpsellCollector:

    ''' A class that routes search request according to provider id '''

    def __init__(self, data) -> None: # Constructor
        self.request_id = data['request_id']
        self.offer_id   = data['offer_id']
        self.data       = data

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

        if res['status'] == 'success':
            res = res['offer_data']

            provider_id   = res['provider_id']
            provider_name = res['provider_name']
            system_id     = res['system_id'] 

            auth_data = {
                'login': 'login',
                'password': 'passsword'
            }

            # provider credentials should be taken from provider api

            # print(provider_id, provider_name, system_id)

            search_data = await get_search_data(request_id=self.request_id)
            search_data = json.loads(search_data)

            system_name = await asyncio.create_task(get_system_name(db_name='content', system_id=system_id))

            if system_name is not None and system_name in INTEGRATIONS:
                integration = INTEGRATIONS[system_name](auth_data, self.data)
                response = await integration.upsell(system_id, provider_id, provider_name, self.request_id, res['other'], search_data)

                if response['status'] == 'success':
                    result['status'] = 'success'
                    result['code'] = '100'
                    result['trip_type'] = search_data['trip_type']
                    result['offers'] = response['data']
                else:
                    print('gds couldnt respond')
                    result['status'] = 'error'
                    result['code'] = '404'

                
            else:
                print('integration not found')
                result['status'] = 'error'
                result['code'] = '404'
            return result   
        else:
            result['status'] = 'error'
            result['code'] = '404'
            return result 

