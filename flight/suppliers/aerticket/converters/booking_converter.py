import uuid

async def booking_converter(offer_id, booking_data, ticket, search_data, passengers, agent):
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

    response['routes'] = ticket['ticket']['routes']
    response['price_info'] = ticket['ticket']['price_info']
    response['price_details'] = ticket['ticket']['price_details']
    response['agent'] = agent
    response['passengers'] = await get_passengers(passengers, ticket['ticket']['price_details'], ticket['ticket']['baggages_info'], ticket['ticket']['fares_info'])
    
    return response

async def get_passengers(passengers, price_info, baggages_info, fares_info):
    response = []

    for passenger in passengers:
        passenger_order_id = uuid.uuid1()
        passenger_id = uuid.uuid1()
        passenger_tmp = {
            'ticket_number': None,
            'passenger_type': passenger['type'],
            'first_name': passenger['first_name'],
            'last_name': passenger['last_name'],
            'middle_name': passenger['middle_name'],
            'birth_date': passenger['birth_date'],
            'gender': passenger['gender'],
            'passenger_category': "Unknown",
            'phone_number': '+998992747465',
            'order_id': str(passenger_order_id),
            'passenger_id': str(passenger_id),
            'document': {
                "document_type": passenger['document']['type'],
                "citizenship": passenger['citizenship'],
                "passport_number": passenger['document']['number'],
                "passport_issuance": passenger['document']['issue_date'],
                "passport_expiry": passenger['document']['expire_date']
            },
            'ticket_info': {
                'price_info': [],
                'fares_info': [],
                'baggage_info': []
            },
            'seat_detail': [],
            'SSR': {},
            'OSI': {},
            'DOCO': {},
            'DOCA': {},
            'mile_card': {}
        }
        response.append(passenger_tmp)
    return(response)