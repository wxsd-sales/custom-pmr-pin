import aiohttp
import logging
import traceback

from lib.settings import Settings, LogRecord, CustomFormatter

logging.setLogRecordFactory(LogRecord)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

class TokenRefresher(object):
    def __init__(self):
        self._refresh_token = Settings.service_app_refresh_token

    def build_access_token_payload(self):
        payload = "grant_type=refresh_token&"
        payload += "client_id={0}&".format(Settings.service_app_client_id)
        payload += "client_secret={0}&".format(Settings.service_app_client_secret)
        payload += "refresh_token={0}".format(self._refresh_token)
        return payload

    async def refresh_token(self, state=""):
        try:
            logger.info('TokenRefresher.refresh_token called')
            url = "https://webexapis.com/v1/access_token"
            headers = {
                'cache-control': "no-cache",
                'content-type': "application/x-www-form-urlencoded"
                }
            ret_val = None
            payload = self.build_access_token_payload()
            logger.info("refresh token payload:{0}".format(payload))
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, data=payload) as resp:
                    resp = await resp.json()
                    logger.info("TokenRefresher.refresh_token /access_token Response: {0}".format(resp))
                    ret_val = resp["access_token"]
        except Exception as e:
            logger.info("TokenRefresher.refresh_token Exception:{0}".format(e))
            traceback.print_exc()
        return ret_val