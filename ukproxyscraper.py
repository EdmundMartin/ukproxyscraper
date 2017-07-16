from random import choice
import re
import json

import requests
from lxml import html as html_parser

from proxy_errors import EmptyProxyList

class ProxyScraper(object):

    def __init__(self):
        self.proxy_dict = {'free-proxy-list': 'https://free-proxy-list.net/uk-proxy.html',
                           'gather-proxy': 'http://www.gatherproxy.com/proxylist/country/?c=United%20Kingdom',
                           'xroxy': 'http://www.xroxy.com/proxy-country-GB.htm'}
        self.proxy_list = []

    @staticmethod
    def random_user_agent():
        desktop_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
        return {'User-Agent': choice(desktop_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}

    def scrape_freeproxy_list(self):

        r = requests.get(self.proxy_dict['free-proxy-list'], headers=self.random_user_agent())
        dom = html_parser.fromstring(r.text)
        proxy_table = dom.cssselect('table tr')
        for res in proxy_table[1:]:
            try:
                ip = res[0].text_content()
                port = res[1].text_content()
                formatted_proxy = {'http':'{}:{}'.format(str(ip).strip(),str(port).strip())}
                if formatted_proxy['http'] != ':':
                    self.proxy_list.append(formatted_proxy)
            except (KeyError, IndexError):
                pass

    def scrape_gatherproxy(self):

        port_codes = {'1F90':'8080', '50': '80', '7A38': '31288', 'C38':'8118', 'D021': '53281'}

        r = requests.get(self.proxy_dict['gather-proxy'], headers=self.random_user_agent())
        dom = html_parser.fromstring(r.text)
        proxy_table = dom.cssselect('table script')
        for res in proxy_table:
            try:
                res = re.findall(r'{.*}', res.text_content())[0]
                result_json = json.loads(res)
                proxy_port = port_codes[result_json['PROXY_PORT']]
                self.proxy_list.append({'http': '{}:{}'.format(result_json['PROXY_IP'], proxy_port)})
            except (KeyError, IndexError):
                pass
    def grab_all_proxies(self):
        proxy_scrapers = [self.scrape_gatherproxy, self.scrape_freeproxy_list]
        for proxy in proxy_scrapers:
            try:
                proxy()
            except:
                pass
        self.dedupe_proxies()

    def random_proxy(self):
        if self.proxy_list:
            return choice(self.proxy_list)
        else:
            raise EmptyProxyList("Can't grab a random proxy from an empty list")

    def pop_proxy(self):
        if self.proxy_list:
            return self.proxy_list.pop()
        else:
            raise EmptyProxyList("Can't pop from an empty proxy list")

    def dedupe_proxies(self):
        temp_list = []
        for proxy in self.proxy_list:
            for values in proxy.values():
                if values not in temp_list:
                    temp_list.append(proxy)
        self.proxy_list = temp_list