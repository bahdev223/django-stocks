from stocks.valorisation.registry import ValuationRegistry
from stocks.valorisation.base import BaseValuationStrategy
from stocks.valorisation.pmp import PMPStrategy
from stocks.valorisation.fifo import FIFOStrategy
from stocks.valorisation.standard import StandardCostStrategy

ValuationRegistry.register(PMPStrategy)
ValuationRegistry.register(FIFOStrategy)
ValuationRegistry.register(StandardCostStrategy)

__all__ = [
    "ValuationRegistry",
    "BaseValuationStrategy",
    "PMPStrategy",
    "FIFOStrategy",
    "StandardCostStrategy",
]
