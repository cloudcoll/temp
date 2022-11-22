import json
import queue
import requests
import time
requests.packages.urllib3.disable_warnings()

class AwvsScan(object):
    def __init__(self):
        self.scanner = "https://152.32.145.124:3443"
        self.api = '1986ad8c0a5b3df4d7028d5f3c06e936ca7b4345c1bca401297bcba358437af39'
        self.ScanMode = '11111111-1111-1111-1111-111111111111'
        self.headers = {'X-Auth': self.api, 'content-type': 'application/json'}
        self.targets_id = queue.Queue()
        self.scan_id = queue.Queue()
        self.site = queue.Queue()

    def main(self):
        print('='*30)
        print("""1、use target.txt add targets\n2、Scan targets\n3、delete all targets\n4、use target.txt add targets and scan""")
        print('='*30)
        choice = input(">")
        if choice == '1':
           self.targets()
        if choice == '2':
            self.scans()
        if choice == '3':
            self.del_targets()
        if choice == '4':
            self.targets()
            self.scans()
        self.main()

    def openfile(self):
        with open('target.txt') as cent:
            for web_site in cent:
                web_site = web_site.strip('\n\r')
                self.site.put(web_site)

    def targets(self):
        self.openfile()
        while not self.site.empty():
            website = self.site.get()
            try:
                data = {'address':website,
                        'description':'awvs-auto',
                        'criticality':'10'}
                response = requests.post(self.scanner + '/api/v1/targets', data=json.dumps(data), headers=self.headers, verify=False)
                cent = json.loads(response.content)
                target_id = cent['target_id']
                self.targets_id.put(target_id)
            except Exception as e:
                print('Target is not website! {}'.format(website))

    def scans(self):
        while not self.targets_id.empty():
            data = {'target_id' : self.targets_id.get(),
                    'profile_id' : self.ScanMode,
                    'schedule' : {'disable': False, 'start_date': None, 'time_sensitive' : False}}

            response = requests.post(self.scanner + '/api/v1/scans', data=json.dumps(data), headers=self.headers, allow_redirects=False, verify=False)
            if response.status_code == 201:
                cent = response.headers['Location'].replace('/api/v1/scans/','')
                print(cent)
            r = requests.get(url=self.scanner + '/api/v1/me/stats', headers=headers, verify=False).json()
            runnum = int(r['scans_running_count']) # 正在扫描的个数
            if runnum < 10:
                time.sleep(60)

    def get_targets_id(self):
        response = requests.get(self.scanner + "/api/v1/targets", headers=self.headers, verify=False)
        content = json.loads(response.content)
        for cent in content['targets']:
            self.targets_id.put([cent['address'],cent['target_id']])

    def del_targets(self):
        while True:
            self.get_targets_id()
            if self.targets_id.qsize() == 0:
                break
            else:
                while not self.targets_id.empty():
                    targets_info = self.targets_id.get()
                    response = requests.delete(self.scanner + "/api/v1/targets/" + targets_info[1], headers=self.headers, verify=False)
                    if response.status_code == 204:
                        print('delete targets {}'.format(targets_info[0]))

if __name__ == '__main__':
    Scan = AwvsScan()
    Scan.main()