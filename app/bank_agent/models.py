from typing import Tuple
from django.db import models
from django.core.validators import MinValueValidator

from bank_agent.services import (
    # intra_bank_transfer_request,
    # retire_fund_request,
    # add_fund_request,
    BankAppAPIClient,
)


class Bank(models.Model):
    """Bank model with url details"""

    name = models.CharField(max_length=255)
    uuid = models.UUIDField(unique=True)
    token = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self) -> str:
        return self.name


class TransferRequest(models.Model):
    """Transfer Request Model to store transfer requests made"""

    source_bank: Bank = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        related_name="source_bank_transfer_request",
    )
    source_account_id = models.UUIDField()
    destination_bank: Bank = models.ForeignKey(
        Bank,
        on_delete=models.CASCADE,
        related_name="destination_bank_transfer_request",
    )
    destination_account_id = models.UUIDField()
    amount = models.DecimalField(
        decimal_places=2, max_digits=18, validators=[MinValueValidator(1)]
    )
    info = models.CharField(max_length=255)
    service_detail = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return (
            f"Transfer of {self.amount} from {self.source_account_id} "
            f"to {self.destination_account_id}"
        )

    class Meta:
        ordering = ["-created"]

    def send_request_to_banks(self) -> None:
        """sends request to banks"""

        if self.source_bank == self.destination_bank:
            status_code, response_detail = self.__make_intrabank_transfer()

            if status_code == 201:
                # successful transfer
                self.completed = True
            self.service_detail = response_detail

        else:
            status_code, response_detail = self.__make_interbank_transfer()

            if status_code == 201:
                # successful transfer
                self.completed = True
            self.service_detail = response_detail
        self.save()

    def __make_intrabank_transfer(self) -> Tuple[int, str]:
        """Makes an intra-bank transfer from source to destination account"""
        transfer_bank_service = BankAppAPIClient(
            self.source_bank.token,
            self.source_bank.url,
            str(self.source_bank.uuid),
            self.source_bank.name,
        )

        # intra bank transfer
        return transfer_bank_service.intra_bank_transfer_request(
            str(self.source_account_id),
            str(self.destination_account_id),
            self.info,
            self.amount,
        )

    def __make_interbank_transfer(self) -> Tuple[int, str]:
        """Makes an inter-bank transfer from source to destination account"""
        source_bank_service = BankAppAPIClient(
            self.source_bank.token,
            self.source_bank.url,
            str(self.source_bank.uuid),
            self.source_bank.name,
        )

        destination_bank_service = BankAppAPIClient(
            self.destination_bank.token,
            self.destination_bank.url,
            str(self.destination_bank.uuid),
            self.destination_bank.name,
        )

        # retire fund from source account
        status_code, response_detail = self.__retire_fund_from_source(
            source_bank_service
        )

        if status_code == 201:
            # successful fund retire, add fund to destination account
            status_code, response_detail = self.__add_fund_to_destination(
                destination_bank_service
            )

            if status_code == 201:
                # successful fund retire and fund add
                self.completed = True

            else:
                # successful fund retire and but not fund add, fund reversal
                self.__reverse_fund_to_source(source_bank_service)

        return status_code, response_detail

    def __retire_fund_from_source(
        self, source_bank_service: BankAppAPIClient
    ) -> Tuple[int, str]:
        """Retires fund from source account"""
        return source_bank_service.retire_fund_request(
            str(self.source_account_id),
            str(self.destination_bank.uuid),
            self.info,
            self.amount,
        )

    def __add_fund_to_destination(
        self, destination_bank_service: BankAppAPIClient
    ) -> Tuple[int, str]:
        """Adds fund to destination account"""
        return destination_bank_service.add_fund_request(
            str(self.destination_account_id),
            str(self.source_bank.uuid),
            self.info,
            self.amount,
        )

    def __reverse_fund_to_source(
        self, source_bank_service: BankAppAPIClient
    ) -> Tuple[int, str]:
        """Adds fund to source account"""
        return source_bank_service.add_fund_request(
            str(self.destination_account_id),
            str(self.source_bank.uuid),
            self.info,
            self.amount,
        )
