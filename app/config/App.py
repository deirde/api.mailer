from flask import Flask
from app.config.Config import Config as config_app

class App(object):

    def __init__(self):
        app = Flask(
            import_name = __name__,
            instance_path = config_app().data['instance_path'],
            instance_relative_config = config_app().data['instance_relative_config']
        )
        app.config['DEFAULT_TIMEZONE'] = config_app().data['timezone']
        app.config['SECRET_KEY'] = config_app().data['secret_key']
        app.config['TESTING'] = config_app().data['testing']
        app.debug = config_app().data['debug']
        app.config['SQLALCHEMY_DATABASE_URI'] = config_app().data['database_uri']
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config_app().data['sqlalchemy_track_modifications']
        self.data = app
        if config_app().data['enable_internal_log']:
            from logging.handlers import RotatingFileHandler
            import logging
            handler = RotatingFileHandler(
                config_app().data['internal_log_file_path'],
                maxBytes =  config_app().data['internal_log_max_bytes'],
                backupCount = config_app().data['internal_log_backup_count']
            )
            logger = logging.getLogger(config_app().data['import_name'])
            logger.setLevel(logging.ERROR)
            logger.addHandler(handler)

    def run(self):
        return self.data