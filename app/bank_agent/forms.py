from django import forms

from bank_agent.models import TransferRequest


class TransferRequestForm(forms.ModelForm):
    """Model form for TransferRequest"""
    class Meta:
        model = TransferRequest
        fields = (
            "source_bank",
            "source_account_id",
            "destination_bank",
            "destination_account_id",
            "amount",
            "info",
        )
