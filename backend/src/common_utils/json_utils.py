from typing import Dict, Any, Optional
import collections


# from: https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys
def flatten_dict_by_joining(
    d: collections.Mapping, parent_key: Optional[str] = "", sep: Optional[str] = "-"
) -> collections.Mapping:
    items = []
    for k, v in d.items():
        new_k = sep.join([parent_key, k]) if parent_key else k
        if isinstance(v, collections.Mapping):
            items.extend(flatten_dict_by_joining(v, new_k, sep=sep).items())
        else:
            items.append((new_k, v))
    return dict(items)