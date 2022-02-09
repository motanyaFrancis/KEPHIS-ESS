# import requests
# from requests_ntlm import HttpNtlmAuth

# username = "fke-admin"
# password = "Administrator#2021!"

# site_url = "http://102.37.117.22:1448/ADMINBC/ODataV4/Company('FKETEST')/UpcomingEvents"

# r = requests.get(site_url, auth=HttpNtlmAuth(username, password))

# print(r.status_code)

# import requests
# from requests_ntlm import HttpNtlmAuth
# import json

# username = "NAVADMIN"
# password = "W3C0d3@llD@y"

# site_url = "http://20.121.189.145:7048/BC140/ODataV4/Company('KMPDC')/Imprests"

# r = requests.get(site_url, auth=HttpNtlmAuth(username, password)).json()

# print(r)


# import requests
# from requests_ntlm import HttpNtlmAuth

# username = "NAVADMIN"
# password = "N@vAdm$n2030!!"

# site_url = "http://13.68.215.64:1248/BC140/ODataV4/Company(%27KMPDC%27)/ProspectiveSuppliercard"

# r = requests.get(site_url, auth=HttpNtlmAuth(username, password))

# print(r.status_code)


from traceback import print_tb
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
from zeep import Client
from zeep.transports import Transport
import enum
from datetime import datetime

AUTHS = Session()

WEB_SERVICE_PWD = 'W3C0d3@llD@y'
BASE_URL = 'http://20.121.189.145:7047/BC140/WS/KMPDC/Codeunit/WebPortal'

AUTHS.auth = HttpNtlmAuth('domain\\NAVADMIN', WEB_SERVICE_PWD)
CLIENT = Client(BASE_URL, transport=Transport(session=AUTHS))

claimNo = ""
claimType = 2
isOnBehalf = False
accountNo = ''
payee = 'Papa'
purpose = 'Test'
usersId = "NAVADMIN"
staffNo = ''
currency = ""
imprestSurrDocNo = ''
myAction = 'insert'


response = CLIENT.service.FnStaffClaimHeader(
    claimNo, claimType, isOnBehalf, accountNo, payee, purpose, usersId, staffNo, currency, imprestSurrDocNo, myAction)
print(response)
