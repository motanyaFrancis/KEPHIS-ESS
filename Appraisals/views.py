import base64
import logging
from django.shortcuts import render, redirect
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
            SupervisorNo = await sync_to_async(request.session.__getitem__)('SupervisorNo')
            supervisor_appraisal = []
            approved = []
            await sync_to_async(request.session.__setitem__)('Supervisor', False)
            await sync_to_async(request.session.save)()

            async with aiohttp.ClientSession() as session:
                get_appraisals = asyncio.ensure_future(self.simple_fetch_data(session,
                                            f'/QyEmployeeAppraisal?$filter=AppraiserID%20eq%20%27{User_ID}%27'))
                
                get_periods = asyncio.ensure_future(self.simple_fetch_data(session,
                                            '/QyAppraisalPeriod?$filter=Active%20eq%20true'))
                supervisor = asyncio.ensure_future(self.simple_double_filtered_data(session,
                                        '/QyEmployeeAppraisal','DocumentStage','eq','Supervisor',
                                            'and','AppraiserNo','eq',SupervisorNo))
                response = await asyncio.gather(get_appraisals,
                                                    get_periods,
                                                        supervisor)
                

                open= [x for x in response[0] if x['Status'] == 'Open'] # type: ignore
                pending= [x for x in response[0] if x['Status'] == 'Pending Approval'] # type: ignore
                approved = [x for x in response[0] if x['Status'] == 'Released'] # type: ignore
                completed= [x for x in response[0] if x['Status'] == 'Completed'] # type: ignore
                periods = [x for x in response[1]] # type: ignore
                supervisor_appraisal = [x for x in response[2]] # type: ignore
   
                if len(supervisor_appraisal) > 0:
                    await sync_to_async(request.session.__setitem__)('Supervisor', True)
                    await sync_to_async(request.session.save)()
                Supervisor = await sync_to_async(request.session.__getitem__)('Supervisor')
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
            'pending':pending,
            'approved':approved,
            'supervisor_appraisal':supervisor_appraisal,
            'Supervisor':Supervisor,
            'completed':completed
        }
                
        return render(request, 'appraisals.html', ctx)
    
    async def post(self, request):
        try:
            soap_headers = await sync_to_async(request.session.__getitem__)('soap_headers')
            appraisalNo = request.POST.get('appraisalNo')
            appraisalPeriod = request.POST.get('appraisalPeriod')
            Employee_No_ = await sync_to_async(request.session.__getitem__)('Employee_No_')
            myAction = request.POST.get('myAction')
            appraisee_remarks = request.POST.get('appraisee_remarks')
            appraiser_remarks = request.POST.get('appraiser_remarks')
            manager_remarks = request.POST.get('manager_remarks')
            
            response = self.make_soap_request(soap_headers,
                                                'FnAppraisalForm',
                                                    appraisalNo,
                                                        appraisalPeriod,
                                                            Employee_No_,
                                                                myAction,
                                                                    appraisee_remarks,
                                                                        appraiser_remarks,
                                                                            manager_remarks)
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
            Supervisor = await sync_to_async(request.session.__getitem__)('Supervisor')
            res = {}
            targets = []  
            attributes = []
            allFiles = []   
            trainings = []  
            print(pk)     
            async with aiohttp.ClientSession() as session:
                get_appraisal = asyncio.ensure_future(self.simple_fetch_data(session,
                                            f'/QyEmployeeAppraisal?$filter=AppraisalNo%20eq%20%27{pk}%27'))
                get_targets = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyPersonalTarget',
                                                            'AppraisalNo','eq',pk))
                get_attributes = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyAttributes',
                                                            'AppraisalNo','eq',pk))
                get_attachments = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyDocumentAttachments',
                                                            'No_','eq',pk))
                get_trainings = asyncio.ensure_future(self.simple_one_filtered_data(session,
                                                        '/QyTrainingAndDevelopment',
                                                            'AppraisalNo','eq',pk))
                response = await asyncio.gather(get_appraisal,
                                                    get_targets,
                                                        get_attributes,
                                                            get_attachments,
                                                                get_trainings)
            
            
                for appraisal in response[0]: # type: ignore
                    res = appraisal
                targets = [x for x in response[1]] # type: ignore
                attributes = [x for x in response[2]] # type: ignore
                allFiles = [x for x in response[3]] # type: ignore
                trainings = [x for x in response[4]]  # type: ignore
                
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
            "file": allFiles,
            'trainings':trainings,
            'Supervisor':Supervisor,
        }
            
        return render(request, 'appraisalDetails.html', ctx)
            
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
        
class FnAppraisalGoals(UserObjectMixins,View):
    def post(self,request, pk):
        try:
            soap_headers = request.session['soap_headers']
            appraisalLine = int(request.POST.get('appraisalLine'))
            targetsSetForTheYear = request.POST.get('targetsSetForTheYear')
            weight = float(request.POST.get('weight'))
            unitOfMeasureORPerformanceIndicator = request.POST.get('unitOfMeasureORPerformanceIndicator')
            selfRating = request.POST.get('selfRating')
            supervisorRating = request.POST.get('supervisor_score')
            User_ID = request.session['User_ID']
            myAction = request.POST.get('myAction')
            print(supervisorRating)
            
            if not selfRating:
                selfRating=0
                
            if not supervisorRating:
                supervisorRating=0

            
            response = self.make_soap_request(soap_headers,'FnAppraisalGoals',pk,
                                                appraisalLine,targetsSetForTheYear,weight,
                                                    unitOfMeasureORPerformanceIndicator,
                                                        int(selfRating),int(supervisorRating),User_ID,
                                                        myAction)
            if response == True:
                messages.success(request,'success')
                return redirect('AppraisalDetails', pk=pk)
            messages.error(request,f'{response}')
            return redirect('AppraisalDetails', pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('AppraisalDetails', pk=pk)
        
class FnAppraisalTrainingAndDevelopment (UserObjectMixins,View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            appraisalLine = request.POST.get('appraisalLine')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            commentsBySupervisor = request.POST.get('commentsBySupervisor')
            User_ID = request.session['User_ID']
            myAction = request.POST.get('myAction')
            print(commentsBySupervisor)
            if not commentsBySupervisor:
                commentsBySupervisor = ''

            response = self.make_soap_request(soap_headers,'FnAppraisalTrainingAndDevelopment',
                                              pk,appraisalLine,description,duration,
                                                commentsBySupervisor,User_ID,myAction)
            if response == True:
                messages.success(request,'success')
                return redirect('AppraisalDetails', pk=pk)
            messages.error(request,f'{response}')
            return redirect('AppraisalDetails', pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('AppraisalDetails', pk=pk)
                
class FnGetAppraisalAttributes(UserObjectMixins,View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            supervisorAppraisalScore = float(request.POST.get('supervisorAppraisalScore'))
            LineNo = int(request.POST.get('LineNo'))
            myAction = request.POST.get('myAction')
            response = self.make_soap_request(soap_headers,
                                              'FnGetAppraisalAttributes',pk,
                                                supervisorAppraisalScore,
                                                    LineNo,myAction)
            if response == True:
                messages.success(request,'success')
                return redirect('AppraisalDetails', pk=pk)
            messages.error(request,f'{response}')
            return redirect('AppraisalDetails', pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('AppraisalDetails', pk=pk)
class FnSubmitEmployeeAppraisal(UserObjectMixins,View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            User_ID = request.session['User_ID']
            response = self.make_soap_request(soap_headers,
                                              'FnSubmitEmployeeAppraisal',pk,User_ID)
            if response == True:
                messages.success(request,'successfully sent')
                return redirect('Appraisals')
            messages.error(request,f'{response}')
            return redirect('AppraisalDetails', pk=pk)
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('AppraisalDetails', pk=pk)

class FnInitiateAppraisal(UserObjectMixins,View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            response = self.make_soap_request(soap_headers,
                                              'FnInitiateAppraisal',pk)
            if response == True:
                messages.success(request,'successfully sent')
                return redirect('AppraisalDetails', pk=pk)
            messages.error(request,f'{response}')
            return redirect('Appraisals')
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('Appraisals')
class FnSubmitAppraisalToSupervisor(UserObjectMixins,View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            response = self.make_soap_request(soap_headers,
                                              'FnSubmitAppraisalToSupervisor',pk)
            if response == True:
                messages.success(request,'successfully sent')
                return redirect('Appraisals')
            messages.error(request,f'{response}')
            return redirect('Appraisals')
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('Appraisals')
        
class FnSubmitAppraisalToManagerial(UserObjectMixins,View):
    def post(self,request,pk):
        try:
            soap_headers = request.session['soap_headers']
            response = self.make_soap_request(soap_headers,
                                              'FnSubmitAppraisalToManegerial',pk)
            if response == True:
                messages.success(request,'successfully sent')
                return redirect('Appraisals')
            messages.error(request,f'{response}')
            return redirect('Appraisals')
        except Exception as e:
            logging.exception(e)
            messages.error(request,f'{e}')
            return redirect('Appraisals')