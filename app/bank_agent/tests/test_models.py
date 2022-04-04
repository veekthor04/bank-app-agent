from uuid import uuid4
from django.test import TestCase
from django.db.models import signals

from bank_agent.models import Bank, TransferRequest
from bank_agent.signals import post_save_transfer_created_receiver
from bank_agent.utils import sample_bank


class ModelTests(TestCase):
    def setUp(self):
        # do some setup
        signals.post_save.disconnect(
            post_save_transfer_created_receiver, sender=TransferRequest
        )

    def test_bank_str(self):
        """Test string representation for bank model"""
        bank: Bank = Bank.objects.create(
            name="test_name",
            uuid="8bce8de8-4856-4113-aff7-0812a5c6ea29",
            url="http://test_url/",
            token="test_token",
        )
        self.assertEqual(str(bank), bank.name)

    def test_transfer_request_str(self):
        """Test string representation for transfer request model"""
        transfer_request: TransferRequest = TransferRequest.objects.create(
            source_bank=sample_bank(uuid=uuid4()),
            source_account_id=uuid4(),
            destination_bank=sample_bank(uuid=uuid4()),
            destination_account_id=uuid4(),
            amount=10,
        )
        self.assertEqual(
            str(transfer_request),
            f"Transfer of {transfer_request.amount} from "
            f"{transfer_request.source_account_id} to "
            f"{transfer_request.destination_account_id}",
        )
