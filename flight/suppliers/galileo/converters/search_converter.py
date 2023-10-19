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

async def search_converter(offers, guid, name, currency, route_count, request_id):
    pass