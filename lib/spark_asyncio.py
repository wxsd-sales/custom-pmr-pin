import aiohttp
import asyncio
#import time

#start_time = time.time()

class Spark(object):
    def __init__(self, token):
        self.token = token
        self.headers = {"Content-Type":"application/json",
                        "Authorization":"Bearer {0}".format(self.token)}

    def print_error(self, url, resp, res, method):
        print("{0} Error URL {1}:{2}".format(resp.status, method, url))
        print(res)
        try:
            print("TrackingId:{0}".format(resp.headers.get("Trackingid")))
        except Exception as e:
            print("No TrackingId.")

    async def retry_after(self, resp):
        if resp.status == 429:
            retry_after = None
            try:
                retry_after = resp.headers.get("Retry-After")
            except Exception as e:
                pass
            if retry_after == None:
                retry_after = 30
        else:
            retry_after = 10
        print("{0} hit, waiting for {1} seconds and then retrying...".format(resp.status, retry_after))
        await asyncio.sleep(int(retry_after))
        return retry_after

    async def get(self, url, max_retry_times=3):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as resp:
                res = await resp.json()
                #print(res)
                if resp.status > 299:
                    self.print_error(url, resp, res, "GET")
                    if (resp.status in [429] or resp.status >= 500) and max_retry_times > 0:
                        await self.retry_after(resp)
                        max_retry_times-=1
                        res = await self.get(url, max_retry_times)
                return res

    async def handle_req_with_body(self, resp, url, data, headers, method, max_retry_times):
        res = await resp.json()
        #print(res)
        if resp.status > 299:
            self.print_error(url, resp, res, method)
            #self.printf("New msg: {0}".format(msg))
            if (resp.status in [429] or resp.status >= 500) and max_retry_times > 0:
                await self.retry_after(resp)
                max_retry_times-=1
                if method == "PATCH":
                    res = await self.patch(url, data, headers, max_retry_times)
                elif method == "PUT":
                    res = await self.put(url, data, headers, max_retry_times)
                else:
                    res = await self.post(url, data, headers, max_retry_times)
        return res

    async def post(self, url, data, headers={}, max_retry_times=3):
        use_headers = dict(self.headers)
        use_headers.update(headers)
        async with aiohttp.ClientSession(headers=use_headers) as session:
            async with session.post(url, json=data) as resp:
                return await self.handle_req_with_body(resp, url, data, headers, "POST", max_retry_times)

    async def put(self, url, data, headers={}, max_retry_times=3):
        use_headers = dict(self.headers)
        use_headers.update(headers)
        async with aiohttp.ClientSession(headers=use_headers) as session:
            async with session.put(url, json=data) as resp:
                return await self.handle_req_with_body(resp, url, data, headers, "PUT", max_retry_times)

    async def patch(self, url, data, headers={}, max_retry_times=3):
        use_headers = dict(self.headers)
        use_headers.update(headers)
        async with aiohttp.ClientSession(headers=use_headers) as session:
            async with session.patch(url, json=data) as resp:
                return await self.handle_req_with_body(resp, url, data, headers, "PATCH", max_retry_times)