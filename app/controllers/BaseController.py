# -*- coding: utf-8 -*-

import os, uuid, smtplib, re, enum, datetime
from app import app
from flask import g, request, jsonify
from app.decorators.HandleSecret import increase_usage
from apscheduler.schedulers.background import BackgroundScheduler
from validate_email import validate_email
import logging
from app.config.Config import Config as config_app
logger = logging.getLogger(config_app().data['import_name'])
from app.services.TimestampService import get as service_timestamp_get
from app.models.DefaultModel import Default as model_default
from app.models.CampaignModel import Campaign as model_campaign
from app.models.PlanningModel import Planning as model_planning

def transport():
    if not lock('locked'):
        lock('hold')
        m_planning = model_planning.get_first_in_queue()
        if m_planning is not None and service_timestamp_get() >= m_planning.dispatch_timestamp:
            m_campaign = model_campaign.get_by_id(m_planning.campaign__id)
            app.logger.info('BaseController: setting up the email for campaign <' +
                str(m_planning.campaign__id) +'> and recipient <' + m_planning.to_addr + '>')
            if m_campaign is not None:
                try:
                    is_valid = validate_email(m_planning.to_addr, check_mx = True, verify = True)
                    if config_app().data['validate_email_before_send'] and is_valid == False:
                        m_campaign.total_failures += 1
                        app.logger.info('BaseController: error, email NOT sent, invalid email')
                    else:
                        if config_app().data['transport_send_email']:
                            server = smtplib.SMTP(m_campaign.smtp_host)
                            server.ehlo_or_helo_if_needed()
                            server.starttls()
                            server.login(m_campaign.smtp_uid, m_campaign.smtp_pwd)
                            m_campaign.message = m_campaign.message.replace('<%cid%>', m_planning.to_addr)
                            m_campaign.message = m_campaign.message.replace('<%el%>', m_planning.to_addr)
                            server.sendmail(m_campaign.smtp_uid, m_planning.to_addr, m_campaign.message)
                            server.quit()
                        m_planning.has_been_sent = True
                        m_planning.add(m_planning)
                        m_planning.commit()
                        model_planning.close()
                        m_campaign.total_email_sent += 1
                        app.logger.info('BaseController: email sent')
                except:
                    m_campaign.total_failures += 1
                    app.logger.info('BaseController: error, email NOT sent, SMTP error')
            if m_campaign.total_recipents <= (m_campaign.total_email_sent + m_campaign.total_failures):
                campaign_close(m_campaign)
            else:
                model_campaign.commit()
                model_campaign.close()
    lock('release')
    return False
schedule = BackgroundScheduler(
    timezone = config_app().data['timezone'],
    daemon = True
)
schedule.add_job(
    transport,
    'interval',
    seconds = config_app().data['transport_interval_seconds']
)
schedule.start()

def campaign_close(m_campaign):
    report = []
    report.append('Report for campaign <' + m_campaign.campaign_name + '>')
    report.append('Sent succesfully <' + str(m_campaign.total_email_sent) +
        '> emails on <' + str(m_campaign.total_recipents) + '> recipents')
    mm_planning = model_planning.get_all_by_campaign_id(m_campaign.id)
    if mm_planning is not None:
        for m_planning in mm_planning:
            to_addr = m_planning.to_addr
            dispatch_timestamp = str(datetime.datetime.fromtimestamp(m_planning.dispatch_timestamp)
                                 .strftime('%Y-%m-%d %H:%M:%S'))
            if m_planning.has_been_sent:
                report.append('Confirmed delivery for <' + to_addr + '> at <' + dispatch_timestamp + '>')
            else:
                report.append('Not delivered to <' + to_addr + '>, tried at <' + dispatch_timestamp + '>')
            model_planning.delete(m_planning)
        model_planning.commit()
    model_planning.optimize()
    if m_campaign.total_recipents >= config_app().data['min_recipients_for_report']:
        if config_app().data['send_raport_to_admin']:
            if m_campaign.admin_email is not None:
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                msg = MIMEMultipart()
                msg['From'] = m_campaign.admin_email
                msg['To'] = m_campaign.admin_email
                msg['Subject'] = report[0]
                msg.attach(MIMEText('\r\n' . join(report), 'plain'))
                server = smtplib.SMTP(m_campaign.smtp_host)
                server.ehlo_or_helo_if_needed()
                server.starttls()
                server.login(m_campaign.smtp_uid, m_campaign.smtp_pwd)
                server.sendmail(m_campaign.smtp_uid, m_campaign.admin_email, msg.as_string())
                server.quit()
    model_campaign.close()
    model_campaign.delete(m_campaign)
    model_campaign.commit()
    model_campaign.optimize()
    model_campaign.close()
    app.logger.info('BaseController: campaign <' + str(m_campaign.id) + '> closed')
    return True

def check_smtp(smtp_host, smtp_uid, smtp_pwd):
    try:
        server = smtplib.SMTP(smtp_host)
        server.ehlo_or_helo_if_needed()
        server.starttls()
        server.login(smtp_uid, smtp_pwd)
        server.quit()
        return True
    except:
        return False

def email_msg_composer(request, campaign_name, from_addr, subject, body_plain, body_html, google_email_tracking_tid):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.base import MIMEBase
    from email import encoders
    response = MIMEMultipart()
    response['From'] = from_addr
    response['Subject'] = subject
    if not google_email_tracking_tid is None:
        tracking_code = google_email_tracking_composer(campaign_name, google_email_tracking_tid)
        body_html = tracking_code + body_html
    response.attach(MIMEText(body_html, 'html'))
    response.attach(MIMEText(body_plain, 'plain'))
    if request.method == 'PUT':
        request_files = request.files.to_dict()
        for file in request_files:
            file = request_files[file]
            extension = os.path.splitext(file.filename)[1]
            file_name = str(uuid.uuid4()) + extension
            file.save(os.path.join(config_app().data['attachment_dir'], file_name))
            attachment = open(config_app().data['attachment_dir'] + file_name, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename= %s' % file_name)
            response.attach(part)
            try:
                os.remove(config_app().data['attachment_dir'] + file_name)
            except OSError:
                pass
    return response

def google_email_tracking_composer(campaign_name, google_email_tracking_tid):
    response = "http://www.google-analytics.com/collect?v=1"
    response += "&tid=" + google_email_tracking_tid
    response += "&cid=<%cid%>"
    response += "&t=event"
    response += "&ec=email"
    response += "&ea=open"
    response += "&el=<%el%>"
    response += "&cs=newsletter"
    response += "&cm=email"
    response += "&cn=" + campaign_name
    return '<img src="' + response + '" />'

def lock(action):
    file_name = os.getcwd() + '/.lock'
    is_file = os.path.isfile(file_name)
    if action == 'hold':
        fd = os.open(file_name, os.O_RDWR|os.O_CREAT)
        os.write(fd, str.encode(''))
        return os.close(fd)
    elif action == 'release':
        try:
            return os.remove(file_name)
        except:
            return True
    elif action == 'locked':
        return is_file

def stop(status, message, logger = True):
    response = {
        'status': status,
        'message': message
    }
    if logger:
        log(response)
    response = jsonify(response)
    response.status_code = status
    return response

def log(response):
    import time, traceback
    data = {
        'time': time.strftime('%m%d%y'),
        'status': response['status'],
        'remote_addr': request.remote_addr,
        'method': request.method,
        'full_path': request.full_path,
        'message': response['message']
    }
    try:
        data['traceback'] = traceback.format_exc()
    except:
        pass
    logger.error(data)

@app.after_request
@increase_usage
def after_request(f):
    if not hasattr(g, 'after_request_callbacks'):
        g.after_request_callbacks = []
    g.after_request_callbacks.append(f)
    f.headers.add('Access-Control-Allow-Origin', '*')
    f.headers.add('Access-Control-Allow-Headers', '*')
    f.headers.add('Access-Control-Allow-Methods', '*')
    return f