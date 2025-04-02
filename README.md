## Setup instructions

0. Clone the repo to your local machine
```
git clone https://github.com/Kunjung/Xero-Oauth-Integration.git
cd Xero-Oauth-Integration
```

1. Add a .env file in the root folder. It should look like this:
```
XERO_CLIENT_ID=your-client-id
XERO_CLIENT_SECRET=your-client-secret
XERO_REDIRECT_URI=https://localhost:5000/callback
XERO_AUTHORIZATION_URL=https://login.xero.com/identity/connect/authorize
XERO_TOKEN_URL=https://identity.xero.com/connect/token
XERO_TENANT_ID=your-tenant-id
XERO_ACCOUNTS_API=https://api.xero.com/api.xro/2.0/Accounts
```
The tenant id can be found here: https://api-explorer.xero.com/accounting/accounts/getaccounts in the auto-generated headers.

The client id and client secret are to be setup in the xero developer panel here: https://developer.xero.com/app/manage/

2. Go back to the project root and run the following commands to setup virtual environment and install dependencies

```
python3 -m venv venv
source venv/scripts/activate
pip install -r requirements.txt
```

3. Currently for Xero, the http://localhost is not supported, it only accepts https://localhost, so use the following command to enable https

```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

4. Update the database credentials in settings.py for postgresql as follows:

```
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database_name',
        'USER': 'user_name',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432'
    }
```

5. Now run the following commmands to migrate the necessary tables and also create a superuser admin to view the accounts data from admin dashboard.

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. Start the server with port 5000 and enable https using the following command
```
python manage.py runserver_plus 5000 --cert-file cert.pem --key-file key.pem
```

