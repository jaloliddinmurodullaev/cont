from flight.suppliers.mixvel.mixvel_integration import MixvelIntegration

INTEGRATIONS = {
    'aerticket': MixvelIntegration,
    'amadeus'  : MixvelIntegration,
    'centrum'  : MixvelIntegration,
    'mixvel'   : MixvelIntegration,
}

class UpsellCollector:

    ''' A class that routes search request according to provider id '''

    def __init__(self, data) -> None: # Constructor
        pass

    async def controller(self): # Router
        pass

