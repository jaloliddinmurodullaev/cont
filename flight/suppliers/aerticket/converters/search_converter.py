import uuid
import copy

from flight.additions.additions import AdditionsTicket

async def search_converter(data, provider_id, provider_name, currency, trip_routes_cnt):
    offers = data['data']
    results = []
    _has_adt = True
    _has_chd = False
    _has_inf = False

    for passens in offers['availableFareList'][0]['passengerTypeFareList']:
        if passens['passengerTypeCode'] == 'ADT':
            _has_adt = True
        if passens['passengerTypeCode'] == 'CHD':
            _has_chd = True
        if passens['passengerTypeCode'] == 'INF':
            _has_inf = True

    passengers_info = {
        'adt': _has_adt,
        'chd': _has_chd,
        'inf': _has_inf
    }
    
    if trip_routes_cnt == 1: # one way
        for _offers in offers['availableFareList']:
            currency_type = _offers['passengerTypeFareList'][0]['priceList'][0]['currency']['iso']

            price_info = await get_price_info(_offers, currency_type)
            price_details = await get_price_details(_offers, currency_type)
            baggage_info = await get_baggage_info(_offers, passengers_info)
            fare_info = await get_fare_info(_offers, passengers_info)

            for offer in _offers['legList']:
                for off in offer['itineraryList']:
                    offer_id = uuid.uuid4()
                    offer_tmp = {
                        'offer_id': str(offer_id),
                        'price_info': price_info,
                        'upsell': True,
                        'booking': True,
                        'price_details': price_details,
                        'baggages_info': baggage_info,
                        'fares_info': fare_info,
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
        for _offers in offers['availableFareList']:
            currency_type = _offers['passengerTypeFareList'][0]['priceList'][0]['currency']['iso']

            price_info = await get_price_info(_offers, currency_type)
            price_details = await get_price_details(_offers, currency_type)

            offers = await round_trip(_offers, price_info, price_details, 
                                       passengers_info, provider_id, provider_name)
            for off in offers:
                results.append(off)

    else: # multi city
        pass 

    return results

async def round_trip(offers, price_info, price_details, passengers_info, provider_id, provider_name):
    results = []
    # for offer in offers['legList']:
    for off_from in offers['legList'][0]['itineraryList']:
        route_1_tmp = {
            "route_index": 1,
            "direction": f"{off_from['segmentList'][0]['departure']['iata']}-{off_from['segmentList'][-1]['destination']['iata']}",
            "stops": len(off_from['segmentList']) - 1,
            "segments": await segment_maker(off_from['segmentList'], 100)
        }
        baggage_info_from = await get_baggage_info(off_from, passengers_info)
        fare_info_from = await get_fare_info(off_from, passengers_info)
        for off_to in offers['legList'][1]['itineraryList']:
            baggage_info_to = await get_baggage_info(off_to, passengers_info)
            fare_info_to = await get_fare_info(off_to, passengers_info)

            baggage_info = baggage_info_from + baggage_info_to
            fare_info = fare_info_from + fare_info_to
            offer_id = uuid.uuid4()
            offer_tmp = {
                'offer_id': str(offer_id),
                'price_info': price_info,
                'upsell': True,
                'booking': True,
                'price_details': price_details,
                'baggages_info': baggage_info,
                'fares_info': fare_info,
                'routes': [],
                'provider': {
                    'provider_id': provider_id,
                    'name': provider_name
                }
            }

            offer_tmp['routes'].append(route_1_tmp)

            route_2_tmp = {
                "route_index": 2,
                "direction": f"{off_to['segmentList'][0]['departure']['iata']}-{off_to['segmentList'][-1]['destination']['iata']}",
                "stops": len(off_to['segmentList']) - 1,
                "segments": await segment_maker(off_to['segmentList'], 100)
            }

            offer_tmp['routes'].append(route_2_tmp)

            complete_offer = AdditionsTicket(
                ticket=offer_tmp,
                offer_id=offer_tmp['offer_id'],
                other={
                    'id': "qanaqadir id lar"
                }
            )
            results.append(complete_offer) 

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

async def get_price_info(_offers, currency_type):
    total_price = 0
    fee_amount = 0

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
    return price_info

async def get_price_details(_offers, currency_type):

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
    
    return price_details

async def get_baggage_info(route, passengers_info):
    baggages_info = []

    for segment in route['segmentList']:
        baggage_info_tmp = {
            "leg": f"{segment['departure']['iata']}-{segment['destination']['iata']}",
            "passenger_type": "ADT",
            "baggage": {
                "value": segment['baggageAllowance']['quantity'],
                "unit": segment['baggageAllowance']['unit'],
                "size": {
                    "height": None,
                    "width": None,
                    "length": None,
                    "unit": ""
                }
            },
            "hand_baggage": {
                "value": 0,
                "unit": segment['baggageAllowance']['unit'],
                "size": {
                    "height": None,
                    "width": None,
                    "length": None,
                    "unit": ""
                }
            },
            "description": ""
        }

        if passengers_info['adt'] == True:
            baggages_info.append(copy.deepcopy(baggage_info_tmp))
        if passengers_info['chd'] == True:
            baggage_info_tmp['passenger_type'] = "CHD"
            baggages_info.append(copy.deepcopy(baggage_info_tmp))
        if passengers_info['inf'] == True:
            baggage_info_tmp['passenger_type'] = "INF"
            baggages_info.append(copy.deepcopy(baggage_info_tmp))

    return baggages_info

async def get_fare_info(route, passengers_info):
    fares_info = []

    for segment in route['segmentList']:
                fare_info_tmp = {
                    "leg": f"{segment['departure']['iata']}-{segment['destination']['iata']}",
                    "passenger_type": "ADT",
                    "seats": "9",
                    "upsell": {
                        "name": segment.get('airlineFareFamily', ''),
                        "services": []
                    },
                    "fare_code": segment['fareBase'],
                    "service_class": segment['cabinClass'],
                    "booking_class": segment['bookingClassCode'],
                    "fare_messages": {
                        "LTD": "",
                        "PEN": ""
                    },
                    "description": ""
                }

                if passengers_info['adt'] == True:
                    fares_info.append(copy.deepcopy(fare_info_tmp))
                if passengers_info['chd'] == True:
                    fare_info_tmp['passenger_type'] = "CHD"
                    fares_info.append(copy.deepcopy(fare_info_tmp))
                if passengers_info['inf'] == True:
                    fare_info_tmp['passenger_type'] = "INF"
                    fares_info.append(copy.deepcopy(fare_info_tmp))

    return fares_info



