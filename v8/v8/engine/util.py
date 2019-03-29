#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal


def model_to_dict(model):
    if model is None:
        return
    ret = dict()
    for k in dir(model):
        if k.startswith('_'):
            continue
        v = getattr(model, k)
        if callable(v):
            continue
        if isinstance(v, (datetime.date, datetime.datetime)):
            ret[k] = v.isoformat()
        elif isinstance(v, Decimal):
            ret[k] = str(v)
        else:
            ret[k] = v
    ret.pop('metadata')
    return ret


def dict_to_model(from_dict, to_model):
    for key, value in from_dict.items():
        if hasattr(to_model, key):
            setattr(to_model, key, value)
