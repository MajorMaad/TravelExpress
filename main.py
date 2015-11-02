#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


# Import handlers
from src.handler import *
from src.userHandler import *
from src.travelHandler import *

# URL handler dispatcher
app = webapp2.WSGIApplication([('/', MainHandler),
								('/signUp', SignUp),
								('/logIn', LogIn),
								('/logOut', LogOut),
								('/addTravel', AddTravel),
								('/driverTravels', ShowDriverTravels),
								('/deleteTravel', DeleteTravel),
								('/modifyTravel', ModifyTravel),
								('/searchTravel', SearchTravel),
								('/resultSearch', ResultSearchTravel),
								('/addUserToTravel', AddUserToTravel),
								('/travelerTravels', ShowTravelerTravels),
								('/myProfile', MyProfile)],
								debug=True)
