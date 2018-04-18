import os, time, random, threading
from multiprocessing import Process, Pool, Queue
import subprocess
import aiohttp
import asyncio
try:
    from aiohttp.errors import ProxyConnectionError, ServerDisconnectedError, ClientResponseError, ClientConnectorError
except:
    from aiohttp import ClientProxyConnectionError as ProxyConnectionError, ServerDisconnectedError, \
        ClientResponseError, ClientConnectorError


# temp error name:aiohttp.client_exceptions.ClientOSError
async def test_single_proxy(proxy):
    try:
        async with aiohttp.ClientSession() as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode('utf-8')
                real_proxy = 'http://' + proxy
                print('Testing:', proxy)
                async with session.get(test_api, proxy=real_proxy, timeout=3) as response:
                    if response.status == 200:
                        print('Valid proxy:', proxy)
                        valid_list.append(proxy)
            except (asyncio.TimeoutError, ProxyConnectionError, TimeoutError, ValueError) as e:
                print('Invalid proxy:', proxy)
    except (ServerDisconnectedError, ClientResponseError, ClientConnectorError) as e:
        print(e)
        pass
'''
python 3.5之前的协程示例
@asyncio.coroutine
def run_func1():
	for count in range(1,5):
		print('func1 runs %d times,%s'% (count,threading.currentThread()))
		yield from asyncio.sleep(1)
@asyncio.coroutine
def run_func2():
	for count in range(1,5): 
		print('func2 runs %d times,%s'% (count,threading.currentThread()))
		yield from asyncio.sleep(1)
'''


async def test_single_proxy2(single_proxy):
    try:
        async with aiohttp.ClientSession() as session:
            try:
                if isinstance(single_proxy, bytes):
                    single_proxy = single_proxy.decode('utf-8')
                real_proxy = 'http://' + single_proxy
                print('Testing:', single_proxy)
                async with session.get(test_api, proxy=real_proxy, timeout=7, headers=HEADERS) as response:
                    if response.status == 200:
                        print('Valid proxy:', single_proxy)
                        valid_list.append(single_proxy)
            except (asyncio.TimeoutError, ProxyConnectionError, requests.exceptions.RequestException) as e:
                print(e)
            except (ValueError, Exception) as e:
                print(e)
        session.close()
    except Exception as e:
        print('create session failed')


async def test_all(proxylist, loop):
    try:
        session = aiohttp.ClientSession()
        tasks = [test_single_proxy2(proxy, session) for proxy in proxylist]
        loop.run_until_complete(asyncio.wait(tasks))
    except (ValueError, asyncio.TimeoutError):
        print('Async Error')
    except (ServerDisconnectedError, ClientResponseError, ClientConnectorError) as e:
        print('Create client session failed!')


def hello_w(loop):
    print('hello')
    loop.stop()


headers = randHeader()
print(len(headers))
'''cp = CrawlProxy()
db = RedisClient()
proxy_list = crawltest(cp)
loop = asyncio.get_event_loop()
tasks = [test_single_proxy2(proxy) for proxy in proxy_list]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()'''


def valid_test(iplist):
    url = 'http://www.baidu.com'
    # time = 3
    valid_ip = []
    for ip in iplist:
        proxy = {'http': 'http://{}'.format(ip), 'https': 'https://{}'.format(ip)}
        try:
            r = requests.get(url, timeout=3, proxies=proxy)
            valid_ip.append(ip)
        except requests.exceptions.RequestException as e:
            print(e)
    return valid_ip


def crawltest(cp):
    proxylist = []
    for web in range(cp.__FuncCount__):
        proxylist += cp.get_raw_proxy(cp.__AllFunc__[web])
    print('get proxy number:{}'.format(len(proxylist)))
    return proxylist