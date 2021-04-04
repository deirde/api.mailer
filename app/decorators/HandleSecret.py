from app import app
from functools import wraps
from flask import g, request, json, jsonify, abort
from app.config.Config import Config as config_app
from app.models.DefaultModel import Default as model_default
from app.decorators.ProcessResponse import process_response as _

def check_secret(f):
    @wraps(f)
    def default(*args, **kwargs):
        try:
            secret = request.headers.get('secret')
        except:
            return _(412, 'The parameter secret is empty or missing', stop = True)
        model = model_default.get_by_secret(secret)
        if model is not None:
            if config_app().data['limit'].get(model.limit, None) is None:
                return _(501, 'The requested functionality is not supported', stop = True)
        if model is not None:
            counter = model_default.get_usage(model)
            if counter >= config_app().data['limit'][model.limit]:
                return _(429, 'The usage limit has been reached', stop = True)
        else:
            return _(401, 'The secret used is not authorized', stop = True)
        return f(*args, **kwargs)
    return default

def increase_usage(f):
    @wraps(f)
    def default(*args, **kwargs):
        try:
            secret = request.headers.get('secret')
            model = model_default.get_by_secret(secret)
            model_default.update_usage(model)
        except:
            pass
        return f(*args, **kwargs)
    return default