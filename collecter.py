# coding=utf8
import logging
import threading
import requests
import json
import config
from offers.appleadstech import Appleadstech
from offers.ichestnut import Ichestnut
from offers.hugoffers import Hugoffers


class myThread (threading.Thread):
    def __init__(self, name, collector):
        threading.Thread.__init__(self)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.collector = collector

    def run(self):
        self.logger.info("Starting " + self.name)
        self.collector.run()



class Collecter(object):
    def __init__(self, app):
        super(Collecter, self).__init__()
        self.app = app
        # self.api = "%s/3.0/admin/offer?API-Key=%s" % (config.domain, config.key)
        self.api = "%s/3.0/admin/offer" % config.domain
        self.headers = {
            "API-Key": config.key,
            # "Content-Type": "application/json"
        }

    def run(self):
        for x in xrange(1, 2): 
            offers = self.app.download(x)
            if not offers:
                return
            
            for offer in offers:
                print json.dumps(offer)
                files = {}
                if offer["logo"] != "":
                    logo = requests.get(offer["logo"])
                    if logo and logo.status_code == 200:
                        try:
                            files["logo"] = logo.content
                        except:
                            pass
                resp = requests.post(self.api, headers=self.headers, data=offer, files=files, timeout=15, verify=False)
                try:
                    print(resp)
                    content = resp.json()
                    print content
                except Exception as e:
                    print(e)

                if not resp or resp.status_code != 200:
                    resp = requests.post(self.api, headers=self.headers, data=offer, files=files, timeout=15, verify=False)
                
                try:
                    print(resp)
                    content = resp.json()
                    print content
                except Exception as e:
                    print(e)
            


def main():
    '''
    applead = Appleadstech()
    colletor1 = Collecter(applead)
    thread1 = myThread("applead-collector", colletor1)
    thread1.start()

    ichest = Ichestnut()
    colletor2 = Collecter(ichest)
    thread2 = myThread("ichest-collector", colletor2)
    thread2.start()
    '''

    hoffers = Hugoffers()
    colletor3 = Collecter(hoffers)
    thread3 = myThread("hugoffers-collector", colletor3)
    thread3.start()


if __name__ == '__main__':
    main()