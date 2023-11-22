import copy

async def rules_converter(rules, routes, fares):
    
    complete_rules = []

    for route in routes:
        route_tmp = {
            'route_index': route['route_index'],
            'segments': []
        }

        for segment in route['segments']:
            segment_leg = segment['leg']
            tarif = ""

            for fare in fares:
                if fare['leg'] == segment_leg:
                    tarif = fare['upsell']['name']

            segment_tmp = {
                "segment": segment['leg'],
                "rules": {
                    "blocks": {
                        "tariff": tarif,
                        "blocks": [],
                        "alldata": None,
                        "full_rules": None,
                        "redirect": None
                    }
                }
            }

            route_tmp['segments'].append(segment_tmp)

        complete_rules.append(route_tmp)

    if 'fareRuleList' in rules:
        for rule in complete_rules:
            for rl in rules['fareRuleList']:
                for seg in rule['segments']:
                    seg['rules']['blocks']['full_rules'] = copy.deepcopy(rl['htmlText'])
    
    return complete_rules
