# codnig=utf8
import requests
import logging
import json
from datetime import datetime


class Hugoffers(object):
    domain = "http://tapcrane.hoapi0.com"
    key = "1d72fd30c41a487d9b798408148cc5fa"
    api = ""
    timeout = 15
    limit = 1
    logger = None
    
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
                "period": "day",
                "type": "conversions",
                "value": d["daily_cap"],
                "goals": [],
                "goal_type": [],
                "affiliates":[],
                "affiliate_type": []
            })
        return caps

    def extrace_offer_payments(self, d):
        payments = []
        payments.append({
            # "partners": [],
            # "countries": [],
            # "country_exclude": [],
            # "cities": [],
            # "devices": [],
            # "os": [],
            "revenue": d["price"],
            # "currency": "",
        })
        return payments

    def extrace_offer_targeting(self, d):
        targets = {}
        countries = []
        if d["geo"] != "":
            countries = d["geo"].split(",")
            targets["country"] = {
                "allow": countries
            }
        if d["platform"] != "":
            targets["os"] = {
                "allow": [{
                    "name": d['platform'],
                    "comparison": "",
                    "version": ""
                }]
            }
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
    
            offers.append({
                "title": d["offer_name"],
                "advertiser": "5df8c50410768e44b351cc66",
                "url": d["tracking_link"],
                "cross_postback_url": "",
                "url_preview": d["preview_link"],
                "trafficback_url": "",
                "domain_url": 0,
                "description_lang": [],
                "stopDate": datetime.strptime(d["end_date"], "%Y-%m-%dT%H:%M:%S+0000").strftime("%Y-%m-%d %H:%M:%S"),
                "start_at": start_at.strftime("%Y-%m-%d %H:%M:%S"),
                "creativeFiles": [],
                "creativeUrls": self.extrace_offer_creatvies(d),
                "sources": [],
                "logo": self.extrace_offer_logo(d),
                "status": status,
                "tags": [],
                "privacy": "public",
                "is_top": 0,
                "is_cpi": is_cpi,
                "payments": self.extrace_offer_payments(d),
                "partner_payments": [],
                "notice_percent_overcap": 90,
                "landings": [],
                "strictly_country": 0,
                "restriction_os": [],
                "caps": self.extrace_offer_caps(d),
                # "targeting": self.extrace_offer_targeting(d)
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