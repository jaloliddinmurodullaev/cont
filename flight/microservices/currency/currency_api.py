import os
import aiohttp

BASE_URL = os.environ.get('CURRENCY_MICROSERVICE_BASE_URL')

class CurrencyMicroservice:

    def __init__(self) -> None:
        self.url = BASE_URL
        self.default_rate = 1

    async def exchange(self, currFrom: str, currTo: str):
        body = {
            "agent_uid": "asad",
            "provider_uid": "alfa1",
            "currency_base": currFrom.upper(), 
            "currency_pair": currTo.upper()
        }

        default_exchange_rate = self.default_rate

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + "/api/v1/agentrates", data=body) as response:
                status_code = response.status
                if status_code in [200, 201]:
                    resp = await response.json()
                    if "rate" in resp['data']:
                        rate = str(resp['data']['rate'])
                        return float(rate)
                    else:
                        return default_exchange_rate
                else:
                    return default_exchange_rate














