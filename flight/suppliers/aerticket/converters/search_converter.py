import json

async def search_converter(data, provider_id, provider_name, currency, lenght, request_id):
    print(data)
    data = dict(data)
    json_object = json.dumps(data, indent=4)
 
    with open("sample.json", "w") as outfile:
        outfile.write(json_object)

    return {
        'data': data
    }