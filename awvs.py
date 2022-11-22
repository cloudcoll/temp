import requests
import json
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


awvs_token = '1986ad8c0a5b3df4d7028d5f3c06e936ca7b4345c1bca401297bcba358437af39'
website = "https://152.32.145.124:3443"
domain_list = []

def awvs_reaper(domainlist):# 接受域名list类型
    headers = {
        'X-Auth': awvs_token,
        'Content-type': 'application/json;charset=utf8'
    }

    api_running_url = website + '/api/v1/me/stats'
    api_add_url = website + "/api/v1/targets"
    api_run_url = website + "/api/v1/scans"

    # 先把所有任务添加上并调整速度
    target_list = []
    for target in domainlist:
        data = '{"address":"%s","description":"create_by_reaper","criticality":"10"}'% target
        r = requests.post(url=api_add_url, headers=headers, data=data, verify=False).json()
        target_id = r['target_id']
        api_speed_url = website+"/api/v1/targets/{}/configuration".format(target_id)
        data = json.dumps({"scan_speed":"fast"})# slow最慢，一般建议fast
        r = requests.patch(url=api_speed_url, headers=headers, data=data, verify=False)
        target_list.append(target_id)

    target_num = len(target_list)

    r = requests.get(url=api_running_url, headers=headers, verify=False).json()
    runnum = int(r['scans_running_count']) # 正在扫描的个数
    flag = 0 # 做数组标志位
    while flag < target_num:
        if runnum < 4:
            target_id = target_list[flag]
            flag = flag + 1
            data = '{"profile_id":"11111111-1111-1111-1111-111111111111","schedule":{"disable":false,"start_date":null,"time_sensitive":false},"target_id":"%s"}'% target_id
            r = requests.post(url=api_run_url, headers=headers, data=data, verify=False).json()
            r = requests.get(url=api_running_url, headers=headers, verify=False).json()
            runnum = int(r['scans_running_count']) # 正在扫描的个数
        else:
            pass
        time.sleep(60)
    return target_num


def openfile(filename):
    with open(filename) as cent:
        for web_site in cent:
            web_site = web_site.strip('\n\r')
            domain_list.append(web_site)
    return domain_list





if __name__ == "__main__":
    domain_list = openfile('target.txt')      # 必须带http或者https
    awvs_reaper(domain_list)



# linux服务器配合screen持久化运行

#注意，无授权请勿扫描，后果自负