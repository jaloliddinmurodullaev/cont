import asyncio
import os
import aiohttp
import json

from flight.models import insert_data
from flight.additions.additions import filter_tickets
from flight.additions.cache_operations import set_status, set_provider_response_to_cache

from .converters.search_converter import search_converter

HERE = os.path.dirname(os.path.abspath(__file__))

GATEWAY = os.environ.get('TRAVELPORT_TEST_GATEWAY')
AUTH_GATEWAY = os.environ.get('TRAVELPORT_TEST_AUTH_GATEWAY')

TTL = 3 * 60

CABIN_TYPES = {
    'economy' : 'Economy',
    'business': 'Business'
}

class GalileoIntegration:

########################################### CONFIG ############################################

    def __init__(self, auth_data, data):
        self.username      = auth_data.get('login', None)
        self.password      = auth_data.get('password', None)
        self.client_id     = auth_data.get('client_id', None)
        self.client_secret = auth_data.get('client_secret', None)
        self.token         = ""
        self.gateway       = GATEWAY
        self.auth_gateway  = AUTH_GATEWAY
        self.data          = data

    async def __request(self, endpoint, context, is_auth=False):
        response = {}

        if is_auth:
            res = self.__send(self.auth_gateway, None, context)
            if res[0] in [200, 201]:
                response['status'] = 'success'
                response['data']   = res[1]
            else:
                response['status'] = 'error'
                response['data']   = res[1]
        else:
            pass

        return response
    
    async def __send(self, url, headers, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                status_code = response.status
                result = await response.json()
                return [status_code, result]

########################################### AUTH ##############################################

    async def auth(self):
        context = {
            "username": self.username,
            "password": self.password,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        res = await asyncio.create_task(self.__request(endpoint="", context=context, is_auth=True))

        token = None
        if res['status'] == 'success' and 'Token' in res['data']['Body']['AppData']['Auth:AuthResponse']:
            token = res['data']['Body']['AppData']['Auth:AuthResponse']['Token']
            self.token = token
        return token

########################################### SEARCH #############################################

    # method name 
    async def search(self, system_id, provider_id, provider_name, request_id):
        data = await asyncio.create_task(self.search_request_maker())
        itinerary = data['CatalogProductOfferingsQueryRequest']['CatalogProductOfferingsRequest']['SearchCriteriaFlight']

        currency = {
            'curFrom': 'UZS',
            'curTo'  : 'USD'
        }

        context = data
        print(context)
        res = await asyncio.create_task(self.__request("catalog/search/catalogproductofferings", context))

        if res['status'] == 'success':
            asyncio.create_task(set_status(request_id=request_id))
            result = {
                'status' : res['status'], 
                'message': res['message'],
                'data'   : asyncio.create_task(search_converter(res['data'], provider_id, provider_name, currency, len(itinerary), request_id))
            }
            result['data'] = asyncio.create_task(filter_tickets(result['data']))
            
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
                    "@type": "SearchCriteriaFlight",
                    "departureDate": dir['departure_date'],
                    "From": {
                        "value": dir['departure_airport'],
                    },
                    "To": {
                        "value": dir['arrival_airport']
                    }
                }
            )
        
        if data['adt'] > 0:
            paxes.append({
                "@type": "PassengerCriteria",
                "number": data['adt'],
                "passengerTypeCode": "ADT"
            })

        if data['chd'] > 0:
            paxes.append({
                "@type": "PassengerCriteria",
                "number": data['chd'],
                "passengerTypeCode": "CNN"
            })

        if data['inf'] > 0:
            paxes.append({
                "@type": "PassengerCriteria",
                "number": data['inf'],
                "passengerTypeCode": "INF"
            })

        if data['ins'] > 0:
            paxes.append({
                "@type": "PassengerCriteria",
                "number": data['ins'],
                "passengerTypeCode": "INS"
            })
        
        body = {
            'CatalogProductOfferingsQueryRequest': {
                "@type": "CatalogProductOfferingsQueryRequest",
                "CatalogProductOfferingsRequest": {
                    "@type": "CatalogProductOfferingsRequestAir",
                    "contentSourceList": [
                        "GDS",
                        "NDC"
                    ],
                    "PassengerCriteria": paxes,
                    "SearchCriteriaFlight": directions,
                    "CustomResponseModifiersAir": {
                        "@type": "CustomResponseModifiersAir",
                        "SearchRepresentation": "Journey",
                        "includeFareCalculationInd": True,
                    },
                    "SearchModifiersAir" : {
                        "CabinPreference" : [ 
                            {
                                "@type" : "CabinPreference",
                                "preferenceType": "Preferred",
                                "cabins" : [CABIN_TYPES[data['class']]], 
                            }
                        ]
                    }
                }
            }
        }
        
        return body

########################################### UPSELL #############################################

    async def upsell(self):
        pass

############################################ RULES #############################################

    async def rules(self):
        pass

########################################### BOOKING ############################################

    async def booking(self):
        pass

############################################ CANCEL ############################################

    async def cancel(self):
        pass

############################################ TICKET ############################################

    async def ticketing(self):
        pass

###################################### ADDITIONAL METHODS ######################################

