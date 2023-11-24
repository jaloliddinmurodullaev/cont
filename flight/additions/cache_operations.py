import os
import redis
import json

from flight.additions.additions import filter_tickets

HOST = os.environ.get('CACHE_HOST')
PORT = os.environ.get('CACHE_PORT')

# minutes for caching offers
MINUTES = 10

async def save_offers(data, provider_id, offers, request_id):
    
    ''' A function that saves provider search response in cache for 3 minutes '''
    
    directions = ""

    for direction in data['directions']:
        directions = directions + f"{direction['departure']}{direction['arrival']}_{direction['departure_date']}_"

    key = f"{request_id}_{provider_id}_{directions}ADT{data.get('adt')}_CHD{data.get('chd')}_INF{data.get('inf')}_INS{data.get('ins')}_FLEX{data.get('flexible')}_{data.get('class')}"

    results = {
        'data': {
            'ticket'       : None,
            'offer_id'     : None,
            'other'        : None,
            'provider_id'  : None,
            'provider_name': None,
            'system_id'    : None
        },
    }

    for offer in offers['data']:
        results['data']['provider_name'] = offer.provider_name
        results['data']['provider_id']   = offer.provider_id
        results['data']['system_id']     = offer.system_id
        results['data']['offer_id']      = offer.offer_id
        results['data']['ticket']        = offer.ticket
        results['data']['other']         = offer.other

        # print(key + "_" + str(offer.offer_id))

        redis_client = redis.Redis(host=HOST, port=PORT)
        redis_client.set(
            key + "_" + str(offer.offer_id), 
            json.dumps(results), 
            MINUTES*60  
        )
        redis_client.close()
    

async def get_offers(request_id): # Cache operation

        ''' A function that checks if given data is in cache '''

        redis_client = redis.Redis(host=HOST, port=PORT)

        keys = redis_client.keys(f"{request_id}_*")
        offers = [json.loads(redis_client.get(key)) for key in keys]

        redis_client.close()

        return offers


async def get_single_offer(request_id, offer_id):
    
    ''' getting single offer'''

    redis_client = redis.Redis(host=HOST, port=PORT)

    partial_key = f"{request_id}_*_{offer_id}"
    key = redis_client.keys(partial_key)[0].decode('utf-8')

    offer = redis_client.get(key)

    offer = json.loads(offer)
    
    redis_client.close()

    if offer != None:
        result = {
            'status': 'success',
            'offer_data': offer['data']
        }
        return result
    else:
        result = {
            'status': 'error',
            'message': 'offer_id not found'
        }
        return result


async def update_offer(request_id, offer_id, value):

    ''' updating an offer'''

    redis_client = redis.Redis(host=HOST, port=PORT)

    try:
        partial_key = f"{request_id}_*_{offer_id}"
        key = redis_client.keys(partial_key)[0].decode('utf-8')
        
        redis_client.set(
                key,
                json.dumps(value), 
                MINUTES*60  
            )

        result = {
            'status': 'success',
            'message': 'an offer has been cached'
        }
    except Exception as e:
        result = {
            'status': 'error',
            'message': str(e)
        }

    redis_client.close()

    return result


async def set_search_data(data, request_id, trip_type, currency): # Cache operation
        data = data
        redis_client = redis.Redis(host=HOST, port=PORT)
        redis_client.set(
            f"search_{request_id}",
            json.dumps({
                "request_id": request_id,
                "adt"       : data.get('adt'),
                "chd"       : data.get('chd'),
                "inf"       : data.get('inf'),
                "ins"       : data.get('ins'),
                "clas"      : data.get('class'),
                "direct"    : data.get('direct'),
                "flexible"  : data.get('flexible'),
                "trip_type" : trip_type,
                "currency"  : currency,
                "directions": json.dumps(data.get('directions')),
            }),
            1200
        )
        redis_client.close()


async def get_search_data(request_id): # Cache operation

        ''' A function that checks if given data is in cache '''

        key = f"search_{request_id}"

        redis_client = redis.Redis(host=HOST, port=PORT)
        search_data = redis_client.get(key)
        redis_client.close()

        return search_data


async def check_search_existance(data, provider_id, request_id): # Cache operation

        ''' A function that checks if given data is in cache '''

        directions = ""

        for direction in data['directions']:
            directions = directions + f"{direction['departure']}{direction['arrival']}_{direction['departure_date']}_"

        key = f"{request_id}_{provider_id}_{directions}ADT{data.get('adt')}_CHD{data.get('chd')}_INF{data.get('inf')}_INS{data.get('ins')}_FLEX{data.get('flexible')}_{data.get('class')}_*"
        
        redis_client = redis.Redis(host=HOST, port=PORT)
        offers = redis_client.get(key)
        print(type(offers))
        redis_client.close()
        return offers


async def check_if_direction_was_searched(data, request_id): # Cache operation
        key = ""
        for direc in data['directions']:
            key += f"{direc['departure']}{direc['arrival']}{direc['departure_date']}"
        key += f"{data['adt']}{data['chd']}{data['inf']}{data['ins']}{data['class']}{data['flexible']}{data['direct']}"
        for provider in data['providers']:
            key += f"{provider['provider_id']}_{provider['system_id']}"

        redis_client = redis.Redis(host=HOST, port=PORT)
        response = []
        redis_response = redis_client.get(key)
        if redis_response == None:
            redis_client.set(
                key,
                json.dumps({
                    'request_id': request_id
                }),
                180
            )
            response = {
                'has': False,
                'request_id': 0
            }
        else:
            res = json.loads(redis_response)
            response = {
                'has': True,
                'request_id': res['request_id']
            }

        redis_client.close()

        return response


async def set_status(request_id):
    redis_client = redis.Redis(host=HOST, port=PORT)
    status = redis_client.get(f"status_{request_id}")
    val = 1

    if status != None:
        loaded_status = json.loads(status)
        val = loaded_status['status'] + 1

    redis_client.set(
        f"status_{request_id}",
        json.dumps({
            "status": val,
        }),
        1200
    )
    redis_client.close()


async def check_status(request_id):
    redis_client = redis.Redis(host=HOST, port=PORT)
    status = redis_client.get(f"status_{request_id}")
    if status != None:
        status = json.loads(status)
        ans = 'success' if status.get('status', 0) > 0 else 'error'
    else:
        ans = 'error'
    redis_client.close()
    return ans

