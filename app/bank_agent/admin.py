from django.contrib import admin

from bank_agent.models import Bank, TransferRequest


admin.site.register(Bank)
admin.site.register(TransferRequest)
