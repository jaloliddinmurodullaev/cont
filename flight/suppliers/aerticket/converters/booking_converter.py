import uuid
import time
from datetime import datetime, timezone

from flight.models import get_orders_count

BASE_MINIMUM_NUMBER = 1000001

async def booking_converter(offer_id, booking_data, ticket, search_data, passengers, agent):
    order_number = await get_orders_count()
    order_number = int(order_number.split(' ')[1])
    
    current_utc_time = datetime.utcnow()
    formatted_date = current_utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    response = {
        "status": "B",
        "order_number": order_number + BASE_MINIMUM_NUMBER,
        "booking_system": ticket['system_id'],
        "provider_uid": ticket['provider_id'],
        "provider_name": ticket['provider_name'],
        "offer_id": offer_id,
        "trip_type": search_data['trip_type'],
        "gds_pnr": booking_data['data']['pnr']['locator'],
        "supplier_pnr": booking_data['data']['pnr']['locator'],
        "created_at": formatted_date,
        "ticket_time_limit": None,
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
        fares_info_tmp = []
        baggages_info_tmp = []
        price_details_tmp = []

        for pr_in in price_info:
            if pr_in['passenger_type'] == passenger['type']:
                price_details_tmp.append({
                    "currency": pr_in['currency'],
                    "fee_amount": pr_in['fee_amount'],
                    "commission_amount": pr_in['commission_amount'],
                    "single_total_amount": pr_in['single_total_amount'],
                    "fare_total_amount": pr_in['base_total_amount'],
                    "tax_total_amount": pr_in['tax_total_amount'],
                    "total_amount": pr_in['total_amount'],
                    "payable_amount": pr_in['payable_amount'],
                    "single_fare_amount": pr_in['single_base_amount'],
                    "single_tax_amount": pr_in['single_tax_amount'],
                    "single_tax_details": pr_in['single_tax_details']
                })
        
        for fr_in in fares_info:
            if fr_in['passenger_type'] == passenger['type']:
                fares_info_tmp.append({
                    "leg": fr_in['leg'],
                    "fare_code": fr_in['fare_code'],
                    "description": fr_in['description'],
                    "booking_class": fr_in['booking_class'],
                    "service_class": fr_in['service_class'],
                    "upsell": {
                        "name": fr_in['upsell']['name'],
                        "services": fr_in['upsell']['services']
                    }
                })

        for bg_in in baggages_info:
            if bg_in['passenger_type'] == passenger['type']:
                baggages_info_tmp.append({
                    "leg": bg_in['leg'],
                    "description": bg_in['description'],
                    "baggage": bg_in['baggage'],
                    "hand_baggage": bg_in['hand_baggage']
                })

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
                'price_info': price_details_tmp,
                'fares_info': fares_info_tmp,
                'baggage_info': baggages_info_tmp
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