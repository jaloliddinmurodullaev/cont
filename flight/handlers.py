import json
import asyncio
import tornado.web

from flight.models import insert_system

from flight.additions.additions import Validator
from flight.collectors.search_collector import SearchCollector
from flight.collectors.offer_collector import OfferCollector
from flight.collectors.upsell_collector import UpsellCollector
from flight.collectors.rules_collector import RulesCollector
from flight.collectors.availability_collector import AvailabilityCollector
from flight.collectors.booking_collector import BookingCollector

# FLIGHT HANDLERS. BE CAREFUL WHILE CHANGING THEM.

class SearchHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.search_request_valiadator(data)):
            # start_time = time.time()
            collector = SearchCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]
        
        # print(f"Search handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class OfferHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.offers_request_valiadator(data)):
            # start_time = time.time()
            collector = OfferCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Offer handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class UpsellHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.upsell_request_validator(data)):
            # start_time = time.time()
            collector = UpsellCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Offer handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class RulesHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.rules_request_validator(data)):
            # start_time = time.time()
            collector = RulesCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Offer handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class AvailabilityHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.availability_request_validator(data)):
            # start_time = time.time()
            collector = AvailabilityCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Offer handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class BookingHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.booking_request_validator(data)):
            # start_time = time.time()
            collector = BookingCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Offer handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])    


class TicketingHandler(tornado.web.RequestHandler):
    async def post(self):
        pass


# SYSTEM HANDLERS. DO NOT TRY TO CHANGE THEM.

class SystemAddHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('system_add.html')

    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.adding_new_system_validator(data)):
            try:
                response = await asyncio.create_task(insert_system(system_id=data['system_id'], system_name=data['system_name'], system_type=data['system_type'], auth_data_fields=data['auth_data_fields']))
            except Exception as e:
                response = {
                    "status": "error", 
                    "message": str(e)
                }

            if response['status'] == 'success':
                success_message = response['message']
                try:
                    self.render("success.html", message=success_message)
                except Exception as e:
                    error_message = str(e)
                    self.render("error.html", message=error_message)
            else:
                error_message = response["message"]
                self.render("error.html", message=error_message)
        else:
            error_message = "Data is not valid. Please provide valid data!"
            self.render("error.html", message=error_message)

