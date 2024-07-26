
import time
from selenium.webdriver.common.by import By

from modules.browser_control import BrowserControl
from tools.selenium_driver_helper import SeleniumDriverHelper
from tools.sercury import get_2fa_code

class FacebookOperate:
    def __init__(self,browser_id,capture = False) -> None:
        self.browser_control = BrowserControl()
        self.driver = self.browser_control.connect_browser(browser_id,capture)
        self.helper = SeleniumDriverHelper(self.driver)
        
    def fetch_facebook_id(self):
        self.driver.get('https://www.facebook.com/profile.php')
        if '?id=' in self.driver.current_url:
            return self.driver.current_url.split('=')[-1]
        else:
            return None
        
    def add_email(self):
        pass
    
    def add_2fa(self):
        helper = self.helper
        
        def _open_2fa_bind(driver):
            # url = 'https://accountscenter.facebook.com/password_and_security'
            url = 'https://accountscenter.facebook.com/password_and_security/two_factor/'
            driver.get(url)

        def _click_2fa_account():
            点击用户xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div/div/div/div/div/div[3]/div[2]/div[4]/div/div/div[2]/div/div/div[1]'
            res = helper.find_or_fail(By.XPATH,点击用户xpath)
            res.click()
            time.sleep(2)

        def _2fa_checkout_password(password):
            res = helper.find_or_fail(By.XPATH, '//input[@type="password"]')
            res.send_keys(password)

            密码确认按钮xpath = '/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div/div/div[4]/div[3]/div/div/div/div/div/div'
            time.sleep(2)
            res = helper.find_or_fail(By.XPATH,密码确认按钮xpath)
            res.click()
            time.sleep(2)

        def _fetch_2fa_key() -> str:
            
            选择密保方式继续按钮xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div/div/div/div[2]/div/div[4]/div[3]/div/div/div/div/div/div/div/div'
            res = helper.find_or_fail(By.XPATH,选择密保方式继续按钮xpath)
            res.click()
            
            time.sleep(10)
            
            令牌密钥xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div/div/div/div[3]/div/div[3]/div[2]/div[4]/div/div/div[4]/div/div[2]/div/div/div[1]/span'
            res = helper.find_or_fail(By.XPATH,令牌密钥xpath)
            otp_key = res.text
            
            令牌密钥下一步按钮xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div/div/div/div[3]/div/div[4]/div[3]/div/div/div/div/div'
            res = helper.find_or_fail(By.XPATH,令牌密钥下一步按钮xpath)
            res.click()
            
            time.sleep(2)
            return otp_key

        def _check_2fa_code(code):
            input_elements = helper.find_or_fail(By.XPATH, '//input[@type="text"]')
            input_elements.send_keys(code)
            time.sleep(3)
            令牌确认下一步按钮xpath = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[2]/div/div/div/div/div/div[4]/div/div[4]/div[3]/div/div/div/div/div/div/div/div'
            res = helper.find_or_fail(By.XPATH,令牌确认下一步按钮xpath)
            res.click()
                
        _open_2fa_bind(self.driver)
        _click_2fa_account()
        password = 'wDRHzyuk0EPJy8M'
        _2fa_checkout_password(password)
        otp_key = _fetch_2fa_key()
        otp_code = get_2fa_code(otp_code=otp_key)
        print(otp_code)
        _check_2fa_code(otp_code)