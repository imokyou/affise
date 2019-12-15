# coding=utf8
import requests
import logging


class Ichestnut(object):
    domain = "http://api.ichestnut.net/v1/apps/get"
    key = "abcdefc"
    api = ""
    timeout = 15
    limit = 1000
    logger = None


    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def set_api(self, query):
        self.api = "%s?code=%s" % (self.domain, self.key)

    def make_request(self, page):
        query = ""
        self.set_api(query)
        self.logger.info("download offers from %s" % self.api)
        resp = requests.get(self.api, timeout=self.timeout)
        if not resp:
            self.logger.info("download fail %s, try again" % self.api)
            resp = requests.get(self.api, timeout=self.timeout)
        return resp

    def extrace_offer_logo(self, d):
        logo = ""
        for icon in d["icon"]:
            logo = icon["url"]
            break
        return logo

    def extrace_offer_creatvies(self, d):
        creatives = []
        for creatvie in d["creatives"]:
            creatives.append(creatvie["url"])
        return creatives

    def extrace_offer_caps(self, d):
        caps = []
        if d["cap"] != 0:   
            caps.append({
                "value": d["caps"]
            })
        return cap

    def extrace_offer_payments(self, d):
        payments = []
        payments.append({
            "partners": [],
            "countries": [],
            "country_exclude": [],
            "cities": [],
            "devices": [],
            "os": [],
            "revenue": d["payout"],
            "currency": d["currency"]
        })
        return payments

    def extrace_offer_targeting(self, d):
        targets = {}
        countries = []
        if len(d["countries"]) >= 1:
            targets["country"] = {
                "allow": d["countries"]
            }
        if d["os_min_version"] != "":
            targets["os"] = {"allow": []}
            oss = d["os_min_version"].split(",")
            for o in oss:
                targets["os"]["allow"].append({
                    "name": o.capitalize(),
                    "comparison": "",
                    "version": ""
                })
        return targets

    def extract_offer(self, data):
        offers = []
        for d in data:
            for o in d["offers"]:
                is_cpi = 0 

                offers.append({
                    "title": o["offer_name"],
                    "advertiser": "",
                    "url": o["tracking_link"],
                    "cross_postback_url": "",
                    "url_preview": o["preview_link"],
                    "trafficback_url": "",
                    "domain_url": 0,
                    "description_lang": [],
                    "stopDate": "",
                    "creativeFiles": [],
                    "creativeUrls": self.extrace_offer_creatvies(data),
                    "sources": [],
                    "logo": self.extrace_offer_logo(data),
                    "status": o["status"],
                    "tags": [],
                    "categories": [o["category"]],
                    "privacy": "public",
                    "is_top": 0,
                    "is_cpi": is_cpi,
                    "payments": self.extrace_offer_payments(o),
                    "partner_payments": [],
                    "notice_percent_overcap": 90,
                    "landings": [],
                    "strictly_country": 0,
                    "restriction_os": [],
                    "caps": [],
                    "targeting": self.extrace_offer_targeting(o)
                })
        return offers


    def download(self, page):
        resp = self.make_request(page)
        if not resp or resp.status_code != 200:
            self.logger.info("can not pull offers from %s, response: %s" % (self.api, resp))
            return None
        content = resp.json()
        if content["success"] == false:
            return None

        self.logger.debug(content)
        if len(content['data']) == 0:
            self.logger.info("can not pull offers from %s, offer is empty" % self.api)
            return None
        return self.extract_offer(content)


if __name__ == '__main__':
    app = Appleadstech()
    for x in xrange(1, 10):
        offers = app.download(x)
        if not offers:
            app.logger.info("pull offers finish in page %s" % x)
            break
    app.logger.info("pull offers done")