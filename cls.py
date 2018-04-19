import requests
import re
import redis
import os,time,random,threading
from multiprocessing import Process,Pool,Queue
import subprocess
import aiohttp
import asyncio
from setting import *
try:
	from aiohttp.errors import ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
except:
	from aiohttp import ClientProxyConnectionError as ProxyConnectionError,ServerDisconnectedError,ClientResponseError,ClientConnectorError
#temp error name:aiohttp.client_exceptions.ClientOSError
async def test_single_proxy(proxy):
	try:
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(proxy,bytes):
					proxy = proxy.decode('utf-8')
				real_proxy = 'http://'+proxy
				print('Testing:',proxy)
				async with session.get(test_api,proxy=real_proxy,timeout=3) as response:
					if response.status==200:
						print('Valid proxy:',proxy)
						valid_list.append(proxy)
			except (asyncio.TimeoutError,ProxyConnectionError,TimeoutError,ValueError) as e:
				print ('Invalid proxy:',proxy)
	except (ServerDisconnectedError,ClientResponseError,ClientConnectorError) as e:
		print(e)
		pass
class RedisClient(object):
	'''#redis数据库的封装'''
	def __init__(self,host=HOST,port=PORT):
		if PASSWORD:
			self.db = redis.Redis(host=host,port=port,password=PASSWORD)	
		else:
			self.db = redis.Redis(host=host,port=port)	
	def get(self,count=1):
		result = self.db.lrange(REDIS_KEY_NAME,0,count-1)
		self.db.ltrim(REDIS_KEY_NAME,count,-1)
		return result
	def put(self,entity):
		self.db.rpush(REDIS_KEY_NAME,entity)
	def pop(self):
		try:
			return self.db.rpop(REDIS_KEY_NAME)
		except Exception as e:
			print('The queue is empty!')
	def queue_len(self):
		return self.db.llen(REDIS_KEY_NAME)

class ProxyMeta(type):
#'''爬取类的meta类，改写了函数的属性，将子类函数的个数和特殊函数名称存为默认属性'''
	def __new__(cls,name,bases,attrs):
		count = 0
		attrs['__AllFunc__']=[]
		for k,v in attrs.items():
			if "crawlFunc_" in k:
				attrs['__AllFunc__'].append(k)
				count+=1
		attrs['__FuncCount__']=count
		return type.__new__(cls,name,bases,attrs)

class CrawlProxy(object,metaclass=ProxyMeta):
	def get_raw_proxy(self,callback):
#	'''将所有爬取函数抓取的proxyIP存到一个list里面'''
		proxy_list = []
		proxy_list = eval("self.{}()".format(callback))
		return proxy_list

	def crawlFunc__xicidaili(self):
#		'''爬取xicidaili网站前三页的高匿IP，基本上都是当天网站验证过的'''
		url='http://www.xicidaili.com/nn/'
		pages = PAGES_SET 
		header = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
		pattern = '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png"\
 alt="Cn" /></td>[\d|\D]*?<td>(.*?)</td>[\d|\D]*?<td>(.*?)</td>'
		proxylist = []
		for index in range(1,pages):
			html=self.get_html(url,index,header).text
			self.get_ProAddrList(html,pattern,proxylist)
		return proxylist

	def crawlFunc__kuaidaili(self):
#		'''爬取kuaidaili网站前三页的高匿IP，基本上都是当天网站验证过的'''
		url='https://www.kuaidaili.com/free/inha/'
		pages = PAGES_SET
		header = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
		pattern = '<td data-title="IP">(.*?)</td>[\d|\D]+?<td data-title="PORT">(.*?)</td>'
		proxylist = []
		for index in range(1,pages):
			html=self.get_html(url,index,header).text
			self.get_ProAddrList(html,pattern,proxylist)
		return proxylist

	def crawlFunc__ip3366(self):
	#	'''爬取ip3366.net网站前十的高匿IP，基本上都是当天网站验证过的'''
		url='http://www.ip3366.net/?stype=1&page='
		pages = PAGES_SET 
		header = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
		pattern = '<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>'
		proxylist = []
		for index in range(1,pages):
			html=self.get_html(url,index,header).text
			self.get_ProAddrList(html,pattern,proxylist)
		return proxylist

	def get_html(self,url,pages,header):
		url_all = url + str(pages)
		try:
			req=requests.get(url_all,headers=header)
			return req
		except requests.exceptions.ConnectionError as e:
			print (e.code)
			print (e.reason)

	def get_ProAddrList(self,html,pattern,proxylist):
		result = re.compile(pattern).findall(html)
		for add in result:
			proxy_add=add[0]+':'+add[1]
			proxylist.append(proxy_add)
	
def valid_test(iplist):
	url = 'http://www.baidu.com'
	#time = 3 
	valid_ip = []
	for ip in iplist:
		proxy ={'http':'http://{}'.format(ip),'https':'https://{}'.format(ip)}
		try:
			r = requests.get(url,timeout = 3,proxies=proxy)
			valid_ip.append(ip)
		except requests.exceptions.RequestException as e:
			print (e)
	return valid_ip
def crawltest(cp):
	proxylist = []
	for web in range(cp.__FuncCount__):
		proxylist += cp.get_raw_proxy(cp.__AllFunc__[web])
	print ('get proxy number:{}'.format(len(proxylist)))	
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
				if isinstance(single_proxy,bytes):
					single_proxy = single_proxy.decode('utf-8')
				real_proxy = 'http://'+single_proxy
				print('Testing:',single_proxy)
				async with session.get(test_api,proxy=real_proxy,timeout=7,headers=HEADERS) as response:
					if response.status==200:
						print('Valid proxy:',single_proxy)
						valid_list.append(single_proxy)
			except (asyncio.TimeoutError,ProxyConnectionError,requests.exceptions.RequestException) as e:
				print (e)
			except (ValueError,Exception) as e:
				print (e)
		session.close()
	except Exception as e:
		print('create session failed')
async def test_all(proxylist,loop):
	try:
		session = aiohttp.ClientSession()
		tasks = [test_single_proxy2(proxy,session) for proxy in proxylist]
		loop.run_until_complete(asyncio.wait(tasks))
	except (ValueError,asyncio.TimeoutError):
		print('Async Error')
	except (ServerDisconnectedError,ClientResponseError,ClientConnectorError) as e:
		print('Create client session failed!')
def hello_w(loop):
	print('hello')
	loop.stop()
	
headers =randHeader()
print(headers)
'''cp = CrawlProxy()
db = RedisClient()
proxy_list = crawltest(cp)
loop = asyncio.get_event_loop()
tasks = [test_single_proxy2(proxy) for proxy in proxy_list]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()'''
