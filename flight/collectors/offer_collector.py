import json
import copy
import asyncio

from flight.additions.cache_operations import check_status
from flight.additions.cache_operations import get_offers, get_search_data

from flight.microservices.currency.currency_api import CurrencyMicroservice

class OfferCollector:
    
    def __init__(self, data: dict) -> None: # Constructor
        self.request_id = data.get('request_id', None)
        self.next_token = data.get('next_token', None)
        self.limit      = data.get('limit', None)
        self.sort_type  = data.get('sort_type', None)
        self.currency   = data.get('currency', None)

    async def collector(self): # Router
        result = {
            "request_id": None,
            "status": None,
            "code": "",
            "trip_type": "",
            "sort_type": "",
            "currency": "USD",
            "count": 0,
            "next_token": None,
            "offers": []
        }

        search_data = await asyncio.create_task(get_search_data(request_id=self.request_id))

        if search_data != None:
            search_data = json.loads(search_data)
            result['status']     = await asyncio.create_task(check_status(request_id=self.request_id))
            result['request_id'] = self.request_id
            result['trip_type']  = search_data['trip_type']
            result['currency']   = self.currency
            result['sort_type']  = self.sort_type

            offers = await asyncio.create_task(get_offers(request_id=self.request_id))
            if offers: 
                for off in offers:
                    result['offers'].append(off['data']['ticket'])
                result['code'] = 100
            else:
                result['status'] = 'error'
                result['code'] = -100           
        else:
            result['status'] = 'error'
            result['code'] = -100

        # Filters

        # sort by price
        if self.sort_type == 'price':
            result['offers'] = await asyncio.create_task(self.sort_by_price(result['offers']))

        result['count'] = len(result['offers'])

        # limit offers
        if self.limit != None:
            if self.limit == 1:
                if len(result['offers']) > 0:
                    result['offers'] = [result['offers'][0]]
            else:
                result['offers'] = result['offers'][:self.limit]
        
        # currency converter
        currFrom = result['offers'][0]['price_info']['currency']
        currTo   = self.currency

        if self.currency != None and currFrom != currTo:
            result['offers'] = await self.currency_converter(result['offers'], currFrom, currTo) 

        return result
    
    async def sort_by_price(self, offers): # Sort
        return sorted(offers, key=lambda offer: offer["price_info"]["price"])
    
    async def currency_converter(self, offers, currFrom, currTo): # Currency Converter
        new_offers = []
        currency_microservice = CurrencyMicroservice()
        rate = await currency_microservice.exchange(currFrom=currFrom, currTo=currTo)

        for offer in offers:
            offer_tmp = copy.deepcopy(offer)
            offer_tmp['price_info']['price']      = copy.deepcopy(round(offer_tmp['price_info']['price']*rate, 2))
            offer_tmp['price_info']['fee_amount'] = copy.deepcopy(round(offer_tmp['price_info']['fee_amount']*rate, 2))
            offer_tmp['price_info']['currency']   = copy.deepcopy(currTo)

            for price_detail in offer_tmp['price_details']:
                price_detail['currency'] = copy.deepcopy(currTo)
                price_detail['single_base_amount'] = copy.deepcopy(round(price_detail['single_base_amount']*rate, 2))
                price_detail['single_tax_amount'] = copy.deepcopy(round(price_detail['single_tax_amount']*rate, 2))
                price_detail['fee_amount'] = copy.deepcopy(round(price_detail['fee_amount']*rate, 2))
                price_detail['commission_amount'] = copy.deepcopy(round(price_detail['commission_amount']*rate, 2))
                price_detail['single_total_amount'] = copy.deepcopy(round(price_detail['single_total_amount']*rate, 2))
                price_detail['base_total_amount'] = copy.deepcopy(round(price_detail['base_total_amount']*rate, 2))
                price_detail['tax_total_amount'] = copy.deepcopy(round(price_detail['tax_total_amount']*rate, 2))
                price_detail['total_amount'] = copy.deepcopy(round(price_detail['total_amount']*rate, 2))
                price_detail['payable_amount'] = copy.deepcopy(round(price_detail['payable_amount']*rate, 2))
            
            new_offers.append(offer_tmp)
        
        return new_offers
