# coding=utf8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
import logging
import json
from datetime import datetime


class Interestmob(object):
  name = "Interestmob"
  domain = "http://getapi.interestmob.com/getmoboffer/getoffersv2/data.do"
  aff_id = ""
  key = "38f655b37dcde7f03fdceaa660bbc8db"
  advertiser = "5e5e2c71f3a0cef2a93e1bd6"
  api = ""
  timeout = 120
  limit = 1
  page = 2
  logger = None
  price_lower = 0.2
  payment_percent = 0.5
  
  def __init__(self):
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s')
    self.logger = logging.getLogger(__name__)
    self.logger.info("%s init..." % self.name)

  def set_api(self, query):
    self.api = "%s?key=%s%s" % (self.domain, self.key, query)

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
    return creatives

  def extrace_offer_logo(self, d):
    logo = None
    try:
      logo = d["icon"]
    except:
      pass
    return logo

  def extrace_offer_caps(self, d):
    caps = []
    if d["cap"] != 0:   
      caps.append({
        "affiliate_type": "all",
        "goal_type": "all",
        "period": "day",
        "type": "conversions",
        "value": d["cap"]
      })
    return caps

  def cal_channel_payment(self, price):
    return price * self.payment_percent


  def extrace_offer_payments(self, d):
    payments = []
    payments.append({
      "goal": "1",
      "total": d["payout"],
      "currency": d["currency"],
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
    if d["countries"]:
      targets["country"]["allow"] = d["countries"]
    if d["os"] != "":
      targets["os"]["allow"].append(d["os"])
    return [targets]

  def extract_tracking_link(self, tracking_link):
    # gaid={gaid}&sub_affid={ sub_affid }&idfa={idfa}&android_id={android_id}&imei={imei}
    tracking_link = tracking_link + "&aff_sub={clickid}&sub2={gaid}&sub3={idfa}&sub4={android_id}&sub5={imei}"
    return tracking_link

  def extract_status(self, d):
    return "active"

  def extract_offer(self, data):
    offers = []
    for d in data["data"]:
      is_cpi = 0
      if d["paymodel"].lower() == "cpi":
        is_cpi = 1

      if not self.match_price_lower(d['payout']):
        continue

      offers.append({
        "external_offer_id": d["offer_id"],
        "title": d["title"],
        "advertiser": self.advertiser,
        "url": self.extract_tracking_link(d["click_link"]),
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
    if len(content["data"]) == 0:
      self.logger.info("can not pull offers from %s, offer is empty" % self.api)
      return None
    return self.extract_offer(content)


if __name__ == '__main__':
  app = Interestmob()
  for x in xrange(1, app.page):
    offers = app.download(x)
    if not offers:
      app.logger.info("pull offers finish in page %s" % x)
      break
    print json.dumps(offers)
    break
  app.logger.info("pull offers done")