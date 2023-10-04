############################## INTEGRATIONS ####################################

from flight.suppliers.mixvel.mixvel_integration import MixvelIntegration
from flight.suppliers.galileo.galileo_integration import GalileoIntegration

# new integrations should be added to INTEGRATIONS
INTEGRATIONS = {
    'aerticket': MixvelIntegration,
    'amadeus'  : MixvelIntegration,
    'centrum'  : MixvelIntegration,
    'mixvel'   : MixvelIntegration,
    'galileo'  : GalileoIntegration,
}

################################################################################