#########################################################################
# This module provides the fast search url handler
# Look into User and Travel DB Table to retrieve corresponding data
#########################################################################

from src.handler import *
from src.travel import *
import json

class FastSearch(MainHandler):

	def post(self):
		data = json.loads(self.request.body)
		response = {}

		if data["db"] == 'travel':
			logging.info("have to look into travel")
			access_db = False

			if data["criteria"] == "to":
				logging.info("==> "+data["criteria"])
				response["travels"] = Travel.all().filter("arrival = ", data['value'])
				access_db = True

			elif data["criteria"] == "from":
				logging.info("==> "+data["criteria"])
				response["travels"] = Travel.all().filter("departure = ", data['value'])
				access_db = True

			elif data["criteria"] == "day":
				logging.info("==> "+data["criteria"])
				response["travels"] = Travel.all().filter("schedule_day = ", data['value'])
				access_db = True

			elif data["criteria"] == "price":
				logging.info("==> "+data["criteria"])
				response["travels"] = Travel.all().filter("price <= ", data['value']).order("price")
				access_db = True

			else:
				logging.info("NOT FOUND ==> "+data["criteria"])


			if access_db:
				Travel.memcache.delete(key=str(self.user.key().id()))
				Travel.memcache.add(key=str(self.user.key().id()), value=response["travels"], time=5)
				self.redirect("/resultSearch")