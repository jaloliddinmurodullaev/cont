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
            (r"/gateway/search",         SearchHandler         ),
            (r"/gateway/offers",         OfferHandler          ),
            (r"/gateway/upsell",         UpsellHandler         ),
            (r"/gateway/rules",          RulesHandler          ),
            (r"/gateway/verify",         VerifyHandler         ),
            (r"/gateway/booking",        BookingHandler        ),
            (r"/gateway/retrieve",       RetrieveHandler       ),
            (r"/gateway/cancel",         CancelHandler         ),
            (r"/gateway/ticketing",      TicketingHandler      ),
            (r"/gateway/void",           VoidHandler           ),
            (r"/gateway/refund",         RefundHandler         ),
            (r"/gateway/add-new-system", SystemAddHandler      ) 
        ],
        debug=True,
        autoreload=True,
        template_path="flight/templates"
    )

    return url_pattern
