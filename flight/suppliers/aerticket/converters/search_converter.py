import json
import uuid

from flight.additions.additions import AdditionsTicket

async def search_converter(data, provider_id, provider_name, currency, trip_routes_cnt, request_id):
    offers = data['data']
    results = []
    
    if trip_routes_cnt == 1: # one way
        for _offers in offers['availableFareList']:
            total_price = 0
            fee_amount = 0
            currency_type = _offers['passengerTypeFareList'][0]['priceList'][0]['currency']['iso']

            for passen in _offers['passengerTypeFareList']:
                for prc in passen['priceList']:
                    if prc['type'] in ['TOTAL_TAX', 'AGENCY_PURCHASE_PRICE']:
                        total_price += prc['value']
                    elif prc['type'] == 'AGENCY_MARGIN':
                        total_price -= prc['value']
                    else:
                        pass
                for prc in passen['surchargeInfoList']:
                    fee_amount += prc['value']

            price_info = {
                "price": total_price - fee_amount,
                "currency": currency_type,
                "fee_amount": fee_amount,
                "commission_amount": 0
            }

            price_details = []

            for passen in _offers['passengerTypeFareList']:
                single_fare_amount = 0
                single_tax_amount = 0
                cnt = passen['count']
                _fee_amount = 0

                for price_list in passen['priceList']:
                    if price_list['type'] == 'TOTAL_TAX':
                        single_tax_amount = price_list['value']
                    if price_list['type'] == 'AGENCY_PURCHASE_PRICE':
                        single_fare_amount = price_list['value']
                
                for charge_list in passen['surchargeInfoList']:
                    _fee_amount += charge_list['value']

            
                price_details_tmp = {
                    "passenger_type": passen['passengerTypeCode'],
                    "currency": currency_type,
                    "quantity": cnt,
                    "single_fare_amount": single_fare_amount - _fee_amount,
                    "single_tax_amount": single_tax_amount,
                    "single_tax_details": [],
                    "fee_amount": _fee_amount,
                    "commission_amount": 0,
                    "single_total_amount": single_fare_amount + single_tax_amount,
                    "base_total_amount": single_fare_amount + single_tax_amount,
                    "tax_total_amount": single_tax_amount * cnt,
                    "total_amount": (single_fare_amount + single_tax_amount) * cnt,
                    "payable_amount": (single_fare_amount + single_tax_amount) * cnt
                }

                price_details.append(price_details_tmp)

            for offer in _offers['legList']:
                for off in offer['itineraryList']:
                    offer_id = uuid.uuid4()
                    offer_tmp = {
                        'offer_id': str(offer_id),
                        'price_info': price_info,
                        'upsell': True,
                        'booking': True,
                        'price_details': price_details,
                        'baggages_info': [],
                        'fares_info': [],
                        'routes': [],
                        'provider': {
                            'provider_id': provider_id,
                            'name': provider_name
                        }
                    }

                    route_tmp = {
                        "route_index": 1,
                        "direction": f"{off['segmentList'][0]['departure']['iata']}-{off['segmentList'][-1]['destination']['iata']}",
                        "stops": len(off['segmentList']) - 1,
                        "segments": await segment_maker(off['segmentList'], 100)
                    }
                    offer_tmp['routes'].append(route_tmp)
                complete_offer = AdditionsTicket(
                    ticket=offer_tmp,
                    offer_id=offer_tmp['offer_id'],
                    other={
                        'id': "qanaqadir id lar"
                    }
                )
                results.append(complete_offer)
    elif trip_routes_cnt == 2: # round trip
        pass 
    else: # multi city
        pass 

    return results

async def segment_maker(segments, duration_minutes):
    result_segments = []

    for segment in segments:
        segment_tmp = {
            "leg": f"{segment['departure']['iata']}-{segment['destination']['iata']}",
            "departure_city": segment['departure']['iata'],
            "departure_date": f"{segment['departureDate']['year']}-{segment['departureDate']['month']}-{segment['departureDate']['day']}",
            "departure_time": f"{segment['departureTimeOfDay']['hour'] if segment['departureTimeOfDay']['hour'] > 9 else '0' + str(segment['departureTimeOfDay']['hour'])}:{segment['departureTimeOfDay']['minute'] if segment['departureTimeOfDay']['minute'] > 9 else '0' + str(segment['departureTimeOfDay']['minute'])}:00",
            "departure_airport": segment['departure']['iata'],
            "departure_country": segment['departure']['iata'],
            "departure_terminal": "",
            "departure_timezone": "",
            "arrival_city": segment['destination']['iata'],
            "arrival_date": f"{segment['arrivalDate']['year']}-{segment['arrivalDate']['month']}-{segment['arrivalDate']['day']}",
            "arrival_time": f"{segment['arrivalTimeOfDay']['hour'] if segment['arrivalTimeOfDay']['hour'] > 9 else '0' + str(segment['arrivalTimeOfDay']['hour'])}:{segment['arrivalTimeOfDay']['minute'] if segment['arrivalTimeOfDay']['minute'] > 9 else '0' + str(segment['arrivalTimeOfDay']['minute'])}:00",
            "arrival_airport": segment['destination']['iata'],
            "arrival_country": segment['destination']['iata'],
            "arrival_terminal": "",
            "arrival_timezone": "",
            "carrier_code": segment['operatingAirline']['iata'],
            "carrier_name": segment['operatingAirline']['name'],
            "carrier_logo": f"https://b2b.easybooking.uz/images/airline/{segment['operatingAirline']['iata']}.svg",
            "duration_minutes": duration_minutes,
            "stop_time_minutes": "",
            "marketing_airline_code": segment['marketingAirline']['iata'],
            "marketing_airline_name": segment['marketingAirline']['name'],
            "marketing_airline_logo": f"https://b2b.easybooking.uz/images/airline/{segment['marketingAirline']['iata']}.svg",
            "operating_airline_code": segment['operatingAirline']['iata'],
            "operating_airline_name": segment['operatingAirline']['name'],
            "operating_airline_logo": f"https://b2b.easybooking.uz/images/airline/{segment['operatingAirline']['iata']}.svg",
            "airplane_info": {
                "has_wifi": False,
                "airplane_code": segment['equipmentType']['code'],
                "airplane_name": segment['equipmentType']['code'],
                "seat_angle": "",
                "seat_width": "",
                "seat_distance": "",
                "seat_scheme": ""
            }
        }
        result_segments.append(segment_tmp)

    return result_segments