from flight.suppliers.mixvel.mixvel_integration import MixvelIntegration
from flight.suppliers.galileo.galileo_integration import GalileoIntegration

INTEGRATIONS = {
    'aerticket': MixvelIntegration,
    'amadeus'  : MixvelIntegration,
    'centrum'  : MixvelIntegration,
    'mixvel'   : MixvelIntegration,
    'galileo'  : GalileoIntegration,
}

class UpsellCollector:

    ''' A class that routes search request according to provider id '''

    def __init__(self, data) -> None: # Constructor
        pass

    async def collector(self): # Router
        pass

