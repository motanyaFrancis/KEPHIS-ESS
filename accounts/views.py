
from django.shortcuts import render, redirect
from django.conf import settings as config
import requests
from requests import Session
from django.contrib import messages
from requests.auth import HTTPBasicAuth
from django.views import View
from datetime import date
import datetime
# Create your views here.
class UserObjectMixin(object):
    model =None
    user = Session()
    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    def get_object(self,username,password,endpoint):
        self.user.auth = HTTPBasicAuth(username, password)
        response = self.user.get(endpoint, timeout=10).json()
        return response

class Login(UserObjectMixin,View):
    template_name = 'auth.html'
    def get(self, request):
        return render(request, self.template_name)
    def post(self,request):
        username = request.POST.get('username').upper().strip()
        password = request.POST.get('password').strip()
        print(username, password)
        try:
            QyUserSetup = config.O_DATA.format(f"/QyUserSetup?$filter=User_ID%20eq%20%27{username}%27")
            res_data = self.get_object(username, password,QyUserSetup)
            for data in res_data['value']:
                request.session['Employee_No_'] = data['Employee_No_']
                request.session['Customer_No_'] = data['Customer_No_']
                request.session['User_ID'] = data['User_ID']
                request.session['E_Mail'] = data['E_Mail']
                request.session['User_Responsibility_Center'] = data['User_Responsibility_Center']
                request.session['password'] = password
                current_year = date.today().year
                request.session['years'] = current_year
                print(request.session['Employee_No_'])
                QyEmployees = config.O_DATA.format(f"/QyEmployees?$filter=No_%20eq%20%27{request.session['Employee_No_']}%27")
                response = self.get_object(username, password,QyEmployees)
                for emp in response['value']:
                    request.session['Department'] = emp['Department_Code']
                return redirect('dashboard')
        except requests.exceptions.RequestException as e:
            print(e)
            messages.error(request, "Invalid Username or Password")
            return redirect('auth')

def logout(request):
    try:
        del request.session['User_ID']
        del request.session['Employee_No_']
        del request.session['Customer_No_']
        del request.session['User_Responsibility_Center']
        del request.session['Department']
        del request.session['years']
        del request.session['E_Mail']
        messages.success(request,"Logged out successfully")
    except KeyError:
        print(False)
    return redirect('auth')

class profile(UserObjectMixin,View):
    def get(self, request):
        try:
            year =request.session['years']
            fullname =request.session['User_ID']
            empNo =request.session['Employee_No_']
            Dpt =request.session['Department']
            mail =request.session['E_Mail']
        except KeyError as e:
            messages.error(request, e)
            return redirect('auth')

        ctx = {"today": self.todays_date,"year": year,"full": fullname,"empNo":empNo,"Dpt":Dpt,"mail":mail}
        return render(request,"profile.html",ctx)