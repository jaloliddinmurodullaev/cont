import json 
import uuid

async def verify_converter(request_id, offer_id):
    return {
        'request_id': request_id,
        'offer_id'  : offer_id
    }