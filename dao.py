# coding=utf8
import os
import csv

class OfferDao(object):
    def __init__(self, advertiser):
      super(OfferDao, self).__init__()
      self.base_path = "data"
      self.advertiser = advertiser
      self.filepath = "%s/%s" % (self.base_path, self.advertiser)
      self.filename = "%s/offer_ids.csv" % self.filepath

    def ids_store_clear(self): 
      if not os.path.exists(self.filepath):
        os.mkdir(self.filepath)
      
      with open(self.filename, "w") as f:
        pass

    def ids_store_append(self, id, offer_id, external_offer_id, status): 
      if not external_offer_id:
        external_offer_id = "0"
      with open(self.filename, "a+") as f:
        writer = csv.writer(f)
        writer.writerow([id, offer_id, external_offer_id, status])

    def ids_store_get(self):
      data = []
      with open(self.filename, "r") as f:
        reader = csv.reader(f)
        for r in reader:
          data.append(r)
      return data

    def find_by_id(self, id):
      data = self.ids_store_get()
      if not data:
        return None
      
      for d in data:
        if int(d[0].strip()) == id:
          return d
      return None
    
    def find_by_offer_id(self, offer_id):
      data = self.ids_store_get()
      if not data:
        return None
      
      for d in data:
        if d[1].strip() == offer_id:
          return d
      return None

    def find_by_external_id(self, external_id):
      data = self.ids_store_get()
      if not data:
        return None
      
      for d in data:
        if d[2].strip() == external_id:
          return d
      return None

    def get_all(self):
      offers = {}
      with open(self.filename, "r+") as f:
        reader = csv.reader(f)
        for item in reader:
          if len(item) < 3 or item[2] == "":
            continue
          offers[item[2]] = item
      return offers