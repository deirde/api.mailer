from app import app
from functools import wraps
from flask import request
from validate_email import validate_email
from app.controllers.BaseController import *

def validate_params_validation(f):
    @wraps(f)
    def default(*args, **kwargs):
        if request.headers.get('email') is None:
            return stop(422, 'Missing parameter email')
        return f(*args, **kwargs)
    return default

def smtp_auth_params_validation(f):
    @wraps(f)
    def default(*args, **kwargs):
        smtp_host = request.headers.get('smtp_host')
        if smtp_host is None:
            return stop(400, 'Missing parameter smtp_host')
        smtp_uid = request.headers.get('smtp_uid')
        if smtp_uid is None:
            return stop(400, 'Missing parameter smtp_uid')
        smtp_pwd = request.headers.get('smtp_pwd')
        if smtp_pwd is None:
            return stop(400, 'Missing parameter smtp_pwd')
        sent_per_hour = request.headers.get('sent_per_hour')
        if not sent_per_hour is None:
            try:
                sent_per_hour = int(sent_per_hour)
            except:
                return stop(400, 'Wrong type sent_per_hour')
        admin_email = request.headers.get('admin_email')
        if not admin_email is None:
            if validate_email(
                admin_email,
                check_mx = False,
                verify = False) == False:
                return stop(412, 'Invalid parameter admin_email')
        return f(*args, **kwargs)
    return default

def email_parts_params_validation(f):
    @wraps(f)
    def default(*args, **kwargs):
        campaign_name = request.headers.get('campaign_name')
        if campaign_name is None:
            return stop(400, 'Missing parameter campaign_name')
        if len(campaign_name) > 32:
            return stop(400, 'Parameter campaign_name too long, max. 32 chars')
        from_addr = request.headers.get('from_addr')
        if from_addr is None:
            return stop(400, 'Missing parameter from_addr')
        if validate_email(from_addr, check_mx = False, verify = False) == False:
            return stop(412, 'Invalid parameter from_addr')
        to_addrs = request.headers.get('to_addrs')
        if to_addrs is None:
            return stop(400, 'Missing parameter to_addrs')
        subject = request.headers.get('subject')
        if subject is None:
            return stop(400, 'Missing parameter subject')
        #body_plain = request.headers.get('body_plain')
        #if body_plain is None:
            #return stop(400, 'Missing parameter body_plain')
        body_html = request.headers.get('body_html')
        if body_html is None:
            return stop(400, 'Missing parameter body_html')
        return f(*args, **kwargs)
    return default