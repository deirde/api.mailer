from app import app
from flask import request
import time, traceback
import logging
from app.config.Config import Config as config_app
logger = logging.getLogger(config_app().data['import_name'])

def update_internal_log(status_code, msg, log = 'info'):
    data = {
        'time': time.strftime('%m%d%y'),
        'remote_addr': request.remote_addr,
        'method': request.method,
        'full_path': request.full_path
    }
    if status_code is not None:
        data['status'] = status_code
    if msg is not None:
        data['message'] = msg
    try:
        data['traceback'] = traceback.format_exc()
    except:
        pass
    try:
        logger.error(data)
    except:
        pass