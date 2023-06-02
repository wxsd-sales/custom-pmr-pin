import aiohttp
import json
import logging
import traceback
import urllib.parse

from aiohttp import web

from lib.spark_asyncio import Spark
from lib.settings import Settings, LogRecord, CustomFormatter

logging.setLogRecordFactory(LogRecord)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

def build_access_token_payload(code, client_id, client_secret, redirect_uri):
    payload = "client_id={0}&".format(client_id)
    payload += "client_secret={0}&".format(client_secret)
    payload += "grant_type=authorization_code&"
    payload += "code={0}&".format(code)
    payload += "redirect_uri={0}".format(redirect_uri)
    return payload

async def get_tokens(code):
    url = "https://webexapis.com/v1/access_token"
    api_url = 'https://webexapis.com/v1'
    payload = build_access_token_payload(code, Settings.client_id, Settings.client_secret, Settings.redirect_uri)
    headers = {
        'cache-control': "no-cache",
        'content-type': "application/x-www-form-urlencoded"
        }
    person = None
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, data=payload) as resp:
                res = await resp.json()
                #print(resp.headers)
                #print(resp.status)
                logger.debug("****************************************************************************")
                logger.debug("WebexOAuthHandler.get_tokens /access_token Response: {0}".format(res))
                logger.debug('----------------------------------------------------------------------------')
                logger.debug('refresh token: {0}'.format(res.get('refresh_token')))
                logger.debug('----------------------------------------------------------------------------')
                person = await Spark(res.get('access_token')).get('{0}/people/me'.format(api_url))
                logger.debug("person:{0}".format(person))
                logger.debug("****************************************************************************")
                person.update({"access_token":res.get('access_token')})
    except Exception as e:
        logger.error("WebexOAuthHandler.get_tokens Exception:{0}".format(e))
        traceback.print_exc()
    return person

def set_cookies(person):
    cookie_max_age = 86400 #seconds
    redirect = web.HTTPFound("/")
    redirect.set_cookie('id', person['id'], max_age=cookie_max_age)
    redirect.set_cookie('avatar', person.get('avatar',''), max_age=cookie_max_age)
    redirect.set_cookie('displayName', person.get('displayName',''), max_age=cookie_max_age)
    redirect.set_cookie('access_token', person.get('access_token',''), max_age=cookie_max_age)
    return redirect

async def get(request):
    response = "Error"
    redirect = None
    try:
        logger.info('Webex OAuth: {0}'.format(request.url))
        if request.query.get("code", None):
            code = request.query.get("code")
            person = await get_tokens(code)
            if person:
                #redirect = "/"
                redirect = set_cookies(person)
        else:
            authorize_url = 'https://webexapis.com/v1/authorize?client_id={0}&response_type=code&redirect_uri={1}&scope={2}'
            authorize_url = authorize_url.format(Settings.client_id, urllib.parse.quote_plus(Settings.redirect_uri), Settings.scopes)
            logger.info("WebexOAuthHandler.get authorize_url:{0}".format(authorize_url))
            redirect = web.HTTPFound(authorize_url)
    except Exception as e:
        response = "{0}".format(e)
        logger.error("WebexOAuthHandler.get Exception:{0}".format(e))
        traceback.print_exc()
    if redirect:
        return redirect
    else:
        return web.Response(text=response)
