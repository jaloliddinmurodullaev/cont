import json


def converter(data):
    offers = []

    for offer in data['OfferListResponse']['OfferID']:
        offerTmp = {
            "offer_id": "",
            "price_info": {
                "price": offer['Price']['TotalPrice'],
                "fee_amount": offer['Price']['TotalFees'],
                "commission_amount": 0
            },
            "upsell": True,
            "booking": True,
            "price_details": [],
            "baggages_info": [],
            "fares_info": [],
            "routes": [],
            "provider": {
                "provider_id": "1233-12323-1122-12233334",
                "name": "provider name is provided in request"
            }
        }

        cur_from = offer['Price']['CurrencyCode']['value']

        for price in offer['Price']['PriceBreakdown']:
            offerTmp['price_details'].append(
                {
                    "passenger_type": price['requestedPassengerType'],
                    "base_amount": price['Amount']['Base'],
                    "tax_amount": price['Amount']['Taxes']['TotalTaxes'],
                    "tax_details": [
                        {
                            "code": tax['taxCode'],
                            "total": tax['value'],
                            "currency": cur_from,
                            "description": ""
                        } for tax in price['Amount']['Taxes']['Tax']
                    ],
                    "fee_amount": price['Amount']['Fees']['TotalFees'],
                    "commission_amount": 0,
                    "total_amount": price['Amount']['Total'],
                    "payable_amount": price['Amount']['Total'],
                }
            )
        
        for passFlight in offer['Product']['PassengerFlight']:
            fares = data['OfferListResponse']['ReferenceList']
            for seg in passFlight['FlightProduct'][0]['segmentSequence']:
                segmentInd = ""
                for segm in offer['Product']['FlightSegment']:
                    if seg == segm['sequence']:
                        segmentInd = f"{segm['Flight']['Departure']['location']}-{segm['Flight']['Arrival']['location']}"
                services = []
                fare_name = ""
                for fare in fares:
                    for brand in fare['Brand']:
                        if passFlight['FlightProduct'][0]['Brand']['BrandRef'] == brand['id']:
                            services.append((
                                {
                                    "status": True,
                                    "code": fx['classification'],
                                    "name": fx['inclusion']
                                } for fx in brand['BrandAttribute']
                            ))
                            fare_name = brand['name']
                fareTmp = {
                    "leg": segmentInd,
                    "passenger_type": passFlight['passengerTypeCode'],
                    "seats": 2,
                    "upsell": {
                        "name": fare_name,
                        "services": services
                    },
                    "fare_code": passFlight['FlightProduct'][0]['fareBasisCode'],
                    "service_class": passFlight['FlightProduct'][0]['cabin'],
                    "booking_class": passFlight['FlightProduct'][0]['classOfService'],
                    # "fare_messages": {
                    #     "LTD": "",
                    #     "PEN": ""
                        
                    # },
                    "description": passFlight['FlightProduct'][0]['fareType']
                }
                offerTmp['fares_info'].append(fareTmp)

        # for baggage in offer['TermsAndConditionsFull']['BaggageAllowance']:
        #     {
        #         "leg": "IST-ESB",
        #         "passenger_type": "ADT",
        #         "baggage": {
        #             "value": 1,
        #             "unit": "PC",
        #             "size":{
        #                 "height": 129,
        #                 "width": 236,
        #                 "length": 112,
        #                 "unit": "cm"
        #             }
        #         },
        #         "hand_baggage": {
        #             "value": 1,
        #             "unit": "PC",
        #             "size":{
        #                 "height": 29,
        #                 "width": 23,
        #                 "length": 17,
        #                 "unit": "cm"
        #             }
        #         },
        #         "description": " "
        #     }

        for route in offer['Product']:
            routeTmp = {
                "route_index": "",
                "direction": "",
                "stops": "",
                "segments": []
            }
            rtIndex = int(route['id'].split('p')[1])
            routeTmp['route_index'] = rtIndex + 1
            routeTmp['direction'] = f"{route['FlightSegment'][0]['Flight']['Departure']['location']}-{route['FlightSegment'][-1]['Flight']['Arrival']['location']}"
            routeTmp['stops'] = len(route['FlightSegment']) - 1

            for segment in route['FlightSegment']:
                hours = int(segment['Flight']['duration'].split('PT')[1].split('H')[0])
                minutes = int(segment['Flight']['duration'].split('PT')[1].split('H')[1].split("M")[0])
                duration = hours * 60 + minutes
                segmentTmp = {
                    "segment_index": segment['sequence'],
                    "leg": f"{segment['Flight']['Departure']['location']}-{segment['Flight']['Arrival']['location']}",
                    "carrier_code": segment['Flight']['operatingCarrier'],
                    "carrier_name": segment['Flight']['operatingCarrierName'],
                    "carrier_logo": "https://b2b.easybooking.uz/images/airline/" + segment['Flight']['carrier'] + ".svg",
                    "flight_number": segment['Flight']['number'],
                    "departure_airport": segment['Flight']['Departure']['location'],
                    "departure_date": segment['Flight']['Departure']['date'],
                    "departure_time": segment['Flight']['Departure']['time'],
                    "departure_timezone": "",
                    "arrival_airport": segment['Flight']['Arrival']['location'],
                    "arrival_date": segment['Flight']['Arrival']['date'],
                    "arrival_time": segment['Flight']['Arrival']['time'],
                    "arrival_timezone": "",
                    "duration_minutes": duration,
                    "seatmap_availability": None,
                    "services_availability": None,
                    "flights_info": {
                        "airplane_info": {
                            "airplane_code": segment['Flight']['equipment'],
                            "airplane_name": segment['Flight']['equipment'],
                            "seat_distance": "",
                            "seat_width": "",
                            "seat_angle": "",
                            "has_wifi": None
                        },
                        "departure_country": segment['Flight']['Departure']['location'],
                        "departure_city": segment['Flight']['Departure']['location'],
                        "departure_city_code": segment['Flight']['Departure']['location'],
                        "departure_terminal": "",
                        "arrival_country": segment['Flight']['Arrival']['location'],
                        "arrival_city": segment['Flight']['Arrival']['location'],
                        "arrival_city_code": segment['Flight']['Arrival']['location'],
                        "arrival_terminal": "",
                        "stop_time_minutes": 0,
                        "marketing_airline_code": segment['Flight']['operatingCarrier'],
                        "marketing_airline_logo": "https://b2b.easybooking.uz/images/airline/" + segment['Flight']['operatingCarrier'] + ".svg",
                        "marketing_airline_name": segment['Flight']['operatingCarrierName'],
                        "operating_airline_code": segment['Flight']['operatingCarrier'],
                        "operating_airline_logo": "https://b2b.easybooking.uz/images/airline/" + segment['Flight']['operatingCarrier'] + ".svg",
                        "operating_airline_name": segment['Flight']['operatingCarrierName']
                    }
                }
                routeTmp['segments'].append(segmentTmp)
            offerTmp['routes'].append(routeTmp)
        offers.append(offerTmp)
    return offers

def main():
    c_from = open("from.json")
    c_from = json.load(c_from)

    print(converter(c_from))

if __name__ == "__main__":
    main()