from json import JSONDecoder
from cff2coins.models.cff_coin_span import CffCoinSpan


def cff_coin_span_object_hook(d: dict) -> object:
    if "coin_span" in d and "references" in d:
        cff_coin_span = CffCoinSpan()
        cff_coin_span.coin_span = [tuple(t) for t in d["coin_span"]]
        cff_coin_span.references = [
            r for r in d["references"] if isinstance(r, CffCoinSpan)
        ]
        return cff_coin_span
    return d


class CffCoinSpanJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=cff_coin_span_object_hook, *args, **kwargs)
