# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import logging
import json
from datetime import datetime


class Hugoffers(object):
    domain = "http://tapcrane.hoapi0.com"
    key = "1d72fd30c41a487d9b798408148cc5fa"
    advertiser = "5df8c50410768e44b351cc66"
    api = ""
    timeout = 15
    limit = 20
    logger = None
    price_lower = 0.2
    payment_percent = 0.5
    
    statusMap = {
        "RUNNING": "active"
    }


    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info("Hugoffers init...")

    def set_api(self, query):
        self.api = "%s/v1?cid=tapcrane&token=%s%s" % (self.domain, self.key, query)

    def make_request(self, page):
        query = "&page=%s,%s" % (self.limit, page)
        self.set_api(query)
        self.logger.info("download offers from %s" % self.api)
        resp = requests.get(self.api, timeout=self.timeout)
        if not resp:
            self.logger.info("download fail %s, try again" % self.api)
            resp = requests.get(self.api, timeout=self.timeout)
        return resp

    def match_price_lower(self, price):
        if float(price) < self.price_lower:
            return False

        return True

    def extrace_offer_creatvies(self, d):
        creatives = []
        for c in d['creative_link']:
            creatives.append(c['url'])
        return creatives

    def extrace_offer_logo(self, d):
        logo = None
        if d["icon_link"] != "":
            logo = d["icon_link"]
        return logo

    def extrace_offer_caps(self, d):
        caps = []
        if d["daily_cap"] != 0:   
            caps.append({
                "affiliate_type": "all",
                "goal_type": "all",
                "period": "day",
                "type": "conversions",
                "value": d["daily_cap"]
            })
        return caps

    def cal_channel_payment(self, price):
        return price * self.payment_percent


    def extrace_offer_payments(self, d):
        payments = []
        payments.append({
            "goal": "1",
            "total": d["price"],
            "currency": "USD",
            "type": "fixed",
            "revenue": self.cal_channel_payment(d["price"])
        })
        return payments

    def extrace_offer_targeting(self, d):
        targets = {
            "country": {"allow":[], "deny":[]},
            # "region": {"allow":[], "deny":[]},
            # "city": {"allow":[], "deny":[]},
            # "os": {"allow":[], "deny":[]},
            # "isp": {"allow":[], "deny":[]},
            # "ip": {"allow":[], "deny":[]},
            # "browser": {"allow":[], "deny":[]},
            # "brand": {"allow":[], "deny":[]},
            # "device_type": [],
            # "connection": [],
            # "affiliate_id": [],
            # "sub": [],
            # "deny_groups":[],
            # "url": ""
        }
        if d["geo"] != "":
            targets["country"]["allow"] = d["geo"].split(",")
        return [targets]
        

    def extract_offer(self, data):
        offers = []
        for d in data["offers"]:
            is_cpi = 0
            if d["price_model"] == "cpi":
                is_cpi = 1
            status = ""

            if self.statusMap.has_key(d["status"]):
                status = self.statusMap[d["status"]]

            start_at = datetime.strptime(d["start_date"], "%Y-%m-%dT%H:%M:%S+0000")
            if start_at < datetime.now():
                start_at = datetime.now()

            if not self.match_price_lower(d['price']):
                continue
    
            offers.append({
                "external_offer_id": d["campid"],
                "title": d["offer_name"],
                "advertiser": self.advertiser,
                "url": d["tracking_link"],
                "url_preview": d["preview_link"],
                "stopDate": datetime.strptime(d["end_date"], "%Y-%m-%dT%H:%M:%S+0000").strftime("%Y-%m-%d %H:%M:%S"),
                "start_at": start_at.strftime("%Y-%m-%d %H:%M:%S"),
                # "creativeUrls": self.extrace_offer_creatvies(d),
                "logo": self.extrace_offer_logo(d),
                "status": status,
                "is_cpi": is_cpi,
                "payments": self.extrace_offer_payments(d),
                "caps": self.extrace_offer_caps(d),
                "targeting": self.extrace_offer_targeting(d)
            })
        return offers


    def download(self, page):
        resp = self.make_request(page)
        if not resp or resp.status_code != 200:
            self.logger.info("can not pull offers from %s, response: %s" % (self.api, resp))
            return None
        content = resp.json()
        self.logger.debug(content)
        if len(content['offers']) == 0:
            self.logger.info("can not pull offers from %s, offer is empty" % self.api)
            return None
        return self.extract_offer(content)


if __name__ == '__main__':
    app = Hugoffers()
    for x in xrange(1, 10):
        offers = app.download(x)
        if not offers:
            app.logger.info("pull offers finish in page %s" % x)
            break
        print json.dumps(offers)
        break
    app.logger.info("pull offers done")