import base64
import logging
from django.shortcuts import render, redirect
import requests
from requests import Session
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
from django.views import View
from myRequest.views import UserObjectMixins
import aiohttp # type: ignore
import asyncio
from asgiref.sync import sync_to_async
# Create your views here.

class UserObjectMixin(object):
    model = None
    session = Session()
    session.auth = config.AUTHS
    todays_date = dt.datetime.now().strftime("%b. %d, %Y %A")

    def get_object(self, endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response
    
    
class Appraisals(UserObjectMixins,View):
    async def get(self, request):
        try:
            User_ID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role =await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role =await sync_to_async(request.session.__getitem__)('TO_role')
            full_name =await sync_to_async(request.session.__getitem__)('full_name')
            async with aiohttp.ClientSession() as session:
                get_appraisals = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                            '/QyEmployeeAppraisal','AppraiseeID','eq',User_ID))
                
                get_periods = asyncio.ensure_future(self.simple_fetch_data(session,
                                            '/QyAppraisalPeriod'))
                response = await asyncio.gather(get_appraisals,get_periods)
                

                open= [x for x in response[0] if x['Status'] == 'Open'] # type: ignore
                periods = [x for x in response[1]] # type: ignore
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            print(e)
            messages.info(request, f"{e}")
            return redirect('dashboard')
        ctx = {
            "today": self.todays_date,
            "res": open,
            "full": full_name,
            'periods':periods,
            'driver_role':driver_role,
            'TO_role':TO_role,
        }
                
        return render(request, 'appraisals.html', ctx)
    
    async def post(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
            appraisalNo = request.POST.get('appraisalNo')
            appraisalPeriod = request.POST.get('appraisalPeriod')
            Employee_No_ = await sync_to_async(request.session.__getitem__)('Employee_No_')
            # to be removed
            remarks = 'None'
            myAction = request.POST.get('myAction')
            
            response = self.make_soap_request(soap_headers,'FnAppraisalForm',
                                        appraisalNo, appraisalPeriod,
                                            Employee_No_, remarks, myAction )
            if response !=True and response !='0':
                messages.success(request, 'success')
                return redirect('AppraisalDetails', pk=response)
            messages.error(request, f'{response}')
            return redirect('Appraisals')
        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('Appraisals')
class AppraisalDetails(UserObjectMixins, View):
    async def get(self, request, pk):
        try:
            User_ID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role =await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role =await sync_to_async(request.session.__getitem__)('TO_role')
            full_name =await sync_to_async(request.session.__getitem__)('full_name')
            res = {}
            targets = []  
            attributes = []
            allFiles = []          
            async with aiohttp.ClientSession() as session:
                get_appraisal = asyncio.ensure_future(self.simple_double_filtered_data(session,
                                            '/QyEmployeeAppraisal','AppraisalNo','eq',pk,
                                                'and','AppraiseeID','eq',User_ID))
                get_targets = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyPersonalTarget',
                                                            'AppraisalNo','eq',pk))
                get_attributes = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyAttributes',
                                                            'AppraisalNo','eq',pk))
                get_attachments = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyDocumentAttachments',
                                                            'No_','eq',pk))
                response = await asyncio.gather(get_appraisal,
                                                    get_targets,
                                                        get_attributes,
                                                            get_attachments)
            
            
                for appraisal in response[0]: # type: ignore
                    res = appraisal
                targets = [x for x in response[1]] # type: ignore
                attributes = [x for x in response[2]] # type: ignore
                allFiles = [x for x in response[3]] # type: ignore
                
        except Exception as e:
            logging.exception(e)
            messages.error(request, f"{e}")
            return redirect('Appraisals')
        
        ctx = {
            "res": res,
            "today": self.todays_date,
            'full': full_name,
            'driver_role':driver_role,
            'TO_role':TO_role,
            'targets':targets,
            'attributes':attributes,
            "file": allFiles
        }
            
        return render(request, 'appraisalDetails.html', ctx)
    
class SupervisorAppraisal(UserObjectMixins,View):
    async def get(self,request, pk):
        try:
            User_ID = await sync_to_async(request.session.__getitem__)('User_ID')
            driver_role =await sync_to_async(request.session.__getitem__)('driver_role')
            TO_role =await sync_to_async(request.session.__getitem__)('TO_role')
            full_name =await sync_to_async(request.session.__getitem__)('full_name')
            res = {}
            targets = []  
            attributes = []
            allFiles = []
            ctx = {}
            async with aiohttp.ClientSession() as session:
                get_appraisal = asyncio.ensure_future(self.simple_double_filtered_data(session,
                                            '/QyEmployeeAppraisal','AppraisalNo','eq',pk,
                                                'and','AppraiseeID','eq',User_ID))
                get_targets = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyPersonalTarget',
                                                            'AppraisalNo','eq',pk))
                get_attributes = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyAttributes',
                                                            'AppraisalNo','eq',pk))
                get_attachments = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyDocumentAttachments',
                                                            'No_','eq',pk))
                response = await asyncio.gather(get_appraisal,
                                                    get_targets,
                                                        get_attributes,
                                                            get_attachments)
            
            
                for appraisal in response[0]: # type: ignore
                    res = appraisal
                targets = [x for x in response[1]] # type: ignore
                attributes = [x for x in response[2]] # type: ignore
                allFiles = [x for x in response[3]] # type: ignore
                ctx = {
                    "res": res,
                    "today": self.todays_date,
                    'full': full_name,
                    'driver_role':driver_role,
                    'TO_role':TO_role,
                    'targets':targets,
                    'attributes':attributes,
                    "file": allFiles
                }
        except Exception as e:
            logging.exception(e)
            messages.error(request, f'{e}')
            return redirect('Appraisals')
        return render(request,'supervisor.html',ctx)
        
class AppraisalAttachments(UserObjectMixins,View):
    def post(self, request, pk):
        try:
            soap_headers = request.session['soap_headers']
            attachments = request.FILES.getlist('attachment')
            tableID = 52177491
            attachment_names = []
            response = False

            for file in attachments:
                fileName = file.name
                attachment_names.append(fileName)
                attachment = base64.b64encode(file.read())

                response = self.make_soap_request(soap_headers,'FnUploadAttachedDocument',
                                                    pk, fileName, attachment, tableID,
                                                        request.session['User_ID'])
                
            if response is not None:
                if response == True:
                    messages.success(request, "Uploaded {} attachments successfully".format(len(attachments)))
                    return redirect('AppraisalDetails', pk=pk)
                messages.error(request, "Upload failed: {}".format(response))
                return redirect('AppraisalDetails', pk=pk)
            messages.error(request, "Upload failed: Response from server was None")
            return redirect('AppraisalDetails', pk=pk)
        except Exception as e:
            messages.error(request, "Upload failed: {}".format(e))
            logging.exception(e)
            return redirect('AppraisalDetails', pk=pk)
        
class SupervisorAttachments(UserObjectMixins,View):
    def post(self, request, pk):
        try:
            soap_headers = request.session['soap_headers']
            attachments = request.FILES.getlist('attachment')
            tableID = 52177491
            attachment_names = []
            response = False

            for file in attachments:
                fileName = file.name
                attachment_names.append(fileName)
                attachment = base64.b64encode(file.read())

                response = self.make_soap_request(soap_headers,'FnUploadAttachedDocument',
                                                    pk, fileName, attachment, tableID,
                                                        request.session['User_ID'])
                
            if response is not None:
                if response == True:
                    messages.success(request, "Uploaded {} attachments successfully".format(len(attachments)))
                    return redirect('SupervisorAppraisal', pk=pk)
                messages.error(request, "Upload failed: {}".format(response))
                return redirect('SupervisorAppraisal', pk=pk)
            messages.error(request, "Upload failed: Response from server was None")
            return redirect('SupervisorAppraisal', pk=pk)
        except Exception as e:
            messages.error(request, "Upload failed: {}".format(e))
            logging.exception(e)
            return redirect('SupervisorAppraisal', pk=pk)