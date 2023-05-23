from __future__ import print_function,unicode_literals
import aiohttp
import asyncio
import json
import logging
import traceback

from aiohttp import web
from datetime import datetime, timedelta

import lib.oauth as oauth

from lib.mongo_controller import MongoController
from lib.spark_asyncio import Spark
from lib.settings import Settings, LogRecord, CustomFormatter
from lib.xsi_manager import Calls, XSIManager


logging.setLogRecordFactory(LogRecord)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

class SparkObj(object):
    s = None

db = MongoController()
db.pmrs.create_index("pin", unique=True)

def html_response(document):
    with open('static/html/{0}'.format(document), "r") as d:
        return web.Response(text=d.read(), content_type='text/html')

"""
async def text(request):
    return web.Response(text="Hello, world")
"""

async def main(request):
    logger.debug('main hit.')
    if request.cookies.get('access_token') and request.cookies.get('id'):
        return html_response('index.html')
    else:
        return web.HTTPFound("/oauth")

async def setup(request):
    """
    Populate the UI with current PMR PIN mapping
    """
    logger.debug('cookies:')
    logger.debug(request.cookies)
    if request.cookies.get('access_token') and request.cookies.get('id'):
        my_pmr = await Spark(request.cookies.get('access_token')).get('https://webexapis.com/v1/meetingPreferences/personalMeetingRoom')
        pmr_details = {'address':my_pmr['sipAddress'], 'hostPin':my_pmr['hostPin'], "pin":"None"}
        cursor = db.find({'personId':request.cookies.get('id')})
        for document in await cursor.to_list(length=100):
            if document['address'] == pmr_details['address']:
                pmr_details['pin'] = document['pin']
        
        response = {
                    "avatar": request.cookies.get('avatar',''),
                    "pmrs": [pmr_details] 
                    }
    else:
        response = {"error": "Please login again." }
    return web.Response(text=json.dumps(response))

async def update(request):
    """
    POST requests from the UI to update / delete a PMR PIN
    """
    if request.cookies.get('access_token') and request.cookies.get('id'):
        body = await request.json()
        body.update({"personId":request.cookies.get('id')})
        body.update({"dev":Settings.dev})
        if body['pin'] != None:
            logger.info('updating PIN DB: {0}'.format(body))
            res = await db.update(body)
            if res == "DuplicateKeyError":
                response = {"error": "That PIN has already been taken." }
            else:
                response = {"pin": body['pin'], "address": body['address'] }
        else:
            body.pop('pin')
            res = await db.delete_one(body)
            if res:
                response = {"pin": "None", "address": body['address'] }
            else:
                response = {"error": "There is no PIN set for that PMR." }
    else:
        response = {"error": "Please login again." }
    return web.Response(text=json.dumps(response))


async def webex_connect(request):
    """
    Handles POST requests from Webex Connect (/connect).  
    This allows us to keep track of who is dialing which PMR PIN.
    We need to know this information when the XSI Event showing the call has made it to the queue has been triggered.
    Then, we can redirect the call to the PMR corresponding to the PIN the PSTN caller entered.
    """
    body = await request.json()
    logger.info("webex_connect request.json():{0}".format(body))
    body = body.get('data',{})
    if body.get('pin'):
        #dialed_number = body["dialed_number"].replace("+","")
        caller_number = body["caller_number"].replace("+","")
        pmr = await db.find_one({"pin":body["pin"], "dev":Settings.dev})
        approved_call = None
        if pmr:
            approved_call = {caller_number : {"sip": pmr['address']}}

        if approved_call:
            Calls.approved.update(approved_call)
            logger.info("approved_call:{}".format(approved_call))
            if Settings.debug:
                logger.warning('Running in Debug Mode. Call will NOT be received by XSI!')
            return web.Response(text='true')
        else:
            raise web.HTTPNotFound()

async def refresh_loop():
    next_check_seconds = 600 #how often we check the browser is running, and whether the meeting has ended and needs to be started again
    reset_hour = 0
    xsi_manager = XSIManager(True)
    last_daily_reset = None
    while True:
        logger.info("refresh_loop - running")
        try:
            now = datetime.utcnow()
            if last_daily_reset == None or (last_daily_reset < (now - timedelta(minutes=75)) and now.hour == reset_hour):
                """
                last_daily_reset is None only the first time this loop spins up
                Otherwise, this condition is true iff:
                last_daily_reset occurred more than 75 minutes ago, and the current hour is the hour we're supposed to reset (reset_hour.)
                """
                await xsi_manager.new_connector(Settings.call_queue_target)
                last_daily_reset = now
                logger.debug('Daily Reset Portion Complete.')
        except Exception as e:
            traceback.print_exc()
        logger.info("refresh_loop - done. Sleeping for {0} seconds.".format(next_check_seconds))
        await asyncio.sleep(next_check_seconds)

def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(refresh_loop())

if __name__ == '__main__':
    app = web.Application()
    app.add_routes([web.get('/oauth', oauth.get)])
    app.add_routes([web.get('/', main)])
    app.add_routes([web.post('/', setup)])
    app.add_routes([web.post('/update', update)])
    app.add_routes([web.post('/connect', webex_connect)])
    app.add_routes([web.static('/static', 'static')])
    
    loop = asyncio.get_event_loop()
    loop.create_task(refresh_loop())
    
    web.run_app(app, loop=loop, port=Settings.port)

