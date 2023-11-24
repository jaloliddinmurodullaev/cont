import json
import asyncio

from flight.additions.cache_operations import get_search_data
from flight.additions.cache_operations import get_single_offer

from flight.integrations import INTEGRATIONS
from flight.models import get_system_name

class BookingCollector:
    
    ''' A class that returns the rule of a ticket '''

    def __init__(self, data) -> None:
        self.passengers = data['passengers']
        self.request_id = data['request_id']
        self.offer_id   = data['offer_id']
        self.data       = data

    async def collector(self):
        
        try:
            offer = await get_single_offer(request_id=self.request_id, offer_id=self.offer_id)
        except Exception as e:
            return {
                'status': 'error',
                'request_id': self.request_id,
                'code': 502
            }

        if offer['status'] == 'success':
            offer = offer['offer_data']

            provider_id   = offer['provider_id']
            provider_name = offer['provider_name']
            system_id     = offer['system_id']

            auth_data = {
                'login'   : 'login',
                'password': 'passsword'
            }

            search_data = await get_search_data(request_id=self.request_id)
            search_data = json.loads(search_data)

            system_name = await asyncio.create_task(get_system_name(db_name='content', system_id=system_id))

            if system_name is not None and system_name in INTEGRATIONS:
                integration = INTEGRATIONS[system_name](auth_data, self.data)
                print(19919)
                print(integration)
                result = await integration.booking(system_id, provider_id, provider_name, self.request_id, self.offer_id, self.passengers, offer, search_data)

                return result
        else:
            result = {
                'status'    : 'error',
                'request_id': self.request_id,
                'code'      : 404
            }

        return result

