############################## INTEGRATIONS ####################################

from flight.suppliers.mixvel.mixvel_integration import MixvelIntegration
from flight.suppliers.galileo.galileo_integration import GalileoIntegration
from flight.suppliers.aerticket.aerticket_integration import AerticketIntegration

# new integrations should be added to INTEGRATIONS
INTEGRATIONS = {
    'aerticket': AerticketIntegration,
    'amadeus'  : MixvelIntegration,
    'centrum'  : MixvelIntegration,
    'mixvel'   : MixvelIntegration,
    'galileo'  : GalileoIntegration,
}

################################################################################

class Integrations:
    id = 'primary_key'
    name = 'aerticket'
    integration = 'AerticketIntegration'
    system_id = 'uuid_code'