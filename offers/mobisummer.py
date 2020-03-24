# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import logging
import json
from datetime import datetime


class Mobisummer(object):
  name = "Mobisummer"
  domain = "http://api.tracksummer.com/api/v1/get"
  aff_id = "7950"
  key = "e886cae4-8623-47e2-a009-e1443c3424d0"
  advertiser = "5e5e2eb13e69e6128bb5e16f"
  api = ""
  timeout = 120
  limit = 1
  page = 10
  logger = None
  price_lower = 0.2
  payment_percent = 0.5
  
  def __init__(self):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s')
    self.logger = logging.getLogger(__name__)
    self.logger.info("%s init..." % self.name)

  def set_api(self, query):
    self.api = "%s?code=%s%s" % (self.domain, self.key, query)

  def make_request(self, page):
    query = "&page=%s&pageSize=%s" % (page, self.limit)
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
    for c in d['banners']:
      creatives.append(c['url'])
    return creatives

  def extrace_offer_logo(self, d):
    logo = None
    try:
      logo = d["icons"]
    except:
      pass
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
    return float(price) * self.payment_percent


  def extrace_offer_payments(self, d):
    payments = []
    payments.append({
      "goal": "1",
      "total": d["payout"],
      "currency": "USD",
      "type": "fixed",
      "revenue": self.cal_channel_payment(d["payout"])
    })
    return payments

  def extrace_offer_targeting(self, d):
    targets = {
      "country": {"allow":[], "deny":[]},
      # "region": {"allow":[], "deny":[]},
      # "city": {"allow":[], "deny":[]},
      "os": {"allow":[], "deny":[]},
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
    if d["country"] != "":
      targets["country"]["allow"].append(d["country"])
    if d["platform"] != "":
      targets["os"]["allow"].append(d["platform"])
    return [targets]

  def extract_tracking_link(self, tracking_link):
    tracking_link = tracking_link + "&aff_sub={clickid}"
    return tracking_link.replace('{device_id}', '{sub2}') \
            .replace('{idfa}', '{sub3}')

  def extract_status(self, d):
    return d["status"]
      

  def extract_offer(self, data):
    offers = []
    for d in data["offers"]:
      is_cpi = 0
      if d["payout_type"].lower() == "cpi":
        is_cpi = 1

      if not self.match_price_lower(d['payout']):
        continue

      offers.append({
        "external_offer_id": d["offer_id"],
        "title": d["offer_name"],
        "advertiser": self.advertiser,
        "url": self.extract_tracking_link(d["tracking_link"]),
        "url_preview": d["preview_link"],
        "logo": self.extrace_offer_logo(d),
        "status": self.extract_status(d),
        "is_cpi": is_cpi,
        "payments": self.extrace_offer_payments(d),
        "caps": self.extrace_offer_caps(d),
        "targeting": self.extrace_offer_targeting(d),
        "creativeUrls": self.extrace_offer_creatvies(d),
        "stopDate": "",
        "start_at": "",
      })
    return offers


  def download(self, page):
    resp = self.make_request(page)
    if not resp or resp.status_code != 200:
      self.logger.info("can not pull offers from %s, response: %s" % (self.api, resp))
      return None
    content = resp.json()
    self.logger.debug(content)
    if len(content["offers"]) == 0:
      self.logger.info("can not pull offers from %s, offer is empty" % self.api)
      return None
    return self.extract_offer(content)


if __name__ == '__main__':
  app = Mobisummer()
  for x in xrange(1, app.page):
    offers = app.download(x)
    if not offers:
      app.logger.info("pull offers finish in page %s" % x)
      break
    print json.dumps(offers)
    break
  app.logger.info("pull offers done")