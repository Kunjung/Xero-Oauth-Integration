## Setup instructions

1. Add a .env file in the root folder. It should look like this:
```
XERO_CLIENT_ID=your-client-id
XERO_CLIENT_SECRET=your-client-secret
XERO_REDIRECT_URI=https://localhost:5000/callback
XERO_AUTHORIZATION_URL=https://login.xero.com/identity/connect/authorize
XERO_TOKEN_URL=https://identity.xero.com/connect/token
```

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

4. Now run the following commmands to migrate the necessary tables

```
python manage.py makemigrations
python manage.py migrate
```

5. Start the server with port 5000 and enable https using the following command
```
python manage.py runserver_plus 5000 --cert-file cert.pem --key-file key.pem
```

