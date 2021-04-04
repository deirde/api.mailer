from app import app
from flask import request
from phpserialize import *
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.config.Config import Config as config_app
from app.controllers.BaseController import *
from app.services.TimestampService import get_or_ko as service_timestamp_get
from app.decorators.ProcessResponse import process_response as _

class Ban(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    insert_date = db.Column(db.Integer)
    last_update_date = db.Column(db.Integer)
    signature = db.Column(db.Text)
    counter = db.Column(db.Integer)
    is_banned = db.Column(db.Boolean)

    def __init__(self, insert_date, last_update_date, signature, counter = 0, is_banned = False):
        self.insert_date = insert_date
        self.last_update_date = last_update_date
        self.signature = signature
        self.counter = counter
        self.is_banned = is_banned

    def __repr__(self):
        return '<Request %r>' % self.signature

    @staticmethod
    def generate_signature():
        return dumps(str(request.environ))

    @staticmethod
    def get_by_signature(signature = None):
        return Ban.query.filter_by(signature = signature).first()

    @staticmethod
    def add_by_signature(signature):
        now = service_timestamp_get()
        try:
            m = Ban(now, now, signature, 1, False)
            db.session.add(m)
            db.session.commit()
            db.session.close()
            return True
        except:
            return False

    @staticmethod
    def update(m):
        now = service_timestamp_get()
        try:
            if m.is_banned == True and now - m.last_update_date > config_app().data['ban_timeout_millis']:
                m.is_banned = False
            elif now - m.last_update_date < config_app().data['ban_trap_range_millis']:
                m.counter += 1
                if m.counter > 10:
                    m.is_banned = True
            m.last_update_date = now
            db.session.commit()
            db.session.close()
            return True
        except:
            return False