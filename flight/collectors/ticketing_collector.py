import json
import asyncio

from flight.integrations import INTEGRATIONS

from flight.models import get_system_name
from flight.models import update_order
from flight.models import get_order

class TicketingCollector:
    
    ''' A class that returns the rule of a ticket '''

    def __init__(self, data) -> None:
        self.order_number = data['order_number']
        self.payment_type = data['payment_method']
        self.data         = data
        self.TICKET       = 'T'

    async def collector(self):
        try:
            print(self.order_number)
            order = await get_order(order_number=self.order_number)
        except Exception as e:
            return {
                'status'      : 'error',
                'order_number': self.order_number,
                'code'        : -100
            }
        
        if order is not None:
            provider_id   = order['provider_uid']
            provider_name = order['provider_name']
            system_id     = order['booking_system']

            auth_data = {
                'login'   : 'login',
                'password': 'password'
            }

            system_name = await asyncio.create_task(get_system_name(system_id=system_id))

            if system_name is not None and system_name in INTEGRATIONS:
                integration = INTEGRATIONS[system_name](auth_data, self.data)
                result = await integration.ticketing(system_id, provider_id, provider_name, self.data, order)

                if result['status'] == 'success':
                    await update_order(order_number=self.order_number, order_status_code=self.TICKET)
                    ticketed_offer = await get_order(self.order_number)
                    result = {
                        'status': 'success',
                        'code'  : 100,
                        'order' : ticketed_offer
                    }

        else:
            result = {
                'status': 'error',
                'code'  : -100
            }

        return result