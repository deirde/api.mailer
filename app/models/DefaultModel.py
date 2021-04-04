from app import app
from flask import json
import time
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.config.Config import Config as config_app

class Default(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    insert_date = db.Column(db.Integer)
    last_update_date = db.Column(db.Integer)
    name = db.Column(db.String(32))
    secret = db.Column(db.String(24))
    limit = db.Column(db.String(4))
    log = db.Column(db.Text)

    def __init__(self, insert_date, last_update_date, name, secret, limit, log):
        self.insert_date = insert_date
        self.last_update_date = last_update_date
        self.name = name
        self.secret = secret
        self.limit = limit
        self.log = log

    def __repr__(self):
        return '<Title %r>' % self.name

    @staticmethod
    def get_by_secret(secret):
        return Default.query.filter_by(secret = secret).first()

    @staticmethod
    def get_usage(m):
        counter = 0
        try:
            log = json.loads(m.log)
            today = time.strftime(config_app().data['date_format'])
            if today in log:
                counter = log[today]
        except:
            pass
        return counter

    @staticmethod
    def update_usage(m):
        if m is not None:
            today = time.strftime(config_app().data['date_format'])
            try:
                log = json.loads(m.log)
                if today in log:
                    log[today] += 1
                else:
                    log[today] = 1
            except:
                log = {
                    today: 1
                }
            if log[today] - 1 < config_app().data['limit'][m.limit]:
                if len(log) > config_app().data['database_log_backup_count']:
                    del log[log.keys()[-1]]
                m.log = json.dumps(log)
                db.session.commit()
                db.session.close()
                app.logger.info('DefaultModel: the limit has been successfully increased')