from app import app
from functools import wraps
from flask import jsonify, abort
from app.decorators.UpdateInternalLog import update_internal_log

def process_response(status_code, msg = '', stop = False, echo = 'info', log = True):
    response = {
        'status': status_code,
        'message': msg
    }
    if echo is not False:
        logger_msg = 'Status code <' + str(status_code) + '> Message <' + msg + '>'
        if echo == 'info':
            app.logger.info(logger_msg)
        if echo == 'warning':
            app.logger.warning(logger_msg)
    if log:
        update_internal_log(status_code, msg)
    if stop:
        response = jsonify(response)
        response.status_code = status_code
        abort(response)
    else:
        return response