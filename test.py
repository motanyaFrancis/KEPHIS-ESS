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
# claimNo = "SC0020"
# claimType = "SALARY ADAVANCE"
# accountNo = 'C00010'
# amount = 10
# description = "Test"
# claimReceiptNo = ""
# dimension3 = ""
# expenditureDate = datetime.fromisoformat("2022-12-12")
# expenditureDescription = "Testing"
# myAction = 'insert'


# response = CLIENT.service.FnStaffClaimLine(lineNo,
#                                            claimNo, claimType, accountNo, amount, description, claimReceiptNo, dimension3, expenditureDate, expenditureDescription, myAction)
# print(response)

applicationNo = 'LPL0004'
employeeNo = 'AH'
usersId = "NAVADMIN"
dimension3 = ''
leaveType = "ANNUAL"
date_str3 = '02-20-2022'
# plannerStartDate = datetime.strptime(date_str3, '%m-%d-%Y')
plannerStartDate = "2021-09-01"
isReturnSameDay = False
daysApplied = 2
isLeaveAllowancePayable = False
myAction = 'insert'

response = CLIENT.service.FnLeaveApplication(applicationNo,
                                             employeeNo, usersId, dimension3, plannerStartDate, isReturnSameDay, dimension3, daysApplied, isLeaveAllowancePayable, myAction)
print(response)

# loanNo = ''
# date_str3 = '02-20-2022'
# requestedDate = datetime.strptime(date_str3, '%m-%d-%Y')
# usersId = "NAVADMIN"
# pmlNo = ''
# loanProductType = ''
# loanDuration = 1
# requestedAmount = 100
# interestCalculationMethod = ''
# repaymentFrequency = ''
# bankName = "1"
# bankAccountNo = '12345678'
# bankBranchName = '100'
# myAction = 'insert'

# response = CLIENT.service.FnLoanApplication(loanNo,
#                                             requestedDate, usersId, pmlNo, loanProductType, loanDuration, requestedAmount, interestCalculationMethod, repaymentFrequency, bankName, bankAccountNo, bankBranchName, myAction)
# print(response)


# collateralCode = ''
# loanNo = ""
# collateralType = ""
# date_str3 = '02-20-2022'
# maturityDate = datetime.strptime(date_str3, '%m-%d-%Y')
# collateralValue = 100
# isPerfected = True
# isExcludedActivities = 1
# isNemaCompliant = 1
# securityType = ""
# myAction = 'insert'

# response = CLIENT.service.FnLoanCollateral(collateralCode,
#                                             loanNo, collateralType, maturityDate, collateralValue, isPerfected, isExcludedActivities, isNemaCompliant, securityType,  myAction)
# print(response)

# requisitionNo = ''
# orderDate = datetime.strptime('02-20-2022', '%m-%d-%Y')
# employeeNo = 'AH'
# reason = "Test"
# expectedReceiptDate = datetime.strptime('02-20-2022', '%m-%d-%Y')
# isConsumable = True
# myUserId = "NAVADMIN"
# myAction = 'insert'

# response = CLIENT.service.FnPurchaseRequisitionHeader(requisitionNo,
#                                                       orderDate, employeeNo, reason, expectedReceiptDate, isConsumable, myUserId, myAction)
# print(response)


# requisitionNo = ''
# lineNo = 0
# procPlanItem = ''
# itemType = ""
# specification = ''
# quantity = 1
# myUserId = "NAVADMIN"
# myAction = 'insert'

# response = CLIENT.service.FnPurchaseRequisitionLine(requisitionNo,
#                                                     lineNo, procPlanItem, itemType, specification, quantity, myUserId, myAction)
# print(response)

# requisitionNo = ''
# orderDate = datetime.strptime('02-20-2022', '%m-%d-%Y')
# employeeNo = 'AH'
# reason = "Test"
# expectedReceiptDate = datetime.strptime('02-20-2022', '%m-%d-%Y')
# myUserId = "NAVADMIN"
# myAction = 'insert'

# response = CLIENT.service.FnRepairRequisitionHeader(requisitionNo,
#                                                     orderDate, employeeNo, reason, expectedReceiptDate, myUserId, myAction)
# print(response)

# requisitionNo = ''
# lineNo = 0
# assetCode = ''
# myAction = 'insert'

# response = CLIENT.service.FnRepairRequisitionLine(requisitionNo,
#                                                   lineNo, assetCode, myAction)
# print(response)

# requisitionNo = ''
# employeeNo = 'AH'
# issuingStore = "AFGHANISTA"
# reason = ""
# expectedReceiptDate = datetime.strptime('02-20-2022', '%m-%d-%Y')
# myUserId = "NAVADMIN"
# myAction = 'insert'

# response = CLIENT.service.FnStoreRequisitionHeader(requisitionNo, employeeNo, issuingStore, reason, expectedReceiptDate,
#                                                    myUserId, myAction)
# print(response)

# requisitionNo = ''
# lineNo = 0
# itemCode = ""
# location = "AFGHANISTA"
# quantity = 1
# myAction = 'insert'

# response = CLIENT.service.FnStoreRequisitionLine(requisitionNo, lineNo, itemCode, location, quantity,
#                                                  myAction)
# print(response)
