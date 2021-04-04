from app import app
import urllib3, json
from app.config.Config import Config as config_app
from app.decorators.ProcessResponse import process_response as _

def get():
    response = False
    try:
        http = urllib3.PoolManager()
        r = http.request('GET', config_app().data['service_timer_baseurl'])
        payload = json.loads(r.data.decode('utf-8'))
        if payload['posix'] is not None:
            response = int(payload['posix']['timestamp'])
    except:
        response = None
        pass
    return response

def get_or_ko():
    response = get()
    if response == False or response == None:
        _(403, 'The required service time is unavailable', stop = True)
    return response