from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.shortcuts import redirect
from datetime import datetime

from .models import Account

# Create your views here.
def index(request):
    context = {"title": "Hello to Varicon App."}
    return render(request, "index.html", context)

def revoke_token(request):
    request.session.pop('access_token', None)
    request.session.pop('code', None)
    request.session.modified = True
    request.session.modified = True
    context = {"title": "Revoked access token"}
    return render(request, "index.html", context)

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
    request.session["code"] = code

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
        
        # print("response_data: ")
        # print(response_data)
        # return JsonResponse(response_data)
        context = {"data": response_data.items(), "code": code, "title": "Authorized"}
        return render(request, "index.html", context)
    else:
        return JsonResponse({"error": "Failed to get access token"}, status=400)


def get_xero_data(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Access token missing"}, status=400)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Xero-tenant-id': 'd8baa8b5-e3c8-462e-b015-4b53458a4efe',  # Replace with the tenant ID from Xero
    }

    # Example: Get a list of invoices
    response = requests.get('https://api.xero.com/api.xro/2.0/Accounts', headers=headers)

    if response.status_code == 200:
        # return JsonResponse(response.json())
        account_data = response.json()['Accounts']
        context = {"data": account_data}
        return render(request, "accounts.html", context)
    else:
        return JsonResponse({"error": response.text}, status=response.status_code)


def save_xero_data(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Access token missing"}, status=400)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Xero-tenant-id': 'd8baa8b5-e3c8-462e-b015-4b53458a4efe',  # Replace with the tenant ID from Xero
    }

    # Example: Get a list of invoices
    response = requests.get('https://api.xero.com/api.xro/2.0/Accounts', headers=headers)

    if response.status_code == 200:
        accounts_info = response.json()["Accounts"]
        for account_info in accounts_info:
            # print("account_info: ", account_info)
            # print("type: ", type(account_info))
            required_fields = (
                'AccountID', 'Code', 'Name', 'Status', 'Type', 'TaxType', 'Class', 'EnablePaymentsToAccount',
                'ShowInExpenseClaims', 'BankAccountNumber', 'BankAccountType', 'CurrencyCode', 'ReportingCode',
                'ReportingCodeName', 'HasAttachments', 'AddToWatchlist'
            )
            for field in required_fields:
                if field not in account_info:
                    if field in ('EnablePaymentsToAccount', 'ShowInExpenseClaims', 'HasAttachments', 'AddToWatchlist'):
                        account_info[field] = False
                    else:
                        account_info[field] = ''
            timestamp = account_info["UpdatedDateUTC"].split('+')[0].split('Date(')[-1]
            timestamp = int(timestamp) / 1000
            updated_date = datetime.fromtimestamp(timestamp)
            account = Account(
                account_id = account_info["AccountID"],
                code = account_info["Code"],
                name = account_info["Name"],
                status = account_info["Status"],
                type = account_info["Type"],
                tax_type = account_info["TaxType"],
                account_class = account_info["Class"],
                enable_payments_to_account = account_info["EnablePaymentsToAccount"],
                show_in_expense_claims = account_info["ShowInExpenseClaims"],
                bank_account_number = account_info["BankAccountNumber"],
                bank_account_type = account_info["BankAccountType"],
                currency_code = account_info["CurrencyCode"],
                reporting_code = account_info["ReportingCode"],
                reporting_code_name = account_info["ReportingCodeName"],
                has_attachments = account_info["HasAttachments"],
                updated_date = updated_date,  # account_info["UpdatedDateUTC"],
                add_to_watchlist = account_info["AddToWatchlist"]
            )
            account.save()
        # return JsonResponse(response.json())
        save_to_db = True
        context = {"save_to_db": save_to_db, "data": accounts_info}
        return render(request, "accounts.html", context)
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
    code = request.session.get('code')

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
        context = {"data": response_data.items(), "title": "Refreshed", "code": code}
        return render(request, "index.html", context)
        # return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "Failed to refresh token"}, status=400)
