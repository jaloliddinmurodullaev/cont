import asyncio
import json
import random
import hashlib
import uuid
import copy
import redis
import os

from flight.additions.additions import Helper, AdditionsTicket

HOST = os.environ.get('CACHE_HOST')
PORT = os.environ.get('CACHE_PORT')

redis_client = redis.Redis(host=HOST, port=PORT)

async def search_converter(offers, provider_uid, name, currency, route_count, request_id):
    offer_id = str(uuid.uuid4())
    ticket = offers
    other = {
        "ticket_id": "kkakkka",
        "impportants": "nasmjaas"
    }
    obj = AdditionsTicket(
        ticket=ticket,
        offer_id=offer_id,
        other=other
    )
    return obj
