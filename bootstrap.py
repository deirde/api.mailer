#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app
from app.config.Config import Config as config_app
from cherrypy import wsgiserver

if config_app().data['debug'] and config_app().data['testing']:
    app.run(
        config_app().data['ip'],
        port = config_app().data['port']
    )

else:
    d = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer((
        config_app().data['ip'],
        config_app().data['port']
    ), d)
    server.start()