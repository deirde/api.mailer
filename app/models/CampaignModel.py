from app import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)
from app.controllers.BaseController import *

class Campaign(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    insert_date = db.Column(db.Integer)
    last_update_date = db.Column(db.Integer)
    campaign_name = db.Column(db.String(32))
    smtp_host = db.Column(db.String(64))
    smtp_uid = db.Column(db.String(48))
    smtp_pwd = db.Column(db.String(24))
    sent_per_hour = db.Column(db.Integer, default = 100)
    admin_email = db.Column(db.String(64))
    message = db.Column(db.Text)
    total_recipents = db.Column(db.Integer)
    total_email_sent = db.Column(db.Integer, default = 0)
    total_failures = db.Column(db.Integer, default = 0)

    def __init__(
            self,
            insert_date,
            last_update_date,
            campaign_name,
            smtp_host,
            smtp_uid,
            smtp_pwd,
            sent_per_hour,
            admin_email,
            message,
            total_recipents,
            total_email_sent = 0,
            total_failures = 0
        ):
        self.insert_date = insert_date
        self.last_update_date = last_update_date
        self.campaign_name = campaign_name
        self.smtp_host = smtp_host
        self.smtp_uid = smtp_uid
        self.smtp_pwd = smtp_pwd
        self.sent_per_hour = sent_per_hour
        self.admin_email = admin_email
        self.message = message
        self.total_recipents = total_recipents
        self.total_email_sent = total_email_sent
        self.total_failures = total_failures

    def __repr__(self):
        return '<ID %r>' % self.id

    @staticmethod
    def get_by_id(id):
        return Campaign.query.filter_by(
            id = id
        ).first()

    @staticmethod
    def add(model):
        db.session.add(model)

    @staticmethod
    def delete(model):
        return db.session.delete(model)

    @staticmethod
    def commit():
        return db.session.commit()

    def close():
        return db.session.close()

    def optimize():
        return db.engine.execute("VACUUM;")
