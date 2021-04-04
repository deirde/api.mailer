from app import app
from functools import wraps
from flask import g, request, json, jsonify, abort
from app.models.BanModel import Ban as model_ban
from app.decorators.ProcessResponse import process_response as _

def handle_ban(f):
    @wraps(f)
    def default(*args, **kwargs):
        signature = model_ban.generate_signature()
        m = model_ban.get_by_signature(signature)
        if m is None:
            if model_ban.add_by_signature(signature) is not True:
                return _(500, 'Something wrong adding your signature', stop = True)
        else:
            if m.is_banned == 1:
                return _(423, 'Your signature is banned, try again later', stop = True)
            if model_ban.update(m) is not True:
                return _(500, 'Something wrong managing your signature', stop = True)
        return f(*args, **kwargs)
    return default