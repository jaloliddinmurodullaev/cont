import uuid

# Base Integration class for all Integrations
class BaseIntegration:

    def __init__(self) -> None:
        pass

    async def search(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def upsell(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def rules(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def verify(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def get_services(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response
    
    async def service_assign(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def seat_map(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def seat_assign(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def booking(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def cancel_booking(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def ticketing(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

    async def void(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response 

    async def refund(self):
        response = {
            "status": "error",
            "message": "not implemented"
        }
        return response

# Base Search Converter class for all Search Converters
class BaseSearchConverter:

    def __init__(self, offers) -> None:
        self.offers = offers
        self.offer  = None

    async def convert(self):
        offers = []
        for offer in self.offers:
            self.offer = offer
            offerTmp = {
                "offer_id": self.get_offer_id(),
                "price_info": self.get_price_info(),
                "upsell": self.if_upsell_is_available(),
                "booking": self.if_booking_is_available(),
                "price_details": self.get_price_details(),
                "baggages_info": self.get_baggage_info(),
                "fares_info": self.get_fares_info(),
                "routes": self.get_routes(),
                "provider": self.get_provider()
            }
            offers.append(offerTmp)
        return offers

    async def get_offer_id(self):
        offer_id = str(uuid.uuid4())
        return offer_id

    async def get_price_info(self):
        pass

    async def if_upsell_is_available(self):
        pass

    async def if_booking_is_available(self):
        pass

    async def get_price_details(self):
        pass

    async def get_baggage_info(self):
        pass

    async def get_fares_info(self):
        pass

    async def get_routes(self):
        routeTmp = {
            "route_index": "",
            "direction": "",
            "stops": "",
            "segments": self.get_segments()
        }
        return routeTmp
    
    async def get_segments(self):
        pass

    async def get_provider(self):
        provider = {
            "provider_id": self.offer,
            "name": self.offer
        }
        return provider

# Base Upsell Converter for all Upsell Converters
class BaseUpsellConverter:

    pass
