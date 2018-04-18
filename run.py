import datetime
import aiohttp
import requests
import asyncio
from setting import *
#from Crawl import ProxyMeta,CrawlProxy
all_proxy = []
async def crawlFunc__xicidaili(session):
    # '''爬取xicidaili网站前N页的高匿IP'''
    url='http://www.xicidaili.com/nn/'
    pages = PAGES_SET
    pattern='<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png"\
alt="Cn" /></td>[\d|\D]*?<td>(.*?)</td>[\d|\D]*?<td>(.*?)</td>'
    proxylist = []
    try:
        for index in range(1, pages):
            async with session.get(url + str(index),timeout=7) as response:
                if response.status == 200:
                    result = re.compile(pattern).findall(response.text())
                    print(len(result))
                    for add in result:
                        proxy_add = add[0] + ':' + add[1]
                        proxylist.append(proxy_add)
                    all_proxy += proxylist
    except requests.exceptions.ConnectionError as e:
        print(e)
async def crawlFunc__kuaidaili(session):
    # '''爬取kuaidaili网站前N页的高匿IP'''
    url = 'https://www.kuaidaili.com/free/inha/'
    pages = PAGES_SET
    header = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'}
    pattern = '<td data-title="IP">(.*?)</td>[\d|\D]+?<td data-title="PORT">(.*?)</td>'
    proxylist = []
    try:
        for index in range(1, pages):
            async with session.get(url + str(index), timeout=7) as response:
                if response.status == 200:
                    result = re.compile(pattern).findall(response.text())
                    print(len(result))
                    for add in result:
                        proxy_add = add[0] + ':' + add[1]
                        proxylist.append(proxy_add)
                    all_proxy += proxylist
    except requests.exceptions.ConnectionError as e:
            print(e.code)
            print(e.reason)

async def test_asy():
    url = "http://www.baidu.com"
    async with aiohttp.ClientSession() as session:
        async with session.get(url,timeout=7) as response:
            asyncio.sleep(0.5)
            print(response.status)
    pass

def crawltest(cp):
    proxylist = []
    for web in range(cp.__FuncCount__):
        proxylist += cp.get_raw_proxy(cp.__AllFunc__[web])
    return proxylist
async def main():
    starttime = datetime.datetime.now()
    loop = asyncio.get_event_loop()
    async with aiohttp.ClientSession() as session:
        tasks = [crawlFunc__kuaidaili(session),crawlFunc__xicidaili(session)]
        loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    endtime = datetime.datetime.now()
    print(endtime - starttime)
if __name__ == '__main__':
    main()