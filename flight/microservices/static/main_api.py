import os
import aiohttp

BASE_URL = os.environ.get('STATIC_MICROSERVICE_BASE_URL')

class StaticMicroservice:
    def __init__(self) -> None:
        self.url = BASE_URL

    async def get_airport_data(self, airport_iata):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url + "/data/airports/" + airport_iata) as response:
                status_code = response.status
                if status_code in [200, 201]:
                    return response.json()['data'][0]
                else:
                    return None
                
    async def get_country_data(self, country_iata):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url + "/data/country/" + country_iata) as response:
                status_code = response.status
                if status_code in [200, 201]:
                    return response.json()['data'][0]
                else:
                    return None
                
    async def get_country_cities_data(self, country_iata):
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url + "/data/cities/" + country_iata) as response:
                status_code = response.status
                if status_code in [200, 201]:
                    return response.json()['data']
                else:
                    return None
                
    async def get_document_type(self, country: str):
        if country.upper() == "RU":
            body = {
                "country": "RU"
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url + "/data/typedocument", data=body) as response:
                    status_code = response.status
                    if status_code in [200, 201]:
                        return response.json()['data']
                    else:
                        return None
        else:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url + "/data/typedocument") as response:
                    status_code = response.status
                    if status_code in [200, 201]:
                        return response.json()['data']
                    else:
                        return None
                    


