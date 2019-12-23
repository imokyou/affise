# coding=utf8
import logging
import threading
import requests
import json
import urllib
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
            'content-type': 'application/x-www-form-urlencoded'
        }

    def build_query(self, offer):
        querys = []
        querys.append("title=%s" % offer["title"])
        querys.append("advertiser=%s" % offer["advertiser"])
        querys.append("url=%s" % urllib.quote(offer["url"]))
        querys.append("url_preview=%s" % offer["url_preview"])
        querys.append("stopDate=%s" % offer["stopDate"])
        querys.append("start_at=%s" % offer["start_at"])
        querys.append("status=%s" % offer["status"])
        querys.append("is_cpi=%s" % offer["is_cpi"])


        for x in xrange(len(offer["payments"])):
            querys.append("payments[%s][goal]=%s" % (x, 1))
            querys.append("payments[%s][total]=%s" % (x, offer["payments"][x]['total']))
            querys.append("payments[%s][currency]=%s" % (x, offer["payments"][x]['currency']))
            querys.append("payments[%s][revenue]=%s" % (x, offer["payments"][x]['revenue']))
            querys.append("payments[%s][type]=%s" % (x, offer["payments"][x]['type']))

        for x in xrange(len(offer["caps"])):
            querys.append("caps[%s][affiliate_type]=%s" % (x, offer["caps"][x]['affiliate_type']))
            querys.append("caps[%s][goal_type]=%s" % (x, offer["caps"][x]['goal_type']))
            querys.append("caps[%s][period]=%s" % (x, offer["caps"][x]['period']))
            querys.append("caps[%s][type]=%s" % (x, offer["caps"][x]['type']))
            querys.append("caps[%s][value]=%s" % (x, offer["caps"][x]['value']))

        for x in xrange(len(offer["targeting"])):
            for k in xrange(len(offer["targeting"][x]["country"]["allow"])):
                country_allow = offer["targeting"][x]["country"]["allow"][k]
                querys.append("targeting[%s][country][allow][%s]=%s" % (x, k, country_allow))

        return "&".join(querys)

    
    def run(self):
        for x in xrange(2, 3): 
            offers = self.app.download(x)
            if not offers:
                return
            
            for offer in offers:
                # print json.dumps(offer)
                files = {}
                if offer["logo"] != "":
                    try:
                        logo = requests.get(offer["logo"], verify=False)
                        files["logo"] = logo.content
                    except:
                        pass

                post_data = self.build_query(offer)
                print(post_data)
                resp = requests.request("POST", self.api, headers=self.headers, data=post_data, timeout=15, verify=False)
                try:
                    print(resp)
                    content = resp.json()
                    print content
                    print resp.text
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