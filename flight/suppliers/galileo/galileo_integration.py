import asyncio
import os
import aiohttp
import datetime
import uuid
import json
from jinja2 import Environment, FileSystemLoader

from flight.models import insert_data
from flight.additions.cache_operations import set_status, set_provider_response_to_cache

HERE = os.path.dirname(os.path.abspath(__file__))

TEST_GATEWAY = os.environ.get("TEST_GATEWAY_TRAVELPORT")
USERNAME = os.environ.get("USERNAME_TRAVELPORT")
PASSWORD = os.environ.get("USERNAME_PASSWORD")

TTL = 3 * 60

CABIN_TYPES = {
    'economy' : 'Economy',
    'business': 'Business'
}

class GalileoIntegration:

########################################### DEFAULT ############################################

    def __init__(self, auth_data, data):
        self.login = auth_data.get('login', None)
        self.password = auth_data.get('password', None)
        self.gateway = TEST_GATEWAY
        self.data = data

    async def __request(self, endpoint, context):
        return self.gateway
    
    async def __send(self, url, headers, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers, ssl=self.verify_ssl) as response:
                status_code = response.status
                result = await response.text()
                return [status_code, result]

########################################### AUTH ###############################################

    async def auth(self):
        context = {
            "login": self.login,
            "password": self.password,
            "structure_unit_id": self.structure_unit_id,
        }
        res = await asyncio.create_task(self.__request("catalog/search/catalogproductofferings", context))

        token = None
        if res['status'] == 'success' and 'Token' in res['data']['Body']['AppData']['Auth:AuthResponse']:
            token = res['data']['Body']['AppData']['Auth:AuthResponse']['Token']
            self.token = token
        return token 

########################################### SEARCH #############################################

    # method name 
    async def search(self, system_id, provider_id, provider_name, request_id):
        data = await asyncio.create_task(self.search_request_maker())
        itinerary = data['itinerary']
        paxes     = data['paxes']

        currency = {
            'curFrom': 'UZS',
            'curTo'  : 'USD'
        }

        context = data
        res = await asyncio.create_task(self.__request("catalog/search/catalogproductofferings", context))

        if res['status'] == 'success':
            asyncio.create_task(set_status(request_id=request_id))
            result = {
                'status' : res['status'], 
                'message': res['message'],
                'data'   : (res['data'], provider_id, provider_name, currency, len(itinerary) == 1, request_id)
            }

            # inserting data to cache
            asyncio.create_task(set_provider_response_to_cache(data=self.data, provider_id=provider_id, offer=result, request_id=request_id))

            # inserting data to a database for Business Intelligence
            asyncio.create_task(insert_data(system_id=system_id, provider_id=provider_id, provider_name=provider_name, offers=result))
            
            return json.dumps(result)
        else:
            result = {
                'status' : res['status'], 
                'message': res['message'],
                'data'   : res['data']
            }
            return result
 
    async def search_request_maker(self):
        data = self.data
        directions = []
        paxes = []

        for dir in data['directions']:
            directions.append(
                {
                    "origin": dir['departure_airport'],
                    "destination": dir['arrival_airport'],
                    "departure": dir['departure_date'],
                    "cabin": CABIN_TYPES[data['class']]
                }
            )
        pax = 0
        for _ in range(data['adt']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "ADT"
            })
            pax += 1

        for _ in range(data['chd']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "CNN"
            })
            pax += 1

        for _ in range(data['inf']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "INF"
            })
            pax += 1

        for _ in range(data['ins']):
            paxes.append({
                "pax_id": f"PAX-{pax+1}",
                "ptc": "INS"
            })
            pax += 1
        
        body = {
            'itinerary': directions,
            'paxes': paxes
        }
        
        return body

########################################### UPSELL #############################################

    async def upsell(self):
        pass

########################################### RULES ##############################################

    async def rules(self):
        pass

########################################### BOOKING ############################################

    async def booking(self):
        pass

########################################### CANCEL #############################################

    async def cancel(self):
        pass

########################################### TICKET #############################################

    async def ticketing(self):
        pass

###################################### ADDITIONAL METHODS ######################################

