# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import logging
import json
from datetime import datetime


class Vinsmok(object):
  name = "Vinsmok"
  domain = "http://vinsmok.hoapi0.com/v1"
  aff_id = "vinsmok"
  key = "ea33feba431343548deef79eafaba6dd"
  advertiser = "5e5e2adc3e69e6128bb5e16d"
  api = ""
  timeout = 120
  limit = 1
  page = 2
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
    self.logger.info("%s init..." % self.name)

  def set_api(self, query):
    self.api = "%s?cid=%s&token=%s%s" % (self.domain, self.aff_id, self.key, query)

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
    try:
      logo = d["icon_link"]
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
    if d["geo"] != "":
      targets["country"]["allow"].append(d["geo"])
    if d["platform"] != "":
      targets["os"]["allow"].append(d["platform"])
    return [targets]

  def extract_tracking_link(self, tracking_link):
    return tracking_link.replace('[click_id]', '[clickid]') \
            .replace('[source]', '[sub2]') \
            .replace('[idfa]', '[sub3]') \
            .replace('[advertising_id]', '[sub4]') \
            .replace('[', '{').replace(']', '}')

  def extract_status(self, d):
    status = ""
    if self.statusMap.has_key(d["status"]):
      status = self.statusMap[d["status"]]
    return status
      

  def extract_offer(self, data):
    offers = []
    for d in data["offers"]:
      is_cpi = 0
      if d["price_model"].lower() == "cpi":
        is_cpi = 1

      if not self.match_price_lower(d['price']):
        continue

      start_at = datetime.strptime(d["start_date"], "%Y-%m-%dT%H:%M:%S+0000")
      if start_at < datetime.now():
        start_at = datetime.now()

      offers.append({
        "external_offer_id": d["campid"],
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
        "stopDate": datetime.strptime(d["end_date"], "%Y-%m-%dT%H:%M:%S+0000").strftime("%Y-%m-%d %H:%M:%S"),
        "start_at": start_at.strftime("%Y-%m-%d %H:%M:%S"),
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
  app = Vinsmok()
  for x in xrange(1, app.page):
    offers = app.download(x)
    if not offers:
      app.logger.info("pull offers finish in page %s" % x)
      break
    print json.dumps(offers)
    break
  app.logger.info("pull offers done")