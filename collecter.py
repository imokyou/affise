# coding=utf8
import logging
import threading
import requests
import json
import os
import csv
import urllib
import config
import time
from offers.appleadstech import Appleadstech
from offers.ichestnut import Ichestnut
from offers.hugoffers import Hugoffers
from dao import OfferDao


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
        self.find_api = "%s/3.0/offer" % config.domain
        self.list_api = "%s/3.0/offers" % config.domain
        self.list_limit = 50
        self.headers = {
            "API-Key": config.key,
            'content-type': 'application/x-www-form-urlencoded'
        }
        self.request_timeout = 30
        self.sleep_time = 60 * 10 * 6
        self.offerDao = OfferDao(app.advertiser)

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
        querys.append("external_offer_id=%s" % offer["external_offer_id"])


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

    def make_post(self, api, post_data):
        print "make post request: ", api
        resp = requests.request("POST", api, headers=self.headers, data=post_data, timeout=self.request_timeout, verify=False)
        return resp

    def make_get(self, api):
        print "make get request: ", api
        resp = requests.request("GET", api, headers=self.headers, timeout=self.request_timeout, verify=False)
        return resp

    def add(self, offer):
        print "create new offer", offer["title"]
        files = {}
        if offer["logo"] != "":
            try:
                logo = requests.get(offer["logo"], verify=False)
                files["logo"] = logo.content
            except:
                pass

        post_data = self.build_query(offer)
        print(post_data)
        resp = self.make_post(self.api, post_data)
        try:
            content = resp.json()
            return content
        except Exception as e:
            print(e)
            return None

    def update_offer_external_id(self, id, offer_external_id):
        api = "%s/%s" % (self.api, id)
        post_data = "external_offer_id=%s" % offer_external_id
        resp = self.make_post(api, post_data)
        try:
            content = resp.json()
            return content
        except Exception as e:
            print(e)
            return None

    def update_offer_status(self, id, status):
        print "update offer status", id, status

        api = "%s/%s" % (self.api, id)
        post_data = "status=%s" % status
        resp = self.make_post(api, post_data)
        try:
            content = resp.json()
            return content
        except Exception as e:
            print(e)
            return None

    def edit(self, offer):
        pass

    def find(self, offer_id):
        api = "%s/%s" % (self.find_api, offer_id)
        resp = self.make_get(api)
        try:
            content = resp.json()
            return content
        except Exception as e:
            print(e)
            return None

    def list(self, advertiser = "", page = 1, limit = 20):
        if limit == 0:
            limit = self.list_limit
        api = "%s?page=%s&limit=%s" % (self.list_api, page, limit)
        if advertiser != "":
            api = "%s&advertiser[]=%s" % (api, advertiser)
        
        resp = self.make_get(api)
        try:
            content = resp.json()
            return content
        except Exception as e:
            print(e)
            return None

    def list_all(self, advertiser = ""):
        result = {"offers": []}
        for x in xrange(1, 10):
            resp = self.list(advertiser, x)
            if not resp or not resp["offers"]:
                break

            result["offers"].extend(resp["offers"])

            if resp["pagination"]["total_count"] <= self.list_limit:
                break
        return result

    def store_offer_external_id(self, advertiser):
        resp = self.list_all(advertiser)
        if not resp or not resp["offers"]:
            return

        self.offerDao.ids_store_clear()
        for r in resp["offers"]:
            # print(r["id"], r["offer_id"], r["external_offer_id"])
            self.offerDao.ids_store_append(r["id"], r["offer_id"], r["external_offer_id"])


    def run(self):
        '''
        resp = self.update_offer_external_id("117534", "373032")
        print(resp)
        '''
        
        '''
        resp = self.find("117533")
        print(resp)
        '''
        '''
        resp = self.list_all("5df8c50410768e44b351cc66")
        print resp
        '''
        while True:
            self.store_offer_external_id(self.app.advertiser)
            for x in xrange(1, 10): 
                offers = self.app.download(x)
                if not offers:
                    return
                
                for offer in offers:
                    print offer["external_offer_id"]
                    ids = self.offerDao.find_by_external_id(offer["external_offer_id"])
                    if not ids:
                        resp = self.add(offer)
                    else:
                        self.update_offer_status(ids[0], offer["status"])
                    time.sleep(3)
            print "sleep", self.sleep_time, "seconds..."
            time.sleep(self.sleep_time)
                    


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