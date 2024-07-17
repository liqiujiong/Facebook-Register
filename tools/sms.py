import requests
import time

class Sms:
    def __init__(self, server_url, username, password,sid = 72510):
        self.server_url = server_url
        self.username = username
        self.password = password
        self.sid = sid
        self.token = None
        self.login()

    def login(self):
        url = f"{self.server_url}/sms/?api=login&user={self.username}&pass={self.password}"
        response = requests.get(url)
        data = response.json()
        print(data)
        if data.get('code') == 0:
            self.token = data.get('token')
        else:
            raise Exception(f"Login failed: {data.get('msg')}")

    def get_summary(self):
        url = f"{self.server_url}/sms/?api=getSummary&token={self.token}"
        response = requests.get(url)
        data = response.json()
        print(data)
        if data.get('code') == 0:
            return data
        else:
            raise Exception(f"Failed to get summary: {data.get('msg')}")

    def get_phone(self, isp=None, province=None, ascription=None, paragraph=None, exclude=None, uid=None, author=None):
        url = f"{self.server_url}/sms/?api=getPhone&token={self.token}&sid={self.sid}"
        params = {
            'isp': isp,
            'Province': province,
            'ascription': ascription,
            'paragraph': paragraph,
            'exclude': exclude,
            'uid': uid,
            'author': author
        }
        response = requests.get(url, params={k: v for k, v in params.items() if v is not None})
        data = response.json()
        # print(data)
        if data.get('code') == '0':
            phone = data.get('phone')
            return phone
        else:
            raise Exception(f"Failed to get phone: {data.get('msg')}")

    def get_message(self, phone, sid = None):
        if not sid:
            sid = self.sid
        url = f"{self.server_url}/sms/?api=getMessage&token={self.token}&sid={sid}&phone={phone}"
        response = requests.get(url)
        data = response.json()
        print(data)
        if data.get('code') == "0":
            return data
        elif data.get('code') == -1:
            # 等待短信
            if data.get('msg')!='等待':
                raise Exception(f"Failed to get message: {data.get('msg')}")
            return data
        else:
            raise Exception(f"Failed to get message: {data.get('msg')}")

    def get_message_retry(self, phone, timeout=60, interval=5):
        start_time = time.time()
        count = 1
        while time.time() - start_time < timeout:
            url = f"{self.server_url}/sms/?api=getMessage&token={self.token}&sid={self.sid}&phone={phone}"
            response = requests.get(url)
            data = response.json()
            print(f"{phone}-->第{count}次获取手机验证码:{data.get('msg')}")
            if data.get('code') == "0":
                print(data)
                return data
            if data.get('code') == -1 and data.get('msg') != '等待':
                raise Exception(f"Failed to get message: {data.get('msg')}")
            time.sleep(interval)
        print(f"{phone}-->获取不到手机验证码")
        raise TimeoutError("Failed to get message within the specified timeout period")

    def release_phone(self, phone):
        url = f"{self.server_url}/sms/?api=cancelRecv&token={self.token}&sid={self.sid}&phone={phone}"
        response = requests.get(url)
        data = response.json()
        if data.get('code') == 0:
            return data
        else:
            raise Exception(f"Failed to release phone: {data.get('msg')}")

    def release_all_phones(self):
        url = f"{self.server_url}/sms/?api=cancelAllRecv&token={self.token}"
        response = requests.get(url)
        data = response.json()
        if data.get('code') == 0 or data.get('code') == 200:
            print("释放所有手机号码")
            return data
        else:
            raise Exception(f"Failed to release all phones: {data.get('msg')}")
        

    def blacklist_phone(self, phone):
        url = f"{self.server_url}/sms/?api=addBlacklist&token={self.token}&sid={self.sid}&phone={phone}"
        response = requests.get(url)
        data = response.json()
        if data.get('code') == 0:
            return data
        else:
            raise Exception(f"Failed to blacklist phone: {data.get('msg')}")