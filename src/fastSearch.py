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
				logging.info("==> "+data["criteria"]+" = ["+data["value"]+"]")
				travels = Travel.all().filter("arrival = ", data['value'].capitalize())
				access_db = True

			elif data["criteria"] == "from":
				logging.info("==> "+data["criteria"]+" = ["+data["value"]+"]")
				travels = Travel.all().filter("departure = ", data['value'].capitalize())
				access_db = True

			elif data["criteria"] == "day":
				logging.info("==> "+data["criteria"]+" = ["+data["value"]+"]"+' --> '+type(data["value"]).__name__)
				travels = Travel.by_day(data['value'].capitalize())
				access_db = True

			elif data["criteria"] == "price":
				logging.info("==> "+data["criteria"]+" = ["+data["value"]+"]")
				travels = Travel.all().filter("price <= ", int(data['value'])).order("price")
				access_db = True

			if access_db:
				if memcache.get(key=str(self.user.key().id())):
					memcache.delete(key=str(self.user.key().id()))
				memcache.add(key=str(self.user.key().id()), value=travels.filter("actif = ", True) , time=5)
				logging.info("Added to memcache "+str(travels.count()));
				self.response.out.write(json.dumps({}))

			else:
				logging.info("NOT FOUND ==> "+data["criteria"])
				self.response.out.write(json.dumps({'error':True}))
