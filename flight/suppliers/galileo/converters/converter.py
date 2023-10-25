import asyncio
import json
import random
import hashlib
import uuid
import copy
import redis
import os

from flight.additions.integration import BaseSearchConverter
from flight.additions.additions import Helper, AdditionsTicket

HOST = os.environ.get('CACHE_HOST')
PORT = os.environ.get('CACHE_PORT')

redis_client = redis.Redis(host=HOST, port=PORT)

class SearchConverter(BaseSearchConverter):
    
    def __init__(self, offers) -> None:
        super().__init__(offers)

    async def convert(self):
        return await super().convert()
    
    async def get_price_info(self):
        return await super().get_price_info()
    
    async def if_upsell_is_available(self):
        return await super().if_upsell_is_available()
    
    async def if_booking_is_available(self):
        return await super().if_booking_is_available()
    
    async def get_price_details(self):
        return await super().get_price_details()
    
    async def get_baggage_info(self):
        return await super().get_baggage_info()
    
    async def get_fares_info(self):
        return await super().get_fares_info()
    
    async def get_routes(self):
        return await super().get_routes()
    
    async def get_segments(self):
        return await super().get_segments()

    async def get_provider(self):
        return await super().get_provider()
    
