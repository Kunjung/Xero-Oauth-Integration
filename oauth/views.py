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
    context = {"title": "Hello to Xero App."}
    return render(request, "index.html", context)

def revoke_token(request):
    # Revoke token by deleting the access_token stored in session
    request.session.pop('access_token', None)
    request.session.pop('code', None)
    request.session.modified = True
    request.session.modified = True
    context = {"title": "Revoked access token"}
    return render(request, "index.html", context)

def authorize_in_xero(request):
    xero_auth_url = settings.XERO_AUTHORIZATION_URL
    client_id = settings.XERO_CLIENT_ID
    redirect_uri = settings.XERO_REDIRECT_URI
    scope = 'accounting.transactions.read'
    auth_url = f"{xero_auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}"
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
        access_token = response_data['access_token']
        refresh_token = response_data.get('refresh_token', None)
        
        # Save access_token and refresh_token in session
        request.session['access_token'] = access_token
        if refresh_token:
            request.session['refresh_token'] = refresh_token
        
        context = {"data": response_data.items(), "code": code, "title": "Authorized"}
        return render(request, "index.html", context)
    else:
        context = {"error": "Failed to get access token", "title": "Authorization failed", "status_code": 400}
        return render(request, "index.html", context)


def get_account_data_from_xero(request):
    access_token = request.session.get('access_token')
    if not access_token:
        context = {"error": "Access token missing", "status_code": 400}
        return render(request, "accounts.html", context)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Xero-tenant-id': settings.XERO_TENANT_ID
    }

    # Call the accounts api to get the accounts data from Xero
    response = requests.get(settings.XERO_ACCOUNTS_API, headers=headers)

    if response.status_code == 200:
        account_data = response.json()['Accounts']
        context = {"data": account_data}
        return render(request, "accounts.html", context)
    else:
        context = {"error": response.text, "status_code": response.status_code}
        return render(request, "accounts.html", context)


def save_account_data_to_local_db(request):
    access_token = request.session.get('access_token')
    if not access_token:
        context = {"error": "Access token missing", "status_code": 400}
        return render(request, "accounts.html", context)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Xero-tenant-id': settings.XERO_TENANT_ID
    }

    # Call the accounts api to get the accounts data from Xero
    response = requests.get(settings.XERO_ACCOUNTS_API, headers=headers)

    if response.status_code == 200:
        accounts_info = response.json()["Accounts"]
        
        # Delete all account info from local database
        # This will ensure no duplicates as well as get the latest data only returned from xero api
        Account.objects.all().delete()
        print("Previous account data deleted from local db ...")

        for account_info in accounts_info:
            required_fields = (
                'AccountID', 'Code', 'Name', 'Status', 'Type', 'TaxType', 'Class', 'EnablePaymentsToAccount',
                'ShowInExpenseClaims', 'BankAccountNumber', 'BankAccountType', 'CurrencyCode', 'ReportingCode',
                'ReportingCodeName', 'HasAttachments', 'AddToWatchlist'
            )

            # handle case when fields are missing in response json
            for field in required_fields:
                if field not in account_info:
                    if field in ('EnablePaymentsToAccount', 'ShowInExpenseClaims', 'HasAttachments', 'AddToWatchlist'):
                        account_info[field] = False
                    else:
                        account_info[field] = ''
            
            # convert date format supplied to local datetime
            timestamp = account_info["UpdatedDateUTC"].split('+')[0].split('Date(')[-1]
            timestamp = int(timestamp) / 1000
            updated_date = datetime.fromtimestamp(timestamp)

            # use ORM to create new account object and make entry into database
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
        save_to_db = True
        context = {"save_to_db": save_to_db, "data": accounts_info}
        return render(request, "accounts.html", context)
    else:
        context = {"error": response.text, "status_code": response.status_code}
        return render(request, "accounts.html", context)


def refresh_access_token(request):
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        context = {"error": "Refresh token missing", "title": "Refresh failed", "status_code": 400}
        return render(request, "index.html", context)

    token_url = settings.XERO_TOKEN_URL
    client_id = settings.XERO_CLIENT_ID
    client_secret = settings.XERO_CLIENT_SECRET
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
    else:
        context = {"error": "Failed to get refresh token", "title": "Refresh failed", "status_code": 400}
        return render(request, "index.html", context)
