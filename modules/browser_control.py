
from faker import Faker
from tools.bit_api import createBrowser, fetchBrowserDetail, openBrowser
from selenium import webdriver
from seleniumwire import webdriver as wire_webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from tools.selenium_driver_helper import SeleniumDriverHelper
# for log
import logging
from rich.console import Console
from rich.logging import RichHandler

log = logging.getLogger(__name__)
class BrowserControl():
    def __init__(self,proxy_area = 'hk') -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.faker = Faker()
        self.session_id = self.faker.password(length=15, special_chars=False, digits=True, upper_case=True, lower_case=True)
        self.proxy_server = 'pr.aa4koj1o.lunaproxy.net'
        self.proxy_port = 12233
        self.proxy_username = f'user-lu7069006-region-{proxy_area}-sessid-{self.session_id}-sesstime-30'
        self.proxy_password = f'B8#U&E*asjXRg$'
        self.browser_data = None
        
    def create_browser(self,borwser_name,remark):
        # 创建一个浏览器环境
        json_data = {
            'name': borwser_name,  # 窗口名称
            # 'groupId': self.browser_group_id,
            # 'proxyMethod': 3,  # 代理方式 2自定义 3 提取IP
            # # 代理类型  ['noproxy', 'http', 'https', 'socks5', 'ssh']
            # 'proxyType': 'socks5',

            # 'dynamicIpUrl': 'http://43.156.34.150:777/proxy/get_proxy_list?key=a850b22464e69475ac69b916dfe1307e&index=9&num=1',
            "proxyMethod": 2,
            "proxyType": "socks5",
            "host": self.proxy_server,
            "port": self.proxy_port,
            "proxyUserName": self.proxy_username,
            "proxyPassword": self.proxy_password,
            "duplicateCheck":1,
            'dynamicIpChannel': 'common',
            'isDynamicIpChangeIp': True,
            "browserFingerPrint": {},
            "isIpCreateLanguage ": False,
            "languages":'zh-HK',
            # "platform":"https://www.facebook.com",
            # "userName":phone,
            # "password":fb_password,
            "remark":remark
        }
        self.browser_id = createBrowser(json_data)
        self.logger.info(f'create browser:{self.browser_id}')
        return self.browser_id

    def _get_proxy_info(self):
        proxy_type = self.browser_data.get('proxyType')
        proxy_host = self.browser_data.get('host')
        proxy_port = self.browser_data.get('port')
        proxy_user = self.browser_data.get('proxyUserName')
        proxy_pass = self.browser_data.get('proxyPassword')
        proxy_url = f'{proxy_type}://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}'

        return {
            "proxy_type":proxy_type,
            "proxy_host":proxy_host,
            "proxy_port":proxy_port,
            "proxy_user":proxy_user,
            "proxy_pass":proxy_pass,
            "proxy_url":proxy_url
        }
        

    def connect_browser(self,browser_id,capture = False):
        # 直接连接一个已有的浏览器环境
        
        open_res = openBrowser(browser_id)
        detail_res = fetchBrowserDetail(browser_id)
        
        driverPath = open_res['data']['driver']
        debuggerAddress = open_res['data']['http']
        
        print(driverPath)
        print(debuggerAddress)
        
        self.browser_data = detail_res.get('data')
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", debuggerAddress)
        chrome_service = Service(driverPath)
        
        if capture:
            chrome_options.set_capability("goog:loggingPrefs",{"performance": "ALL"})
            driver = webdriver.Chrome(
                service=chrome_service, 
                options=chrome_options,
            )
        else:
            driver = webdriver.Chrome(
                service=chrome_service, 
                options=chrome_options
            )
        
        self.logger.info(f'connect driver:{open_res}')
        
        self.driver = driver
        self.helper = SeleniumDriverHelper(self.driver)
        return driver
    
    