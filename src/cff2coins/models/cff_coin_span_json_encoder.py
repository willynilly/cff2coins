from json import JSONEncoder
from cff2coins.models.cff_coin_span import CffCoinSpan


class CffCoinSpanJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CffCoinSpan):
            return obj.__dict__
        return super().default(obj)
