import requests
import re
import aiohttp
import asyncio
from setting import *


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
    all_proxy = []
    def get_raw_proxy(self, callback):
        #	'''将所有爬取函数抓取的proxyIP存到一个list里面'''
        proxy_list = []
        proxy_list = eval("self.{}()".format(callback))
        return proxy_list

    async def crawlFunc__xicidaili(self):
        #'''爬取xicidaili网站前N页的高匿IP'''
        url = 'http://www.xicidaili.com/nn/'
        pages = PAGES_SET
        pattern = '<td class="country"><img src="http://fs.xicidaili.com/images/flag/cn.png"\
 alt="Cn" /></td>[\d|\D]*?<td>(.*?)</td>[\d|\D]*?<td>(.*?)</td>'
        proxylist = []
        try:
            async with aiohttp.ClientSession() as session:
                try:
                    for index in range(1, pages):
                        async with session.get(url+str(index), timeout=7) as response:
                            if response.status == 200:
                                result = re.compile(pattern).findall(response.text)
                                for add in result:
                                    proxy_add = add[0] + ':' + add[1]
                                    proxylist.append(proxy_add)
                                print('Valid proxy:', proxy)
                                valid_list.append(proxy)
                        html = session.getk
                            self.get_html(url, index, randHeader()).text
                        self.get_ProAddrList(html, pattern, proxylist)
                except requests.exceptions.ConnectionError as e:
                        print(e.code)
                        print(e.reason)
        except Exception as e:
            print('creat async client failed!')
        self.all_proxy += proxylist

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
