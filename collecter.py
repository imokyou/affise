# coding=utf8
import traceback
import logging
import threading
import requests
import json
import signal
import os
import csv
import urllib
import config
import time
from offers.appleadstech import Appleadstech
from offers.ichestnut import Ichestnut
from offers.hugoffers import Hugoffers
from offers.duunion import DuunionOffers
from offers.duunion2 import DuunionOffers2
from offers.vinsmok import Vinsmok
from offers.mobisummer import Mobisummer
from offers.interestmob import Interestmob
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
        self.request_timeout = 120
        self.sleep_time = 60 * 10 * 6
        self.offerDao = OfferDao(app.advertiser)

    def build_query(self, offer):
        querys = []
        querys.append("title=%s" % urllib.quote(offer["title"]))
        querys.append("advertiser=%s" % offer["advertiser"])
        querys.append("url=%s" % urllib.quote(offer["url"]))
        querys.append("url_preview=%s" % urllib.quote(offer["url_preview"]))
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
        try:
            print self.app.name, "create new offer", offer["title"].encode("utf8"), offer['external_offer_id']
            files = {}
            if offer["logo"] != "":
                try:
                    logo = requests.get(offer["logo"], verify=False)
                    files["logo"] = logo.content
                except:
                    pass

            post_data = self.build_query(offer)
            resp = self.make_post(self.api, post_data)
            return resp.json()
        except:
            traceback.print_exc()
            pass
        

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

    def update_offer_status(self, id, status, url=""):
        print "update offer status", id, status, url

        api = "%s/%s" % (self.api, id)
        
        post_data = "status=%s" % status
        if url != "":
            post_data += "&url=%s" % urllib.quote(url)
        resp = self.make_post(api, post_data)
        print resp
        # print resp.json()
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

    def list(self, advertiser = "", page = 1, limit = 200):
        if limit == 0:
            limit = self.list_limit
        api = "%s?status[]=active&page=%s&limit=%s" % (self.list_api, page, limit)
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
        for x in xrange(1, 50):
            resp = self.list(advertiser, x)
            if not resp or not resp["offers"]:
                break

            print(len(resp["offers"]))

            result["offers"].extend(resp["offers"])
        return result

    def store_offer_external_id(self, advertiser):
        resp = self.list_all(advertiser)
        if not resp or not resp["offers"]:
            return

        self.offerDao.ids_store_clear()
        for r in resp["offers"]:
            # print(r["id"], r["offer_id"], r["external_offer_id"])
            self.offerDao.ids_store_append(r["id"], r["offer_id"], r["external_offer_id"], r["status"])

    def get_offer_external_ids(self, advertiser):
        return self.offerDao.get_all()

    def get_all_external_offers(self):
        external_offers = {}
        for x in xrange(1, 10): 
            offers = self.app.download(x)
            if not offers:
                return external_offers
            
            for offer in offers:
                external_offers[offer['external_offer_id']] = offer
        return external_offers


    def run(self):
        while True:
            self.store_offer_external_id(self.app.advertiser)
            all_offers = self.get_offer_external_ids(self.app.advertiser)
            all_external_offers = self.get_all_external_offers()
            
            not_exists_offers = {}
            exists_offers = {}
            for ext_id, v in all_offers.items():
                if not all_external_offers.has_key(ext_id):
                    not_exists_offers[ext_id] = v
                    if v[3] == "active":
                        self.update_offer_status(v[0], "stopped")
                else:
                    ov  = all_external_offers[ext_id]
                    self.update_offer_status(v[0], "active", ov["url"])
                    exists_offers[ext_id] = v

            for ext_id, v in all_external_offers.items():
                ids = self.offerDao.find_by_external_id(v["external_offer_id"])
                if not ids:
                    resp = self.add(v)
                    print resp
                    break
                    # pass
                else:
                    print "offer exists", ext_id, v["external_offer_id"]
            
            print len(not_exists_offers), len(exists_offers), len(all_offers), len(all_external_offers)
            break
            time.sleep(60 * 30)
                    

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

    try:
        signal.signal(signal.SIGINT, quit)
        signal.signal(signal.SIGTERM, quit)


        # offerApp1 = Hugoffers()
        # colletor1 = Collecter(offerApp1)
        # thread1 = myThread("Hugoffers-collector", colletor1)
        # thread1.setDaemon(True)
        # thread1.start()

        # offerApp2 = DuunionOffers()
        # colletor2 = Collecter(offerApp2)
        # thread2 = myThread("DuunionOffers-collector", colletor2)
        # thread2.setDaemon(True)
        # thread2.start()

        # offerApp3 = DuunionOffers2()
        # colletor3 = Collecter(offerApp3)
        # thread3 = myThread("DuunionOffers2-collector", colletor3)
        # thread3.setDaemon(True)
        # thread3.start()

        # offerApp4 = Appleadstech()
        # colletor4 = Collecter(offerApp4)
        # thread4 = myThread("Appleadstech-collector", colletor4)
        # thread4.setDaemon(True)
        # thread4.start()

        # offerApp5 = Vinsmok()
        # colletor5 = Collecter(offerApp5)
        # thread5 = myThread("Vinsmok-collector", colletor5)
        # thread5.setDaemon(True)
        # thread5.start()

        # offerApp6 = Mobisummer()
        # colletor6 = Collecter(offerApp6)
        # thread6 = myThread("Mobisummer-collector", colletor6)
        # thread6.setDaemon(True)
        # thread6.start()

        offerApp7 = Interestmob()
        colletor7 = Collecter(offerApp7)
        thread7 = myThread("Interestmob-collector", colletor7)
        thread7.setDaemon(True)
        thread7.start()

        while True:
            pass
    except KeyboardInterrupt, e:
        print "you stop the threading"


if __name__ == '__main__':
    main()