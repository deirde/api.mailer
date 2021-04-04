from app import app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class Planning(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    insert_date = db.Column(db.Integer)
    last_update_date = db.Column(db.Integer)
    campaign__id = db.Column(db.Integer)
    to_addr = db.Column(db.String(128))
    dispatch_timestamp = db.Column(db.Integer)
    has_been_sent = db.Column(db.Integer, default = False)

    def __init__(
            self,
            insert_date,
            last_update_date,
            campaign__id,
            to_addr,
            dispatch_timestamp,
            has_been_sent = False
        ):
        self.insert_date = insert_date
        self.last_update_date = last_update_date
        self.campaign__id = campaign__id
        self.to_addr = to_addr
        self.dispatch_timestamp = dispatch_timestamp
        self.has_been_sent = has_been_sent

    def __repr__(self):
        return '<Campaign ID %r>' % self.campaign__id

    @staticmethod
    def get_first_in_queue():
        return Planning.query.filter_by(
            has_been_sent = False
        ).order_by('dispatch_timestamp').first()

    @staticmethod
    def get_all_by_campaign_id(campaign__id):
        return Planning.query.filter_by(
            campaign__id = campaign__id
        )

    @staticmethod
    def add(model):
        return db.session.add(model)

    @staticmethod
    def delete(model):
        return db.session.delete(model)

    @staticmethod
    def commit():
        return db.session.commit()

    def close():
        db.session.close()

    def optimize():
        return db.engine.execute("VACUUM;")