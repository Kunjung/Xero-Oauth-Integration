from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.shortcuts import redirect

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the oauth index.")

def authorize(request):
    xero_auth_url = settings.XERO_AUTHORIZATION_URL
    client_id = settings.XERO_CLIENT_ID
    # client_secret = settings.XERO_CLIENT_SECRET
    redirect_uri = settings.XERO_REDIRECT_URI
    # scope = 'openid profile email accounting.transactions'  # Define the scope you need
    scope = "files.read profile files accounting.contacts.read payroll.settings accounting.attachments accounting.journals.read accounting.attachments.read projects.read accounting.transactions.read accounting.settings.read payroll.payslip payroll.payruns payroll.employees accounting.transactions assets accounting.contacts accounting.budgets.read offline_access assets.read payroll.timesheets projects openid email accounting.reports.read accounting.settings"
    auth_url = f"{xero_auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
    print("auth_url: ", auth_url)
    return redirect(auth_url)

def callback(request):
    # Get the authorization code from the request
    code = request.GET.get('code')

    # Exchange the authorization code for an access token
    token_url = settings.XERO_TOKEN_URL
    redirect_uri = settings.XERO_REDIRECT_URI
    client_id = settings.XERO_CLIENT_ID
    client_secret = settings.XERO_CLIENT_SECRET

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }

    auth = HTTPBasicAuth(client_id, client_secret)

    response = requests.post(token_url, data=data, auth=auth)
    response_data = response.json()

    if response.status_code == 200:
        # Save the token data to session or database
        access_token = response_data['access_token']
        refresh_token = response_data.get('refresh_token', None)
        
        # You can store these tokens in the session or database
        request.session['access_token'] = access_token
        if refresh_token:
            request.session['refresh_token'] = refresh_token
        
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "Failed to get access token"}, status=400)
    

def get_xero_data(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Access token missing"}, status=400)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Xero-tenant-id': 'your-tenant-id',  # Replace with the tenant ID from Xero
    }

    # Example: Get a list of invoices
    response = requests.get('https://api.xero.com/api.xro/2.0/Invoices', headers=headers)

    if response.status_code == 200:
        return JsonResponse(response.json())
    else:
        return JsonResponse({"error": response.text}, status=response.status_code)


def refresh_access_token(request):
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return JsonResponse({"error": "Refresh token missing"}, status=400)

    token_url = settings.XERO_TOKEN_URL
    client_id = settings.XERO_CLIENT_ID
    client_secret = settings.XERO_CLIENT_SECRET
    redirect_uri = settings.XERO_REDIRECT_URI

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        request.session['access_token'] = access_token
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "Failed to refresh token"}, status=400)
