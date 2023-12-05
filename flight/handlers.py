import json
import time
import asyncio
import tornado.web

from flight.models import insert_system

from flight.additions.additions import Validator

from flight.collectors.search_collector       import SearchCollector
from flight.collectors.offer_collector        import OfferCollector
from flight.collectors.upsell_collector       import UpsellCollector
from flight.collectors.rules_collector        import RulesCollector
from flight.collectors.verify_collector       import VerifyCollector
from flight.collectors.booking_collector      import BookingCollector
from flight.collectors.cancel_collector       import CancelCollector
from flight.collectors.retrieve_collector     import RetrieveCollector
from flight.collectors.ticketing_collector    import TicketingCollector
from flight.collectors.void_collector         import VoidCollector
from flight.collectors.refund_collector       import RefundCollector

# FLIGHT HANDLERS. BE CAREFUL WHILE CHANGING THEM.

class SearchHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

    async def post(self):
        data = json.loads(self.request.body)

        error_list = await asyncio.create_task(Validator.search_request_valiadator(data))

        # if error_list == []:
        #     # start_time = time.time()
        #     collector = SearchCollector(data)
        #     response = await asyncio.gather(collector.collector())
        #     # end_time = time.time()
        # else:
        #     response = [{
        #         "status" : "error",
        #         "message": error_list
        #     }, False]
        
        # # print(f"Search handler execution time: {round(end_time - start_time, 2)} seconds")
        # self.write(response[0])

        if len(data['directions']) == 1:
            response_ow = {
                "code": "100",
                "status": "success",
                "request_id": "6c62dcec-9334-11ee-8688-5169d0acfb81"
            }
            self.write(response_ow)
        else:
            response_rt = {
                "code": "100",
                "status": "success",
                "request_id": "0bd10cf8-9336-11ee-8688-5169d0acfb81"
            }
            self.write(response_rt)


class OfferHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

    async def post(self):
        data = json.loads(self.request.body)

        # if await asyncio.create_task(Validator.offers_request_valiadator(data)):
        #     # start_time = time.time()
        #     collector = OfferCollector(data)
        #     response = await asyncio.gather(collector.collector())
        #     # end_time = time.time()
        # else:
        #     response = [{
        #         "status" : "error",
        #         "message": "Data is not valid. Please, provide valid data!"
        #     }, False]

        # # print(f"Offer handler execution time: {round(end_time - start_time, 2)} seconds")
        # self.write(response[0])

        if data['request_id'] == "6c62dcec-9334-11ee-8688-5169d0acfb81":
            if data['next_token'] == "b2ec4126-58b5-4a88-99f4-8387733e0ce0":
                time.sleep(3)
                f = open("./flight/offer_ow2.json")
                data = json.load(f)
                f.close()
                self.write(data)
            else:
                time.sleep(2)
                f = open("./flight/offer_ow.json")
                data = json.load(f)
                f.close()
                self.write(data)
        if data['request_id'] == "0bd10cf8-9336-11ee-8688-5169d0acfb81":
            f = open("./flight/offer_rt.json")
            data = json.load(f)
            f.close()
            self.write(data)


class UpsellHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

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

        # print(f"Upsell handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class RulesHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

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

        # print(f"Rules handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class VerifyHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.verify_request_validator(data)):
            # start_time = time.time()
            collector = VerifyCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Availability handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])


class BookingHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

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

        # print(f"Booking handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])   


class RetrieveHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.retrieve_request_validator(data)):
            # start_time = time.time()
            collector = RetrieveCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Booking handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])  


class CancelHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.cancel_request_validator(data)):
            # start_time = time.time()
            collector = CancelCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Booking handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0]) 


class TicketingHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.ticket_request_validator(data)):
            # start_time = time.time()
            collector = TicketingCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Ticketing handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])  

class VoidHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        # Set CORS headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST")

    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.void_request_validator(data)):
            # start_time = time.time()
            collector = VoidCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Void handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0]) 

class RefundHandler(tornado.web.RequestHandler):
    async def post(self):
        data = json.loads(self.request.body)

        if await asyncio.create_task(Validator.refund_request_validator(data)):
            # start_time = time.time()
            collector = RefundCollector(data)
            response = await asyncio.gather(collector.collector())
            # end_time = time.time()
        else:
            response = [{
                "status" : "error",
                "message": "Data is not valid. Please, provide valid data!"
            }, False]

        # print(f"Void handler execution time: {round(end_time - start_time, 2)} seconds")
        self.write(response[0])   


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

