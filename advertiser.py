# coding=utf8
import json
import logging
import requests
import config



class Advertiser(object):
    routers = {
        "list": "/3.0/admin/advertisers",
        "get": "/3.0/admin/advertiser/%s",
        "add": "/3.0/admin/advertiser"
    }

    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(filename)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)


    def get_list_api(self):
        api = "%s%s?API-Key=%s" % (config.domain, self.routers["list"], config.key)
        return api

    def get_add_api(self):
        api = "%s%s?API-Key=%s" % (config.domain, self.routers["add"], config.key)
        return api    


    def get_list(self, page=1, limit=50):
        query = "page=%s&limit=%s" % (page, limit)
        api = self.get_list_api() + "&" + query
        self.logger.info("download advertisers from %s" % api)
        resp = requests.get(api, timeout=3)
        if not resp or resp.status_code != 200:
            return None

        return resp.json()

    def add(self, advertiser):
        api = self.get_add_api()
        resp  = requests.post(api, data=json.dumps(advertiser), timeout=3)
        if not resp or resp.status_code != 200:
            return None
        return resp.json()



if __name__ == '__main__':
    app = Advertiser()
    rows = app.get_list()
    print(json.dumps(rows))

    # advertiser1 = {
    #     "title": "Appleadstech",
    #     "contact": "",
    #     "skype": "",
    #     "manager": "",
    #     "url": "",
    #     "email": "",
    #     # "allowed_ip": "",
    #     "address_1": "",
    #     "address_2": "",
    #     "city": "",
    #     "country": "",
    #     "zip_code": "",
    #     # "vat_code": "",
    #     # "sub_account_1": "",
    #     # "sub_account_2": "",
    #     # "sub_account_1_except": "",
    #     # "sub_account_2_except": ""
    # }
    # resp = app.add(advertiser1)
    # print(resp)
