import tornado.web

from .handlers import SearchHandler
from .handlers import OfferHandler
from .handlers import UpsellHandler
from .handlers import RulesHandler
from .handlers import VerifyHandler
from .handlers import BookingHandler
from .handlers import RetrieveHandler
from .handlers import CancelHandler
from .handlers import TicketingHandler
from .handlers import VoidHandler
from .handlers import RefundHandler
from .handlers import SystemAddHandler

def application():
    url_pattern = tornado.web.Application(
        [
            (r"/search",         SearchHandler         ),
            (r"/offers",         OfferHandler          ),
            (r"/upsell",         UpsellHandler         ),
            (r"/rules",          RulesHandler          ),
            (r"/verify",         VerifyHandler         ),
            (r"/booking",        BookingHandler        ),
            (r"/retrieve",       RetrieveHandler       ),
            (r"/cancel",         CancelHandler         ),
            (r"/ticketing",      TicketingHandler      ),
            (r"/void",           VoidHandler           ),
            (r"/refund",         RefundHandler         ),
            (r"/add-new-system", SystemAddHandler      ) 
        ],
        debug=False,
        autoreload=True,
        template_path="flight/templates"
    )

    return url_pattern
