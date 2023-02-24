import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
from datetime import datetime

AUTHS = Session()

WEB_SERVICE_PWD = "Admin@123"

BASE_URL = 'http://20.231.15.166:7047/BC140/WS/CRONUS%20International%20Ltd./Codeunit/Employee_Self_Service'

AUTHS.auth = HTTPBasicAuth('WAKINYI', WEB_SERVICE_PWD)
CLIENT = Client(BASE_URL, transport=Transport(session=AUTHS))

bookingDate = datetime.strptime("2022-12-09", '%Y-%m-%d').date()
endDate = datetime.strptime("27-10-2022", '%d-%m-%Y').date()
startTime = datetime.strptime("13:55:26", '%H:%M:%S').time()
endTime = datetime.strptime("16:55:26", '%H:%M:%S').time()

result = CLIENT.service.FnAppraisalForm("",'2022','EMP-00013','','insert')
    
print(result)

