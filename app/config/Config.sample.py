import os

class Config(object):

    def __init__(self):
        self.data = {
            'ip': '0.0.0.0',
            'port': 8081,
            'import_name': __name__,
            'instance_path': None,
            'instance_relative_config': True,
            'debug': True,
            'testing': True,
            'timezone': 'UTC',
            'date_format': '%m%d%y',
            'secret_key': 'qwerty',
            'database_uri': 'sqlite:////' + os.getcwd() + '/app/data/default.db',
            'sqlalchemy_track_modifications': False,
            'enable_internal_log': True,
            'internal_log_file_path': 'app/logs/error_log',
            'internal_log_max_bytes': 2097152,
            'internal_log_backup_count': 10,
            'database_log_backup_count': 10,
            'limit': {
                'soft': 100,
                'hard': 1000
            },
            'ban_timeout_millis': 60000,
            'ban_trap_range_millis': 1000,
            'service_timer_baseurl': 'http://1.2.3.4:8080/secret/qwerty/',
            'attachment_dir': os.getcwd() + '/tmp/',
            'transport_interval_seconds': 3.5,
            'default_sent_per_hour': 100,
            'transport_send_email': True,
            'send_raport_to_admin': True,
            'validate_email_before_send': True,
            'min_recipients_for_report': 1
        }

        if os.getenv('APP_PROD_' + self.data['secret_key']) is not None:
            if os.getenv('APP_PROD_' + self.data['secret_key']):
                self.data['debug'] = False
                self.data['testing'] = False