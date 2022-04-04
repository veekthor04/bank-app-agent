from django.shortcuts import render

import django_tables2 as tables

from bank_agent.models import TransferRequest
from bank_agent.forms import TransferRequestForm


class TransferRequestTable(tables.Table):
    class Meta:
        model = TransferRequest


def index(request):

    form = TransferRequestForm()
    if request.method == "POST":
        form = TransferRequestForm(request.POST)

        if form.is_valid():
            transer_request: TransferRequest = form.save()
            transer_request.send_request_to_banks()

    table = TransferRequestTable(TransferRequest.objects.all())
    context = {
        "form": form,
        "table": table,
    }

    return render(request, "index.html", context)
