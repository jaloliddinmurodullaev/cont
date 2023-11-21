import asyncio
import os
import aiohttp
import json

from flight.models import insert_data
from flight.additions.additions import filter_tickets
from flight.additions.cache_operations import set_status
from flight.additions.cache_operations import set_provider_response_to_cache
from flight.additions.integration import BaseIntegration

from .converters.search_converter import search_converter
from .converters.upsell_converter import upsell_converter

GATEWAY = os.environ.get('AerTicket_Base_URL')
APIKEY = os.environ.get('AerTicket_Login_Key')
PASSKEY = os.environ.get('AerTicket_Password_Key')

TTL = 3 * 60

CABIN_TYPES = {
    'economy' : 'ECONOMY',
    'business': 'BUSINESS'
}

class AerticketIntegration(BaseIntegration):
####################################### INIT #######################################

    def __init__(self, auth_data, data):
        self.loginkey      = auth_data.get('loginKey', None)
        self.passwordkey   = auth_data.get('passwordKey', None)
        self.gateway       = GATEWAY
        self.data          = data

    async def __request(self, endpoint, context, is_auth=True):
        response = {}
        header = {
            'login'   : self.loginkey,
            'password': self.passwordkey
        }
        if is_auth:
            res = await self.__send(self.gateway + endpoint, header, context)
            if res[0] in [200, 201]:
                response['status']  = 'success'
                response['message'] = 'could not get response from supplier'
                response['data']    = res[1]
            else:
                response['status']  = 'error'
                response['message'] = 'could not get response from supplier'
                response['data']    = res[1]
        else:
            pass

        return response
    
    async def __send(self, url, headers, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                status_code = response.status
                result = await response.json()
                return [status_code, result]
            
###################################### SEARCH ######################################
    
    async def search(self, system_id, provider_id, provider_name, request_id):
        data = await asyncio.create_task(self.search_request_maker())

        currency = {
            'curFrom': 'EUR',
            'curTo'  : 'USD'
        }

        context = json.dumps(data)

        res = await asyncio.create_task(self.__request("/api/v1/search", context))

        # res = json.load(open('/home/jalol/Code/responses/ow_adt1.json'))

        if res['status'] == 'success':
            asyncio.create_task(set_status(request_id=request_id))
            result = {
                'status' : res['status'],
                'message': res['message'],
                'data'   : await search_converter(res, provider_id, provider_name, system_id, currency, len(data['segmentList']))
            }
            # inserting data to cache
            await set_provider_response_to_cache(data=self.data, provider_id=provider_id, offers=result, request_id=request_id)
            
            # filtering only offers
            result['data'] = await filter_tickets(result['data'])

            # inserting data to a database for Business Intelligence
            asyncio.create_task(insert_data(system_id=system_id, provider_id=provider_id, provider_name=provider_name, offers=result))
            
            return result
        else:
            result = {
                'status' : res['status'], 
                'message': res['message']  
            } 
            return result
 
    async def search_request_maker(self):
        data = self.data
        directions = []
        paxes = []

        for dir in data['directions']:
            dep_date = dir['departure_date'].split('-')
            directions.append(
                {
                    "departure": {
                        "iata": dir['departure'],
                        "geoObjectType": "AIRPORT"
                    },
                    "destination": {
                        "iata": dir['arrival'],
                        "geoObjectType": "AIRPORT"
                    },
                    "departureDate": {
                        "year": int(dep_date[0]),
                        "month": int(dep_date[1]),
                        "day": int(dep_date[2])
                    }
                }
            )
        
        if data['adt'] > 0:
            paxes.append({
                "passengerTypeCode": "ADT",
			    "count": data['adt']
            })

        if data['chd'] > 0:
            paxes.append({
                "passengerTypeCode": "CHD",
			    "count": data['chd']
            })

        if data['inf'] > 0:
            paxes.append({
                "passengerTypeCode": "INF",
			    "count": data['inf']
            })

        if data['ins'] > 0:
            paxes.append({
                "passengerTypeCode": "INS",
			    "count": data['ins']
            })
        
        body = {
            "segmentList": directions,
            "requestPassengerTypeList": paxes,
            "searchOptions": {
                "cabinClassList": [
                    CABIN_TYPES[data['class']]
                ]
            }
        }
        
        return body

###################################### UPSELL ######################################

    async def upsell(self, system_id, provider_id, provider_name, request_id, data, search_data):
        body = await asyncio.create_task(self.upsell_request_maker(data))

        context = json.dumps(body)

        self.loginkey = APIKEY
        self.passwordkey = PASSKEY

        currency = {
            'curFrom': 'EUR',
            'curTo'  : 'USD'
        } 
        
        res = await asyncio.create_task(self.__request("/api/v1/search-upsell", context))

        result = {
            'status': None,
            'data': None
        }

        if res['status'] == 'success':
            asyncio.create_task(set_status(request_id=request_id))

            trip_routes_cnt = len(res['data']['availableFareList'][0]['legList'])

            # a line below should be applied yet
            # await set_provider_response_to_cache(data=self.data, provider_id=provider_id, offers=result, request_id=request_id)
            resp = await upsell_converter(res['data'], system_id, provider_id, provider_name, currency, trip_routes_cnt, search_data)
            resp = await filter_tickets(resp)

            result = {
                'status': res['status'],
                'data'  : resp
            }
        else:
            result = {
                'status' : res['status'],
                'message': res['message']
            }

        return result
    
    async def upsell_request_maker(self, data):
        upsell = {
            "fareId": data['fareId'],
            "itineraryIdList": data['itineraryIdList']
        }
        return upsell

###################################### RULES  ######################################

    async def rules(self):
        pass

###################################### BOOKING #####################################

    async def booking(self):
        pass

################################## CANCEL BOOKING ##################################

    async def cancel_booking(self):
        pass

################################### SPLIT BOOKING ##################################

    async def split_booking(self):
        pass

#################################### TICKETING #####################################

    async def ticketing(self):
        pass

###################################### VOID ########################################

    async def void(self):
        pass

#################################### REFUND ########################################

    async def refund(self):
        pass

#################################################################################### 