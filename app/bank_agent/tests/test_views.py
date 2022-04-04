from django.urls import reverse
from django.test import TestCase
from unittest.mock import patch

from bank_agent.models import Bank, TransferRequest
from bank_agent.utils import sample_bank


INDEX_URL = reverse("bank_agent:index")


class PublicViewsTests(TestCase):
    """Test the views for the bank agent"""

    def test_get_index_view(self):
        """Test index view"""
        res = self.client.get(INDEX_URL)

        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "index.html")

    @patch("bank_agent.services.BankAppAPIClient.intra_bank_transfer_request")
    def test_post_for_intra_bank_success(self, intra_bank_service):
        """Test post view when intra bank transfer request is success"""
        bank: Bank = sample_bank()
        payload = {
            "source_bank": bank.id,
            "source_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "destination_bank": bank.id,
            "destination_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "amount": 10,
            "info": "test info",
        }

        intra_bank_service.return_value = (201, "Success")
        res = self.client.post(INDEX_URL, payload)

        transfer_requests = TransferRequest.objects.all()

        self.assertEqual(transfer_requests.count(), 1)
        self.assertTrue(transfer_requests.first().completed)
        self.assertIn("Success", res.content.decode())

    @patch("bank_agent.services.BankAppAPIClient.intra_bank_transfer_request")
    def test_post_for_intra_bank_unsuccessful(
        self, intra_bank_service_service
    ):
        """Test post view when intra bank transfer request is unsuccessful"""
        bank: Bank = sample_bank()
        payload = {
            "source_bank": bank.id,
            "source_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "destination_bank": bank.id,
            "destination_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "amount": 10,
            "info": "test info",
        }

        intra_bank_service_service.return_value = (
            400,
            "source: Account does not have enough fund",
        )
        res = self.client.post(INDEX_URL, payload)

        transfer_requests = TransferRequest.objects.all()

        self.assertEqual(transfer_requests.count(), 1)
        self.assertFalse(transfer_requests.first().completed)
        self.assertIn(
            "source: Account does not have enough fund", res.content.decode()
        )

    @patch("bank_agent.services.BankAppAPIClient.retire_fund_request")
    @patch("bank_agent.services.BankAppAPIClient.add_fund_request")
    def test_post_for_inter_bank_success(
        self, retire_fund_service, add_fund_service
    ):
        """Test post view when inter bank transfer request is success"""
        bank_1: Bank = sample_bank()
        bank_2: Bank = sample_bank()
        payload = {
            "source_bank": bank_1.id,
            "source_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "destination_bank": bank_2.id,
            "destination_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "amount": 10,
            "info": "test info",
        }

        retire_fund_service.return_value = (201, "Success")
        add_fund_service.return_value = (201, "Success")
        res = self.client.post(INDEX_URL, payload)

        transfer_requests = TransferRequest.objects.all()

        self.assertEqual(transfer_requests.count(), 1)
        self.assertTrue(transfer_requests.first().completed)
        self.assertIn("Success", res.content.decode())

    @patch(
        "bank_agent.services.BankAppAPIClient.retire_fund_request",
    )
    def test_post_for_inter_bank_unsuccessful(self, retire_fund_service):
        """Test post view when inter bank transfer request is unsuccessful"""
        bank_1: Bank = sample_bank()
        bank_2: Bank = sample_bank()

        payload = {
            "source_bank": bank_1.id,
            "source_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "destination_bank": bank_2.id,
            "destination_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "amount": 10,
            "info": "test info",
        }

        retire_fund_service.return_value = (
            400,
            "source: Account does not have enough fund",
        )
        res = self.client.post(INDEX_URL, payload)

        transfer_requests = TransferRequest.objects.all()

        self.assertEqual(transfer_requests.count(), 1)
        self.assertFalse(transfer_requests.first().completed)
        self.assertIn(
            "source: Account does not have enough fund", res.content.decode()
        )

    @patch("bank_agent.services.BankAppAPIClient.retire_fund_request")
    @patch("bank_agent.services.BankAppAPIClient.add_fund_request")
    def test_post_for_inter_bank_unsuccessful_due_to_destination(
        self, retire_fund_service, add_fund_service
    ):
        """
        Test post view when inter bank transfer request is unsuccessfull
        due to incorrect destination account
        """
        bank_1: Bank = sample_bank()
        bank_2: Bank = sample_bank()
        payload = {
            "source_bank": bank_1.id,
            "source_account_id": "8bce8de8-4856-4113-aff7-0812a5c6ea29",
            "destination_bank": bank_2.id,
            "destination_account_id": "bbbadca3-2fdb-4036-ae04-c23dca10c93c",
            "amount": 10,
            "info": "test info",
        }

        retire_fund_service.return_value = (201, "Success")
        add_fund_service.return_value = (
            400,
            "destination: Object with uuid=bbbadca3-2fdb-4036-ae04-c23dca10c"
            "93c does not exist.",
        )
        res = self.client.post(INDEX_URL, payload)

        transfer_requests = TransferRequest.objects.all()

        self.assertEqual(transfer_requests.count(), 1)
        self.assertFalse(transfer_requests.first().completed)
        self.assertIn(
            "destination: Object with uuid=bbbadca3-2fdb-4036-ae04-c23dca10c"
            "93c does not exist.",
            res.content.decode(),
        )
