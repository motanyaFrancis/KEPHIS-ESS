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
from requests.auth import HTTPBasicAuth

AUTHS = Session()

WEB_SERVICE_PWD = 'Password@123'
BASE_URL = 'http://20.121.189.145:7047/KMPDC/WS/KMPDC/Codeunit/WebPortal'

AUTHS.auth = HTTPBasicAuth('WINNIE', WEB_SERVICE_PWD)
CLIENT = Client(BASE_URL, transport=Transport(session=AUTHS))


# requisitionNo = ''
# lineNo = 0
# itemCode = ""
# location = "AFGHANISTA"
# quantity = 1
# myAction = 'insert'

# response = CLIENT.service.FnStoreRequisitionLine(requisitionNo, lineNo, itemCode, location, quantity,
#                                                  myAction)
# print(response)


#  Modify Documents ---------------------------------------------------
# -------------------------------------------------------------------------

# requestNo = 'TRQ-00006'
# employeeNo = 'AH'
# usersId = "NAVADMIN"
# designation = 'BIRMINGHAM'
# isAdhoc = False
# trainingNeed = 'TRNEV-0005'
# description = "New Test"
# startDate = datetime.strptime('02-23-2022', '%m-%d-%Y')
# endDate = datetime.strptime('02-25-2022', '%m-%d-%Y')
# destination = "ALGERIA"
# currency = "AED"
# isLeaveAllowancePayable = False
# myAction = 'modify'

# response = CLIENT.service.FnTrainingRequest(requestNo,
#                                             employeeNo, usersId, designation, isAdhoc, trainingNeed, description, startDate, endDate, destination, currency, myAction)
# print(response)

# entryNo = ''
# documentNo = 'AH'
# userID = "NAVADMIN"
# approvalComments = 'test'
# myAction = 'insert'

# response = CLIENT.service.FnDocumentApproval(entryNo,
#                                              documentNo, userID, approvalComments,  myAction)
# print(response)


# myUserID = "NAV-TESTDAN\\NAVADMIN"
# applicationNo = "STREQ-000009"


# response = CLIENT.service.FnRequestInternalRequestApproval(myUserID,
#                                                            applicationNo)
# print(response)

myUserID = "NAVADMIN"
trainingNo = "TRQ-00012"


response = CLIENT.service.FnRequestTrainingApproval(myUserID,
                                                    trainingNo)
print(response)
