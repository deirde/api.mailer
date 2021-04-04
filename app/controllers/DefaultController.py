# -*- coding: utf-8 -*-

from app import app
from flask import g, request, jsonify
from app.config.Config import Config as config_app
from app.decorators.ValidationDecorators import *
from app.decorators.HandleSecret import check_secret
from app.decorators.HandleBan import handle_ban
from app.controllers.BaseController import *
from app.services.TimestampService import get as service_timestamp_get
from app.models.CampaignModel import Campaign as model_campaign
from app.models.PlanningModel import Planning as model_planning

@app.route('/v1/email/validate/', methods = ['GET'])
@check_secret
@handle_ban
@validate_params_validation
def email_validate(email = "", check_mx = False, verify = False):
    from validate_email import validate_email
    if request.headers.get('check_mx') and request.headers.get('check_mx').lower() == 'true':
        check_mx = True
    if request.headers.get('verify') and request.headers.get('verify').lower() == 'true':
        verify = True
    response = {
        'status': 200,
        'check_mx': check_mx,
        'verifiy': verify,
        'valid': bool(validate_email(request.headers.get('email'), check_mx = check_mx, verify = verify))
    }
    return jsonify(response)

@app.route('/v1/email/send', methods = ['POST', 'PUT'])
@app.route('/v1/email/gmail/send', methods = ['POST', 'PUT'])
@smtp_auth_params_validation
@email_parts_params_validation
def email_send():
    campaign_name = request.headers.get('campaign_name')
    smtp_host = request.headers.get('smtp_host')
    smtp_uid = request.headers.get('smtp_uid')
    smtp_pwd = request.headers.get('smtp_pwd')
    from_addr = request.headers.get('from_addr')
    to_addrs = request.headers.get('to_addrs').split(';')
    sent_per_hour = request.headers.get('sent_per_hour')
    if sent_per_hour is None:
        sent_per_hour = config_app().data['default_sent_per_hour']
    sent_per_hour = int(sent_per_hour)
    admin_email = request.headers.get('admin_email')
    subject = request.headers.get('subject')
    body_plain = request.headers.get('body_plain')
    if body_plain is None:
        body_plain = ''
    body_html = request.headers.get('body_html')
    google_email_tracking_tid = request.headers.get('google_email_tracking_tid')
    if check_smtp(smtp_host, smtp_uid, smtp_pwd) == False:
        return stop(401, 'SMTP login failed')
    now = service_timestamp_get()
    if not now:
        return stop(500, 'The Timestamp service is unavailable at this moment')
    msg = email_msg_composer(request, campaign_name, from_addr, subject, body_plain, body_html, google_email_tracking_tid)
    m_campaign = model_campaign(now, now, campaign_name, smtp_host, smtp_uid, smtp_pwd, sent_per_hour, admin_email, msg.as_string(), len(to_addrs))
    m_campaign.add(m_campaign)
    m_campaign.commit()
    i = 0
    for to_addr in to_addrs:
        i += 1
        m_planning = model_planning(now, now, m_campaign.id, to_addr, int((now + (3600 / sent_per_hour * i))))
        m_planning.add(m_planning)
    m_planning.commit()
    return jsonify({
        'status': 200,
        'message': 'The delivery has been planned succesfully',
    })
