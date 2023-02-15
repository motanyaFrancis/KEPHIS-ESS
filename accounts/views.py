
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from myRequest.views import UserObjectMixins
import asyncio
import aiohttp
from asgiref.sync import sync_to_async


class Login(UserObjectMixins,View):
    template_name = 'auth.html'
    async def get(self, request):
        return render(request, self.template_name)
    async def post(self,request):
        try:
            username = request.POST.get('username').upper().strip()
            password = request.POST.get('password').strip()
            async with aiohttp.ClientSession() as session:
                task_get_user_setup = asyncio.ensure_future(self.fetch_data(session,username,password,
                                                                        "/QYUserSetup","User_ID","eq"))
                
                user_response = await asyncio.gather(task_get_user_setup)
                                                   
                if user_response[0]['status_code'] == 200:#type:ignore
                    for data in user_response[0]['data']:#type:ignore
                        await sync_to_async(request.session.__setitem__)('Employee_No_', data['Employee_No_'])
                        await sync_to_async(request.session.__setitem__)('Customer_No_', data['Customer_No_'])
                        await sync_to_async(request.session.__setitem__)('User_ID', data['User_ID'])
                        await sync_to_async(request.session.__setitem__)('E_Mail', data['E_Mail'])
                        await sync_to_async(request.session.__setitem__)('User_Responsibility_Center', data['Global_Dimension_1_Code'])
                        await sync_to_async(request.session.__setitem__)('HOD_User', data['HOD_User'])
                        soap_headers = {
                            "username":data['User_ID'],
                            "password":password
                        }
                        await sync_to_async(request.session.__setitem__)('soap_headers', soap_headers)
                        await sync_to_async(request.session.save)()
                                                
                        Employee_No_ = await sync_to_async(request.session.__getitem__)('Employee_No_')
 
                        task_get_employee = asyncio.ensure_future(self.fetch_one_filtered_data(session,
                                                       "/QYEmployees","No_","eq",Employee_No_))
                    
                        employee_response = await asyncio.gather(task_get_employee)
                        for data in employee_response[0]['data']: #type:ignore
                            await sync_to_async(request.session.__setitem__)('full_name', data['First_Name'] + " " + data['Last_Name'] )
                            await sync_to_async(request.session.__setitem__)('driver_role', data['Driver'])
                            await sync_to_async(request.session.__setitem__)('TO_role', data['TO_MI'])
                            await sync_to_async(request.session.save)()
                            messages.success(request,f"Success. Logged in as {request.session['full_name']}")
                            return redirect('dashboard')
                if user_response[0]['status_code'] != 200:#type:ignore
                    messages.error(request,"Authentication Error: Invalid credentials")
                    return redirect('auth')
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,"Authentication Error: Invalid credentials")
            return redirect('auth')   
        except Exception as e:
            print(e)
            messages.error(request,"Authentication Error: Invalid credentials")
            return redirect('auth')
def logout(request):
    try:
        request.session.flush()
        messages.success(request,"Logged out successfully")
    except KeyError:
        print(False)
    return redirect('auth')

class profile(UserObjectMixins,View):
    def get(self, request):
        try:
            fullname =request.session['User_ID']
            empNo =request.session['Employee_No_']
            Dpt =request.session['Department']
            mail =request.session['E_Mail']
        except KeyError as e:
            messages.error(request, f"{e}")
            return redirect('auth')

        ctx = {"today": self.todays_date,"full": fullname,"empNo":empNo,"Dpt":Dpt,"mail":mail}
        return render(request,"profile.html",ctx)