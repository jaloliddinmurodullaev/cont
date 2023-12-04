# External
import asyncio
import os
import copy
import aiohttp
import json

# Internal
from flight.models                      import insert_data
from flight.additions.additions         import filter_tickets
from flight.additions.cache_operations  import set_status
from flight.additions.cache_operations  import save_offers
from flight.additions.cache_operations  import update_offer
from flight.additions.integration       import BaseIntegration
from .converters.search_converter       import search_converter
from .converters.upsell_converter       import upsell_converter
from .converters.rules_converter        import rules_converter
from .converters.verify_converter       import verify_converter
from .converters.booking_converter      import booking_converter

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
            await save_offers(data=self.data, provider_id=provider_id, offers=result, request_id=request_id)
            
            # filtering only offers
            result['data'] = await filter_tickets(result['data'])

            # inserting data to a database for Business Intelligence
            asyncio.create_task(insert_data(system_id=system_id, provider_id=provider_id, provider_name=provider_name, offers=result))
            
            return result
        else:
            result = {
                'status' : res['status'], 
                'message': res['message'],
                'data'   : []
            } 
            await save_offers(data=self.data, provider_id=provider_id, offers=result, request_id=request_id)
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

    async def upsell(self, system_id, provider_id, provider_name, request_id, ticket, search_data): # data is data saved in the "other" field of an offer
        body = await asyncio.create_task(self.upsell_request_maker(ticket['other']))

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

        if res['status'] == 'success' and len(res['data']['availableFareList']) > 0:
            result['status'] = 'success'
            trip_routes_cnt = len(res['data']['availableFareList'][0]['legList'])
            search_data['directions'] = json.loads(search_data['directions'])
            result['data'] = await upsell_converter(res['data'], system_id, provider_id, provider_name, currency, trip_routes_cnt, search_data)
            await save_offers(data=search_data, provider_id=provider_id, offers=result, request_id=request_id)
            result['data'] = await filter_tickets(result['data'])
        else:
            result = {
                'status' : 'error',
                'message': 'no fares found'
            }

        return result
    
    async def upsell_request_maker(self, data): # data is data saved in the "other" field of an offer
        upsell = {
            "fareId": data['fareId'],
            "itineraryIdList": data['itineraryIdList']
        }
        return upsell

###################################### RULES  ######################################

    async def rules(self, system_id, provider_id, provider_name, request_id, ticket, search_data): # data is data saved in the "other" field of an offer
        dat    = ticket['other']
        routes = ticket['ticket']['routes']
        fares  = ticket['ticket']['fares_info']

        body = { 
            "fareId": dat['fareId']
        }

        context = json.dumps(body)

        self.loginkey = APIKEY
        self.passwordkey = PASSKEY

        res = await asyncio.create_task(self.__request("/api/v1/fare-rules", context))
        
        if 'fareRuleList' in res['data'] and len(res['data']['fareRuleList']) > 0:
            result = await rules_converter(res['data'], routes, fares)
        else:
            result = await rules_converter({}, routes, fares)
        
        response = {
            'status': 'success',
            'data': result
        }

        return response
    
###################################### VERIFY ######################################

    async def verify(self, system_id, provider_id, provider_name, request_id, offer_id, ticket, search_data):
        body = await asyncio.create_task(self.verify_request_maker(ticket['other']))

        context = json.dumps(body)

        self.loginkey = APIKEY
        self.passwordkey = PASSKEY 
        
        res = await asyncio.create_task(self.__request("/api/v1/verify-fare", context))

        result = {
            'status': None,
            'data': None
        }

        if res['status'] == 'success' and "fareId" in res['data']['fare']:
            resp = await verify_converter(request_id, offer_id, res['data']['fare']['fareId'])
            
            value = copy.deepcopy(ticket)
            value['other']['fareId'] = copy.deepcopy(resp['fare_id'])
            new_value = {
                'data': {
                    'ticket'       : value['ticket'],
                    'offer_id'     : value['offer_id'],
                    'other'        : value['other'],
                    'provider_id'  : value['provider_id'],
                    'provider_name': value['provider_name'],
                    'system_id'    : value['system_id']
                }
            }

            update_response = await update_offer(request_id, offer_id, new_value)

            if update_response['status'] == 'success':
                print('an offer has been successfully updated')
                result['status'] = 'success'
                result['data'] = resp
            else:
                result['status'] = 'error'
                result['data'] = {}
        else:
            result['status'] = 'error'
            result['data'] = {}
        
        return result
        

    async def verify_request_maker(self, data):
        verify = {
            "fareId": data['fareId'],
            "itineraryIdList": data['itineraryIdList']
        }
        return verify

##################################### BOOKING ######################################

    async def booking(self, system_id, provider_id, provider_name, request_id, offer_id, booking_data, ticket, search_data):
        body = await asyncio.create_task(self.booking_request_maker(ticket['other'], booking_data['passengers'], booking_data['agent']))

        context = json.dumps(body)

        self.loginkey = APIKEY
        self.passwordkey = PASSKEY 

        res = await asyncio.create_task(self.__request("/api/v1/create-booking", context))

        if res['status'] == 'success' and 'pnr' in res['data'] and "locator" in res['data']['pnr'] and res['data']['pnr']['locator'] != "":
            resp = await booking_converter(offer_id, res, ticket, search_data, booking_data['passengers'], booking_data['agent'])
            return resp
        else:
            result = {
                "request_id": request_id,
                "status": "error",
                "code": 405,
            } 
        
        return result

    async def booking_request_maker(self, data, passengers, agent): # data is data saved in the "other" field of an offer
        body = {
            "fareId": data['fareId'],
            "billingInformation": {
                "email": agent['email'],
                "city": agent['city'],
                "country": agent['country'],
                "street": agent['street'],
                "zipCode": agent['zip_code'],
                "lastName": agent['last_name'],
                "firstName": agent['first_name'],
                "phoneNumber": agent['phone_number']
            },
            "passengerList": []
        }

        ids = 0

        for passenger in passengers:
            title = "MR" if passenger['gender'] == 'M' else "MRS"
            ids += 1
            passenger_birth_date = passenger['birth_date'].split('-')
            passport_expiry_date = passenger['document']['expire_date'].split('-')
            date_of_birth = {
                "year": int(passenger_birth_date[0]),
                "month": int(passenger_birth_date[1]),
                "day": int(passenger_birth_date[2])
            }
            expire_date = {
                "year": int(passport_expiry_date[0]),
                "month": int(passport_expiry_date[1]),
                "day": int(passport_expiry_date[2])
            }
            passenger_tmp = {
                "id": ids,
                "passengerTypeCode": passenger['type'],
                "lastName": passenger['last_name'],
                "firstName": passenger['first_name'],
                "dateOfBirth": date_of_birth,
                "gender": "MALE" if passenger['gender'] == "M" else "FEMALE",
                "title": title,
                "travelDocument": {
                    "issuingCountry": {
                        "iso": passenger['citizenship']
                    },
                    "nationality": {
                        "iso": passenger['citizenship']
                    },
                    "number": passenger['document']['number'],
                    "expiration": expire_date,
                    "type": "PASSENGER_PASSPORT",
                    "dateOfBirth": date_of_birth
                },
                "operationalContactData": {
                    "emailAddressRefused": False,
                    "phoneNumberRefused": False,
                    "emailAddress": "d.razzakov@easybooking.uz",
                    "phoneNumber": "998662304400"
                }
            }
            body['passengerList'].append(passenger_tmp)

        return body
    
################################## CANCEL BOOKING ##################################

    async def cancel_booking(self, system_id, provider_id, provider_name, request_data, order_pnr):
        body = {
            'bookingData': {
                'locator': order_pnr
            },
            'forceCancellationOnExistingTickets': False
        }

        context = json.dumps(body)

        self.loginkey = APIKEY
        self.passwordkey = PASSKEY 

        res = await asyncio.create_task(self.__request("/api/v1/cancel-booking", context))
        print(res['data']['success'])
        print(res['status'])
        if res['status'] == 'success' and res['data']['success'] == True:
            response = {
                'status': 'success',
                'code'  : 100
            }
        else:
            response = {
                'status': 'error',
                'code'  : -100 
            }

        return response

#################################### TICKETING #####################################

    async def ticketing(self, system_id, provider_id, provider_name, request_data, order_pnr):
        body = {
            'bookingData': {
                'locator': order_pnr
            }
        }

        context = json.dumps(body)

        self.loginkey = APIKEY
        self.passwordkey = PASSKEY 

        res = await asyncio.create_task(self.__request("/api/v1/ticket-booking", context))
        print(res)
        if res['status'] == 'success' and res['data']['success'] == True:
            response = {
                'status': 'success',
                'code'  : 100
            }
        else:
            response = {
                'status': 'error',
                'code'  : -100 
            }

        return response


###################################### VOID ########################################

    async def void(self, system_id, provider_id, provider_name, request_data, order_pnr):
        body = {
            'bookingData': {
                'locator': order_pnr
            }
        }

        context = json.dumps(body)

        self.loginkey = APIKEY
        self.passwordkey = PASSKEY 

        res = await asyncio.create_task(self.__request("/api/v1/void-booking", context))
        
        if res['status'] == 'success' and res['success'] == True:
            response = {
                'status': 'success',
                'code'  : 100
            }
        else:
            response = {
                'status': 'error',
                'code'  : -100 
            }

        return response

#################################### REFUND ########################################

    async def refund(self):
        pass

#################################################################################### 