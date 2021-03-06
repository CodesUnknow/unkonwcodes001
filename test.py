import requests
import re
import redis
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
PAGES_SET = 2
HOST = 'localhost'
PORT = 6379
PASSWORD = 'dsjsd1111'
REDIS_KEY_NAME = 'proxy'
test_api = 'https://www.baidu.com'
valid_list = []
HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': ' en-US,en;q=0.5',
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'}


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


class RedisClient(object):
    '''#redis数据库的封装'''

    def __init__(self, host=HOST, port=PORT):
        if PASSWORD:
            self.db = redis.Redis(host=host, port=port, password=PASSWORD)
        else:
            self.db = redis.Redis(host=host, port=port)

    def get(self, count=1):
        result = self.db.lrange(REDIS_KEY_NAME, 0, count - 1)
        self.db.ltrim(REDIS_KEY_NAME, count, -1)
        return result

    def put(self, entity):
        self.db.rpush(REDIS_KEY_NAME, entity)

    def pop(self):
        try:
            return self.db.rpop(REDIS_KEY_NAME)
        except Exception as e:
            print('The queue is empty!')

    def queue_len(self):
        return self.db.llen(REDIS_KEY_NAME)


class ProxyMeta(type):
    # '''爬取类的meta类，改写了函数的属性，将子类函数的个数和特殊函数名称存为默认属性'''
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__AllFunc__'] = []
        for k, v in attrs.items():
            if "crawlFunc_" in k:
                attrs['__AllFunc__'].append(k)
                count += 1
        attrs['__FuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class CrawlProxy(object, metaclass=ProxyMeta):
    def get_raw_proxy(self, callback):
        #	'''将所有爬取函数抓取的proxyIP存到一个list里面'''
        proxy_list = []
        proxy_list = eval("self.{}()".format(callback))
        return proxy_list

    def crawlFunc__xicidaili(self):
        #		'''爬取xicidaili网站前三页的高匿IP，基本上都是当天网站验证过的'''
        url = 'http://www.xicidaili.com/nn/'
        pages = PAGES_SET
        header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
        pattern = '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png"\
 alt="Cn" /></td>[\d|\D]*?<td>(.*?)</td>[\d|\D]*?<td>(.*?)</td>'
        proxylist = []
        for index in range(1, pages):
            html = self.get_html(url, index, header).text
            self.get_ProAddrList(html, pattern, proxylist)
        return proxylist

    def crawlFunc__kuaidaili(self):
        #		'''爬取kuaidaili网站前三页的高匿IP，基本上都是当天网站验证过的'''
        url = 'https://www.kuaidaili.com/free/inha/'
        pages = PAGES_SET
        header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
        pattern = '<td data-title="IP">(.*?)</td>[\d|\D]+?<td data-title="PORT">(.*?)</td>'
        proxylist = []
        for index in range(1, pages):
            html = self.get_html(url, index, header).text
            self.get_ProAddrList(html, pattern, proxylist)
        return proxylist

    def crawlFunc__ip3366(self):
        #	'''爬取ip3366.net网站前十的高匿IP，基本上都是当天网站验证过的'''
        url = 'http://www.ip3366.net/?stype=1&page='
        pages = PAGES_SET
        header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
        pattern = '<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>'
        proxylist = []
        for index in range(1, pages):
            html = self.get_html(url, index, header).text
            self.get_ProAddrList(html, pattern, proxylist)
        return proxylist

    def get_html(self, url, pages, header):
        url_all = url + str(pages)
        try:
            req = requests.get(url_all, headers=header)
            return req
        except requests.exceptions.ConnectionError as e:
            print(e.code)
            print(e.reason)

    def get_ProAddrList(self, html, pattern, proxylist):
        result = re.compile(pattern).findall(html)
        for add in result:
            proxy_add = add[0] + ':' + add[1]
            proxylist.append(proxy_add)


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


def get_html(url, pages, header):
    url_all = url + str(pages)
    try:
        req = requests.get(url_all, headers=header)
        return req
    except requests.exceptions.ConnectionError as e:
        print(e.code)
        print(e.reason)


def get_ProAddrList(html, pattern, proxylist):
    result = re.compile(pattern).findall(html)
    for add in result:
        proxy_add = add[0] + ':' + add[1]
        proxylist.append(proxy_add)


# 子进程要执行的代码
def run_proc1():
    url = 'https://www.kuaidaili.com/free/inha/'
    pages = PAGES_SET
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
    pattern = '<td data-title="IP">(.*?)</td>[\d|\D]+?<td data-title="PORT">(.*?)</td>'
    proxylist = []
    for index in range(1, pages):
        html = get_html(url, index, header).text
        get_ProAddrList(html, pattern, proxylist)
    time.sleep(1)
    return proxylist


def run_proc2():
    url = 'http://www.xicidaili.com/nn/'
    pages = PAGES_SET
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
    pattern = '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png"\
 alt="Cn" /></td>[\d|\D]*?<td>(.*?)</td>[\d|\D]*?<td>(.*?)</td>'
    proxylist = []
    for index in range(1, pages):
        html = get_html(url, index, header).text
        get_ProAddrList(html, pattern, proxylist)
    time.sleep(1)
    return proxylist
def loop():
    print('thread %s is running...' % threading.current_thread().name)
    n = 0
    while n < 5:
        n = n + 1
        print('thread %s >>> %s' % (threading.current_thread().name, n))
        time.sleep(1)
    print('thread %s ended.' % threading.current_thread().name)
def simple():
	print('--> coroutine started')
	x = yield
	print('--> coroutine recieved:',x)
def simple2(a):
	print('--> started:a=',a)
	b = yield a
	print('--> started:b=',b)
	c = yield a+b
	print('--> started:c=',c)

from functools import wraps
def coroutine(func):
	@wraps(func)
	def prime(*args,**kwargs):
		gen = func(*args,**kwargs)
		next(gen)
		return gen
	return prime

@coroutine
def averager():
	total = 0.0
	average1 = None
	count = 0
	while True:
		term = yield print(average1)
		total += term
		count += 1
		average1 = total/count
if __name__ == '__main__':
	from inspect import getgeneratorstate
	ave = averager()
	print(getgeneratorstate(ave))
	ave.send(2)
	ave.send(20)
    #starttime = time.time()
    #run_proc1('no1')
    # run_proc2('no2')
    #endtime = time.time()
    #print('total time %s:' % str(endtime - starttime))
    #starttime = time.time()
    ## run_proc1('no1')
    #run_proc2('no2')
    #endtime = time.time()
    #print('total time %s:' % str(endtime - starttime))
    #p1 = Process(target=run_proc1, args=('no1',))
    #p2 = Process(target=run_proc2, args=('no2',))
    #starttime = time.time()
    #p1.start()
    #p2.start()
    #p1.join()
    #p2.join()
    #endtime = time.time()
    #print('total time %s:' % str(endtime - starttime))


    #print('thread %s is running...' % threading.current_thread().name)
    #t1 = threading.Thread(target=run_proc1, name='LoopThread')
    #t2 = threading.Thread(target=run_proc2, name='LoopThread2')
    #starttime = time.time()
    ##t1.start()
    ##t2.start()
    ##t1.join()
    ##t2.join()
    #l1=run_proc1()
    #l2=run_proc2()
    #print('thread %s ended.' % threading.current_thread().name)
    ##endtime = time.time()
    #print('thread total time %s:' % str(endtime - starttime))
    # print('Parent process %s.' % os.getpid())
    # p = Process(target=run_proc, args=('test',))
    # print('Child process will start.')
    # p.start()
    # p.join()
    # print('Child process end.')
