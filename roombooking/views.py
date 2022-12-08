import base64
from django.shortcuts import render, redirect
from datetime import datetime
# from isodate import date_isoformat
import requests
from requests import Session
import json
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
from django.http import HttpResponse
import io as BytesIO
import secrets
import string
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from django.views import View

# Create your views here.


class UserObjectMixin(object):
    model = None
    session = Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response


class InternalRoomBooking(UserObjectMixin, View):
    def get(self, request):
        try:
            userID = request.session['User_ID']
            year = request.session['years']
            
            Access_Point = config.O_DATA.format(f"/QYvisitors")
            response = self.get_object(Access_Point)
            InternalBooking = [x for x in response['value']]
            
        except KeyError as e:
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            messages.error(request, e)
            print(e)
            return redirect('payslip')
        context = {
            "today": self.todays_date, "year": year,
               "full": userID, "res": InternalBooking
        }
        return render(request, 'InternalRoomBooking.html')
    
    