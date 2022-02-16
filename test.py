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

# lineNo = 0
# claimNo = "SC0019"
# claimType = 'SALARY ADAVANCE'
# accountNo = 'C00010'
# amount = 10
# description = "Test"
# claimReceiptNo = "Test"
# dimension3 = ""
# date_string = "2012-12-12"
# expenditureDate = datetime.fromisoformat(date_string)
# expenditureDescription = "Testing"
# myAction = 'insert'


# response = CLIENT.service.FnStaffClaimLine(lineNo,
#                                            claimNo, claimType, accountNo, amount, description, claimReceiptNo, dimension3, expenditureDate, expenditureDescription, myAction)
# print(response)

# applicationNo = ''
# employeeNo = 'AH'
# usersId = "NAVADMIN"
# dimension3 = ''
# leavePeriod = ''
# leaveType = ""
# plannerStartDate = datetime.fromisoformat("2012-12-12")
# isReturnSameDay = datetime.fromisoformat("2012-12-12")
# daysApplied = 1
# isLeaveAllowancePayable = True
# myAction = 'insert'

# response = CLIENT.service.FnLeaveApplication(applicationNo,
#                                              employeeNo, usersId, dimension3, leavePeriod, plannerStartDate, isReturnSameDay, dimension3, daysApplied, isLeaveAllowancePayable, myAction)
# print(response)

loanNo = ''
requestedDate = datetime.fromisoformat("2012-12-12")
usersId = "NAVADMIN"
pmlNo = ''
loanProductType = ''
loanDuration = 1
requestedAmount = 100
interestCalculationMethod = ''
repaymentFrequency = ''
bankName = ''
bankAccountNo = ''
bankBranchName = ''
myAction = 'insert'

response = CLIENT.service.FnLoanApplication(loanNo,
                                            requestedDate, usersId, pmlNo, loanProductType, loanDuration, requestedAmount, interestCalculationMethod, repaymentFrequency, bankName, bankAccountNo, bankBranchName, myAction)
print(response)
