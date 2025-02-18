
import random
import time
from faker import Faker
from main import SeleniumDriverHelper
from modules.browser_control import BrowserControl
from modules.facebook_operate import FacebookOperate
from tools.sms import Sms
from tools.bit_api import updateBrowser,deleteBrowser
# for selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
# for log
import logging
from rich.console import Console
from rich.logging import RichHandler

# console = Console()
# logging.basicConfig(
#     level="INFO",  # 设置日志级别
#     format="%(message)s",  # 设置日志格式
#     datefmt="%Y/%m/%d %H:%M:%S",  # 设置时间格式
#     handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True, show_path=False)]  # 使用RichHandler
# )
log = logging.getLogger(__name__)


class FacebookRegister:
    # 初始化注册信息
    faker = Faker('zh_TW') # 注册名字:zh_TW繁体
    sms_server_url = "https://api.haozhuma.com"
    sms_username = "8641aaa8e3197ff75449ad3b54dc9136e573b9e7f280fadffe58023a4c0dc68d"
    sms_password = "8641aaa8e3197ff7150ddb38c3cb329295debacbf298ad842c031ed923404594"
    sms_sid = 72510 # 对接项目码
    browser_group_id = '2c9bc04790aae7ca0190b5cb34182ea7' # 新注册id


    
    def __init__(self,browser_id = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver = None
        self.helper = None
        self.browser_id = None
        self._init_sms()
        self._init_reg_info()
        self._init_browser(browser_id)
    
    def _init_sms(self):
        self.sms = Sms(server_url=self.sms_server_url, 
                       username=self.sms_username, 
                       password=self.sms_password,
                       sid=self.sms_sid)


    def _init_reg_info(self):
        self.name = self.faker.name_female()
        self.firstname = self.name[1:]
        self.lastname = self.name[0:1]
        self.year = str(random.randint(1985,2005))
        self.month = str(random.randint(1,12))
        self.day = str(random.randint(1,28))
        self.fb_password = self.faker.password(length=15, special_chars=False, digits=True, upper_case=True, lower_case=True)


    def _init_browser(self,browser_id):
        self.phone = self.sms.get_phone(
            exclude='192'
            # ascription='1',
            # paragraph='167'
            # province='34'
        )
        self.win_name = f'facebook-{self.phone}'
        self.reg_info = f'{self.phone},{self.firstname},{self.lastname},{self.year},{self.month},{self.day},{self.fb_password}'
        self.logger.info(f'获取手机号码[{self.phone}]-->{self.reg_info}')
        
        
        bc = BrowserControl()
        if not browser_id:
            browser_id = bc.create_browser(
                borwser_name=self.win_name,
                remark=self.reg_info
            )
        driver = bc.connect_browser(browser_id)
        self.driver = bc.driver
        self.helper = bc.helper
        self.browser_id = browser_id
        return driver

    def _click_home_reg_btn(self,driver):
        创建账户Xpath = '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[5]/a'
        self.helper.wait_until_appear(By.XPATH,创建账户Xpath)
        reg_button = self.helper.find_or_fail(By.XPATH,创建账户Xpath)
        time.sleep(random.uniform(6,12))
        reg_button.click()
        time.sleep(random.uniform(6,12))

    def _input_reg_form(self,driver,phone,lastname,firstname,password,year,month,day):
        username_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "reg_email__"))
        )
        lastname_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "lastname"))
        )
        firstname_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "firstname"))
        )
        password_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "reg_passwd__"))
        )
        year_choose = Select(WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "birthday_year"))
        ))
        month_choose = Select(WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "birthday_month"))
        ))

        day_choose = Select(WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "birthday_day"))
        ))
        sex_click = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "sex"))
        )
        time.sleep(random.uniform(2,3))
        lastname_input.send_keys(lastname)
        time.sleep(random.uniform(2,3))
        firstname_input.send_keys(firstname)
        time.sleep(random.uniform(2,3))
        username_input.send_keys(phone)
        time.sleep(random.uniform(2,3))
        password_input.send_keys(password)
        time.sleep(random.uniform(2,3))
        year_choose.select_by_value(year)
        time.sleep(random.uniform(2,3))
        month_choose.select_by_value(month)
        time.sleep(random.uniform(2,3))
        day_choose.select_by_value(day)
        time.sleep(random.uniform(2,3))
        sex_click.click() # 默认注册女性

    def _submit_reg(self,driver):
        # time.sleep(random.uniform(3,10))
        submit_reg = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "websubmit"))
        )
        time.sleep(random.uniform(2,3))
        submit_reg.click()
        time.sleep(random.uniform(4,10))
        submit_reg.click()
        time.sleep(random.uniform(10,20))

    def _submit_reg_check(self,driver) -> bool:
        
        url = driver.current_url
        if url == 'https://www.facebook.com/':
            error = self.helper.find_or_fail(By.ID,"reg_error_inner")
            if error:
                logging.info(f"注册失败,提交注册出现拦截:{error.text}")
                return False
        else:
            logging.info(f"提交成功,进入新页面{url}")
            if 'checkpoint' in url:
                logging.info(f"注册失败,账号需要申诉验证")
                return False
            # reg_tip_span = WebDriverWait(driver, 30).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "uiHeaderTitle"))
            # )
            # tip = reg_tip_span.text
            # if tip != '輸入短訊中的確認碼':
            #     logging.info(f"注册失败~{tip},号码拉黑")
            #     return False
            # else:
            #     logging.info(f"注册成功：接收短信验证码")
            #     return True

            return True

    def _resend_sms_code(self,driver):
        #长时间接收不到验证码处理--重发
        resend_btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.LINK_TEXT, "再次發送短訊"))
        )
        resend_btn.click()
        time.sleep(random.uniform(10,25))
        try:
            resend_btn = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.LINK_TEXT, "好"))
            )
            resend_btn.click()
            return True
        except Exception as e:
            logging.error("重发短信失败")
        return False

    def _submit_sms_code(self,driver,sms_code):
        sms_input = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "code"))
        )
        sms_input.send_keys(sms_code)
        time.sleep(random.uniform(2,6))
        success_reg_btn = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "confirm"))
        )
        success_reg_btn.click()
    
    def _reg_success_confirm(self,driver):
        time.sleep(random.uniform(2,6))
        success_reg_btn = WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.LINK_TEXT, "確定"))
        )
        success_reg_btn.click()
    
    # def _reg_success_check(self,driver):
    #     success_reg_btn = WebDriverWait(driver, 90).until(
    #         EC.presence_of_element_located((By., "確定"))
    #     )
    #     success_reg_btn.click()
        
    def _fetch_profile_id(driver):
        url = 'https://www.facebook.com/profile.php'
        driver.get('https://www.facebook.com/')
        
    def start_reg(self):
        driver = self.driver
        sms_code = None
        
        # 进行页面打开、打开表单页面
        def open_page_form():
            driver.get('https://www.facebook.com/')
            self._click_home_reg_btn(driver)
            self._input_reg_form(driver,phone=f"86{self.phone}",
                        lastname=self.lastname,
                        firstname=self.firstname,
                        password=self.fb_password,
                        year=self.year,
                        month=self.month,
                        day=self.day)
            return True
        open_result = False
        try:
            open_result = open_page_form()
        except Exception as e:
            self.logger.info("打开填写表单失败-->重试")
            pass
        
        try:
            if not open_result:
                open_result = open_page_form()
                if not open_result:
                    return False
        except Exception as e:
            self.logger.error(f'二次打开表单失败[{e}]-->{self.win_name}')
            self.sms.release_phone(self.phone)
            deleteBrowser(self.browser_id)
            return
        self.logger.info(f"打开表单成功,填写完毕,提交注册")
        
        # 进行提交注册操作
        try:
            self._submit_reg(driver)
            submit_result = self._submit_reg_check(driver)
            assert submit_result,'注册失败'
            time.sleep(random.uniform(5,20))
        except Exception as e:
            self.logger.error(f'提交注册异常:{e}-拉黑号码->{self.win_name}')
            self.sms.blacklist_phone(self.phone)
            deleteBrowser(self.browser_id)
            return
        
        # 提交成功 进行发信
        try:
            resend = self._resend_sms_code(driver)
            if resend:
                for i in range(15):
                    time.sleep(5)
                    sms_res = self.sms.get_message(self.phone)
                    if isinstance(sms_res,dict) and sms_res.get('yzm'):
                        sms_code = sms_res.get('yzm')
                        self.logger.info(f"获取手机验证码:{sms_code}")
                        break
                if not sms_code:
                    assert False,'接收不到短信作废拉黑删除窗口'
            else:
                assert False,'提交注册发送短信失败作废删除窗口'
        except Exception as e:
            self.logger.error(f'进行发信异常:{e}-请确认->{self.win_name}')
            self.sms.blacklist_phone(self.phone)
            deleteBrowser(self.browser_id)
            return
        
        # 获取验证码成功、输入验证码、提交注册
        try:
            self._submit_sms_code(driver,sms_code)
            self._reg_success_confirm(driver)
        except Exception as e:
            self.logger.error(f'短信验证异常[{e}]-->验证码:{sms_code}')

        # 打开主页，更新自己的fb id
        fo = FacebookOperate(self.browser_id)
        fb_id = fo.fetch_facebook_id()
        new_browser_data = {"name":fb_id}
        fo.browser_control.update_browser_info(**new_browser_data)
        # fo.update_
        
if __name__ == '__main__':
    for i in range(10):
        fb_reg = FacebookRegister()
        fb_reg.start_reg()
        
    # TEST 
    # fb_reg = FacebookRegister()
    # browser_id = 'aa855a11b1af4348af2158b50ff1f766'
    # driver = fb_reg._connect_selenium(browser_id)
    
    # fb_reg._click_home_reg_btn(driver)
    
    # fo = FacebookOperate('9626177c30364545bc1685f822cdbf44')
    # fb_id = fo.fetch_facebook_id()
    # new_browser_data = {"name":fb_id}
    # fo.browser_control.update_browser_info(**new_browser_data)