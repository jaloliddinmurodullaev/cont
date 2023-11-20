import os
import redis
import json

from flight.additions.additions import filter_tickets

HOST = os.environ.get('CACHE_HOST')
PORT = os.environ.get('CACHE_PORT')

async def check_offers_existance(request_id): # Cache operation

        ''' A function that checks if given data is in cache '''

        key = f"*_{request_id}"
        offers = []
        
        redis_client = redis.Redis(host=HOST, port=PORT)

        for offer_key in redis_client.scan_iter(key):
            if redis_client.exists(str(offer_key.decode("utf-8"))):
                offerTicket = json.loads(redis_client.get(str(offer_key.decode("utf-8"))))
                offer_tmp = []
                for off in offerTicket['data']:
                    offer_tmp.append(off['ticket'])
                offers = offers + offer_tmp
        redis_client.close()

        return offers

async def get_search_data(request_id): # Cache operation

        ''' A function that checks if given data is in cache '''

        key = f"{request_id}_search"

        redis_client = redis.Redis(host=HOST, port=PORT)
        search_data = redis_client.get(key)
        redis_client.close()

        return search_data

async def check_search_existance(data, provider_id, request_id): # Cache operation

        ''' A function that checks if given data is in cache '''

        directions = ""

        for direction in data['directions']:
            directions = directions + f"{direction['departure']}{direction['arrival']}_{direction['departure_date']}_"

        key = f"{provider_id}_{directions}ADT{data.get('adt')}_CHD{data.get('chd')}_INF{data.get('inf')}_INS{data.get('ins')}_FLEX{data.get('flexible')}_{data.get('class')}_{request_id}"
        
        redis_client = redis.Redis(host=HOST, port=PORT)
        offers = redis_client.get(key)
        redis_client.close()
        return offers

async def set_search_data(data, request_id, trip_type, currency): # Cache operation
        data = data
        redis_client = redis.Redis(host=HOST, port=PORT)
        redis_client.set(
            f"{request_id}_search",
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
    status = redis_client.get(f"{request_id}_status")
    val = 1

    if status != None:
        loaded_status = json.loads(status)
        val = loaded_status['status'] + 1

    redis_client.set(
        f"{request_id}_status",
        json.dumps({
            "status": val,
        }),
        1200
    )
    redis_client.close()

async def check_status(request_id):
    redis_client = redis.Redis(host=HOST, port=PORT)
    status = redis_client.get(f"{request_id}_status")
    if status != None:
        status = json.loads(status)
        ans = 'success' if status.get('status', 0) > 0 else 'error'
    else:
        ans = 'error'
    redis_client.close()
    return ans

async def set_provider_response_to_cache(data, provider_id, offers, request_id):
    # here is where all rules should be applied
    ''' A function that saves provider search response in cache for 3 minutes '''
    directions = ""

    for direction in data['directions']:
        directions = directions + f"{direction['departure']}{direction['arrival']}_{direction['departure_date']}_"

    key = f"{provider_id}_{directions}ADT{data.get('adt')}_CHD{data.get('chd')}_INF{data.get('inf')}_INS{data.get('ins')}_FLEX{data.get('flexible')}_{data.get('class')}_{request_id}"

    results = {
        'data': [],
    }

    for offer in offers['data']:
        results['data'].append({
            'ticket'       : offer.ticket,
            'other'        : offer.other,
            'provider_id'  : offer.provider_id,
            'provider_name': offer.provider_name,
            'system_id'    : offer.system_id
        })

    redis_client = redis.Redis(host=HOST, port=PORT)
    redis_client.set(
        key, 
        json.dumps(results), 
        3*60
        )
    redis_client.close()

async def get_single_offer(request_id, offer_id):
    
    ''' getting single offer'''

    key = f"*_{request_id}"
    offer_tmp = None
    
    redis_client = redis.Redis(host=HOST, port=PORT)

    for offer_key in redis_client.scan_iter(key):
        if redis_client.exists(str(offer_key.decode("utf-8"))):
            offerTicket = json.loads(redis_client.get(str(offer_key.decode("utf-8"))))
            for off in offerTicket['data']:
                if off['ticket']['offer_id'] == offer_id:
                    offer_tmp = off
    redis_client.close()

    if offer_tmp != None:
        result = {
            'status': 'success',
            'offer_data': offer_tmp
        }
    else:
        result = {
            'status': 'error',
            'message': 'offer_id not found'
        }
        return result


