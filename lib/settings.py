import logging 
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(object):
    debug = os.environ["DEBUG_MODE"].replace('"','').lower() == "true"
    dev = os.environ["DEV_MODE"].replace('"','').lower() == "true"

    port = os.environ["MY_APP_PORT"].replace('"','')
    client_id = os.environ["MY_WEBEX_CLIENT_ID"].replace('"','')
    client_secret = os.environ["MY_WEBEX_SECRET"].replace('"','')
    redirect_uri = os.environ["MY_WEBEX_REDIRECT_URI"].replace('"','')
    scopes = os.environ["MY_WEBEX_SCOPES"].replace('"','')

    service_app_client_id = os.environ["MY_SERVICE_APP_CLIENT_ID"].replace('"','')
    service_app_client_secret = os.environ["MY_SERVICE_APP_SECRET"].replace('"','')
    service_app_refresh_token = os.environ["MY_SERVICE_APP_REFRESH_TOKEN"].replace('"','')

    call_queue_target = os.environ["MY_CALL_QUEUE_TARGET"].replace('"','')
    mongo_uri = os.environ["MY_MONGO_URI"].replace('"','')
    mongo_db = os.environ["MY_MONGO_DB"].replace('"','')


class LogRecord(logging.LogRecord):
    def getMessage(self):
        msg = self.msg
        if self.args:
            if isinstance(self.args, dict):
                msg = msg.format(**self.args)
            else:
                msg = msg.format(*self.args)
        return msg

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    blue = "\x1b[31;34m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
