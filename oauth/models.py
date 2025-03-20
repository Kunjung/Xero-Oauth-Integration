from django.db import models
from datetime import datetime

# Create your models here.
class Account(models.Model):
    account_id = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    type = models.CharField(max_length=40)
    tax_type = models.CharField(max_length=40)
    account_class = models.CharField(max_length=40)
    enable_payments_to_account = models.BooleanField()
    show_in_expense_claims = models.BooleanField()
    bank_account_number = models.CharField(max_length=40)
    bank_account_type = models.CharField(max_length=40)
    currency_code = models.CharField(max_length=5)
    reporting_code = models.CharField(max_length=5)
    reporting_code_name = models.CharField(max_length=40)
    has_attachments = models.BooleanField()
    updated_date = models.DateTimeField(default=datetime.now())
    add_to_watchlist = models.BooleanField()
