# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import logging
import json
from datetime import datetime


class DuunionOffers(object):
  name = "DuunionOffers"
  domain = "http://feed.xyz.duunion.com/offers"
  aff_id = "921"
  key = "66f7fde2790496738fe1d4d1c678dcb8"
  advertiser = "5e6e4e27cf4c2cc25ba61f68"
  api = ""
  timeout = 120
  limit = 150
  page = 10
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
    self.logger.info("BeerOffers init...")

  def set_api(self, query):
    self.api = "%s?aff_id=%s&api_key=%s%s" % (self.domain, self.aff_id, self.key, query)

  def make_request(self, page):
    query = "&page=%s&limit=%s" % (page, self.limit)
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
    for c in d['banner']:
      creatives.append(c['url'])
    return creatives

  def extrace_offer_logo(self, d):
    logo = None
    try:
      logo = d[0]["url"]
    except:
      pass
    return logo

  def extrace_offer_caps(self, d):
    caps = []
    if d["conversions_cap"] != 0:   
      caps.append({
        "affiliate_type": "all",
        "goal_type": "all",
        "period": "day",
        "type": "conversions",
        "value": d["conversions_cap"]
      })
    return caps

  def cal_channel_payment(self, price):
    return price * self.payment_percent


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
    # tracking_link += "&click={clickid}&aff_sub={pid}&gaid={sub3}&android_id={sub4}&payout={sum}&idfa={sub5}"
    # return tracking_link
    return tracking_link.replace('[click_id]', '[clickid]') \
            .replace('[source]', '[sub2]') \
            .replace('[idfa]', '[sub3]') \
            .replace('[advertising_id]', '[sub4]') \
            .replace('[', '{').replace(']', '}')

  def extract_status(self, d):
    status = "active"
    if d.has_key("status") and self.statusMap.has_key(d["status"]):
      status = self.statusMap[d["status"]]
    return status
      

  def extract_offer(self, data):
    offers = []
    for d in data["data"]["ad_list"]:
      is_cpi = 0
      if d["conversion_type"].lower() == "cpi":
        is_cpi = 1
        
      status = self.extract_status(d)

      if not self.match_price_lower(d['payout']):
        continue

      offers.append({
        "external_offer_id": d["offer_id"],
        "title": d["title"],
        "advertiser": self.advertiser,
        "url": self.extract_tracking_link(d["click_url"]),
        "url_preview": d["preview_url"],
        "logo": self.extrace_offer_logo(d),
        "status": status,
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
    if content["errno"] != 0:
      self.logger.info("can not pull offers from %s, offer is empty" % self.api)
      return None
    return self.extract_offer(content)


if __name__ == '__main__':
  app = DuunionOffers()
  for x in xrange(1, app.page):
    offers = app.download(x)
    if not offers:
      app.logger.info("pull offers finish in page %s" % x)
      break
    print json.dumps(offers)
    break
  app.logger.info("pull offers done")