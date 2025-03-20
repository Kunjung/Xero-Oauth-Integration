## Setup instructions

> python3 -m venv venv
> source venv/scripts/activate
> pip install -r requirements.txt
> openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
> python manage.py runserver_plus 5000 --cert-file cert.pem --key-file key.pem


