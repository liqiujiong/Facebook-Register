import requests
import json
import time

# 官方文档地址
# https://doc2.bitbrowser.cn/jiekou/ben-di-fu-wu-zhi-nan.html

# 此demo仅作为参考使用，以下使用的指纹参数仅是部分参数，完整参数请参考文档

url = "http://127.0.0.1:54345"
headers = {'Content-Type': 'application/json'}


def createBrowser(json_data):  # 创建或者更新窗口，指纹参数 browserFingerPrint 如没有特定需求，只需要指定下内核即可，如果需要更详细的参数，请参考文档
    res = requests.post(f"{url}/browser/update",
                        data=json.dumps(json_data), headers=headers).json()
    browserId = res['data']['id']
    return browserId


def updateBrowser(ids,browserFingerPrint={},**kwargs):  
    # 更新窗口，支持批量更新和按需更新，ids 传入数组，单独更新只传一个id即可，只传入需要修改的字段即可，比如修改备注，具体字段请参考文档，browserFingerPrint指纹对象不修改，则无需传入
    json_data = {'ids': ids,
                 'browserFingerPrint': browserFingerPrint,
                 **kwargs
                 }
    res = requests.post(f"{url}/browser/update/partial",
                        data=json.dumps(json_data), headers=headers).json()
    return res


def openBrowser(id):  # 直接指定ID打开窗口，也可以使用 createBrowser 方法返回的ID
    json_data = {"id": f'{id}'}
    res = requests.post(f"{url}/browser/open",
                        data=json.dumps(json_data), headers=headers).json()
    return res

def closeBrowser(id):  # 关闭窗口
    json_data = {'id': f'{id}'}
    requests.post(f"{url}/browser/close",
                  data=json.dumps(json_data), headers=headers).json()


def deleteBrowser(id):  # 删除窗口
    json_data = {'id': f'{id}'}
    print(requests.post(f"{url}/browser/delete",
          data=json.dumps(json_data), headers=headers).json())

def fetchBrowserList(page=0,pageSize=100,groupId=None,name=None,remark=None):
    json_data = {
        "page": page,
        "pageSize": pageSize
    }
    if groupId: json_data['groupId'] = groupId
    if name: json_data['name'] = name
    if remark: json_data['remark'] = remark
    res = requests.post(f"{url}/browser/list",
                        data=json.dumps(json_data), headers=headers).json()
    return res.get('data')

def fetchBrowserDetail(id):
    json_data = {
        "id": f'{id}'
    }
    res = requests.post(f"{url}/browser/detail",
                        data=json.dumps(json_data), headers=headers).json()
    return res



if __name__ == '__main__':
    # browser_id = createBrowser()
    # openBrowser(browser_id)

    # time.sleep(10)  # 等待10秒自动关闭窗口

    # closeBrowser(browser_id)

    # time.sleep(10)  # 等待10秒自动删掉窗口

    # deleteBrowser(browser_id)
    # res = fetchBrowserList()
    # print(res)

    data = {
        "name":'hello'
    }
    updateBrowser(["9626177c30364545bc1685f822cdbf44"],{},**data)
