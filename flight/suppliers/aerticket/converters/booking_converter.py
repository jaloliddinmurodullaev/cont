import uuid

async def booking_converter(offer_id, booking_data, ticket, search_data):
    order_id = str(uuid.uuid1())

    response = {
        "status": "B",
        "order_number": 12234512,
        "order_id" : order_id,
        "booking_system": ticket['system_id'],
        "provider_uid": ticket['provider_id'],
        "provider_name": ticket['provider_name'],
        "offer_id": offer_id,
        "trip_type": search_data['trip_type'],
        "gds_pnr": booking_data['data']['pnr']['locator'],
        "supplier_pnr": booking_data['data']['pnr']['locator'],
        "created_at": "2023-10-31T12:53:42Z",
        "ticket_time_limit": "2023-09-13T21:43:00Z",
        "void_time_limit": None,
        "routes": [],
        "price_info": {},
        "price_details": [],
        "agent": {},
        "passengers": []
    }
    
    return response