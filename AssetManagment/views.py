from django.shortcuts import render
# Create your views here.
import asyncio
import base64
import logging
import aiohttp
from django.shortcuts import render, redirect
import requests
from requests import Session
from django.conf import settings as config
import datetime as dt
from django.contrib import messages
from requests.auth import HTTPBasicAuth
from zeep.client import Client
from zeep.transports import Transport
from django.views import View
from django.http import HttpResponse, JsonResponse
from asgiref.sync import sync_to_async
from myRequest.views import UserObjectMixins
from base64 import b64decode
import io as BytesIO
from django.template.loader import render_to_string
import ast
from datetime import datetime


# Create your views here.


from django.shortcuts import render
from django.http import JsonResponse
from .models import Asset
from myRequest.views import UserObjectMixins
from django.views import View
def create_asset(request):
    if request.method == 'POST':
        tag_number = request.POST.get('tag_number')
        asset = Asset(tag_number=tag_number)
        asset.save()
        return JsonResponse({'success': True})

    return render(request, 'asset.html')
class CreateAsset(UserObjectMixins, View):

    async def get(self, request):
        try:
            User_ID = await sync_to_async(request.session.__getitem__
                                          )('User_ID')

            full_name = await sync_to_async(request.session.__getitem__
                                            )('full_name')
#"full": full_name,
            async with aiohttp.ClientSession() as session:
                task_get_assets = asyncio.ensure_future(
                    self.simple_fetch_data(
                        session, "/QyFaScans"))


                response = await asyncio.gather(
                                                task_get_assets,
                                               )


                assets = [x for x in response[0]]  # type: ignore


        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError,
                aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request,
                           "Authentication Error: Invalid credentials")
            return redirect('dashboard')
        except KeyError as e:
            print(e)
            messages.info(request, "Session Expired. Please Login")
            return redirect('auth')
        except Exception as e:
            print(e)
            messages.error(
                request,
                "Whoops! Something went wrong. Please Login to Continue")
            return redirect('dashboard')

        ctx = {
            "today": self.todays_date,
           "asset":assets,
            "full": full_name,
            "User_ID": User_ID,
        }
        return render(request, 'asset.html', ctx)

    async def post(self, request):
        try:
            tagNo = request.POST.get('tagNo')

            userID = await sync_to_async(request.session.__getitem__
                                         )('User_ID')

            soap_headers = await sync_to_async(request.session.__getitem__
                                               )('soap_headers')

            response = self.make_soap_request(soap_headers, 'fnSubmitfaScan',
                                              tagNo)

            print(response)

            if response == True:
                messages.success(request, 'Success')
                return redirect('create_asset')
            if response == False:
                messages.success(request, 'Request Failed')
                return redirect('create_asset')
        except (aiohttp.ClientError, aiohttp.ServerDisconnectedError,
                aiohttp.ClientResponseError) as e:
            print(e)
            messages.error(request, "connect timed out")
            return redirect('create_asset')
        except ValueError:
            messages.error(request, 'Missing Input')
            return redirect('create_asset')
        except KeyError:
            messages.info(request, 'Session Expired, please Login')
            return redirect('auth')

        except Exception as e:
            messages.error(request, f'{e}')
            print(e)
            return redirect('create_asset')
        return redirect('create_asset')