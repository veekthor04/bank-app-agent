import requests
from typing import Tuple
from decimal import Decimal


class BankAppAPIClient:
    # connects to the bank API
    def __init__(
        self,
        bank_token: str,
        bank_url: str,
        bank_id: str,
        bank_name: str,
    ) -> None:
        """_summary_

        Parameters
        ----------
        bank_token : str
            Authorization token for the bank
        bank_url : str
            Base url for the bank
        bank_id : str
            Bank id
        bank_name : str
            Bank name
        """
        self.bank_token = bank_token
        self.bank_url = bank_url
        self.bank_id = bank_id
        self.bank_name = bank_name

    def intra_bank_transfer_request(
        self,
        source_account_id: str,
        destination_account_id: str,
        info: str,
        amount: Decimal,
    ) -> Tuple[int, str]:
        """Send the request to transfer money from one account to another

        Parameters
        ----------
        bank_token : str
            Authorization token for the bank
        bank_url : str
            Base url for the bank
        source_account_id : str
            Source account uuid
        destination_account_id : str
            Destination account uuid
        info : str
            Transfer detail
        amount : Decimal
            Amount

        Returns
        -------
        Tuple[int, str]
            Status code and Response text
        """
        url = self.bank_url + "transfer/"  # intra bank transfer
        headers = {
            "Authorization": f"Token {self.bank_token}",
        }
        data = {
            "source": source_account_id,
            "destination": destination_account_id,
            "info": info,
            "amount": amount,
        }

        return self.__send_request(url, headers, data)

    def retire_fund_request(
        self,
        source_account_id: str,
        destination_bank_id: str,
        info: str,
        amount: Decimal,
    ) -> Tuple[int, str]:
        """Send the request to remove fund from a bank account

        Parameters
        ----------
        source_account_id : str
            Source account UUID
        destination_bank_id : str
            Destination Bank UUID
        info : str
            Transfer detail
        amount : Decimal
            Amount

        Returns
        -------
        Tuple[int, str]
            Status code and Response text
        """
        url = f"{self.bank_url}{source_account_id}/retire/"  # retire fund url"
        headers = {
            "Authorization": f"Token {self.bank_token}",
        }
        data = {
            "dst_bank": destination_bank_id,
            "info": info,
            "amount": amount,
        }

        return self.__send_request(url, headers, data)

    def add_fund_request(
        self,
        destination_account_id: str,
        source_bank_id: str,
        info: str,
        amount: Decimal,
    ) -> Tuple[int, str]:
        """Send the request to add fund to a bank account

        Parameters
        ----------
        destination_account_id : str
            Destination account uuid
        source_bank_id : str
            Source Bank UUID
        info : str
            Account detail
        amount : Decimal
            Amount

        Returns
        -------
        Tuple[int, str]
            Status code and Response text
        """
        url = f"{self.bank_url}{destination_account_id}/add/"  # add fund url"
        headers = {
            "Authorization": f"Token {self.bank_token}",
        }
        data = {
            "src_bank": source_bank_id,
            "info": info,
            "amount": amount,
        }

        return self.__send_request(url, headers, data)

    def __send_request(
        self, url: str, headers: str, data: str
    ) -> Tuple[int, str]:
        """Sends request to the server and returns response details

        Parameters
        ----------
        url : str
            request url
        headers : str
            request headers
        data : str
            request payload

        Returns
        -------
        Tuple[int, str]
            Status code and Response text
        """

        try:
            res = requests.put(url, headers=headers, data=data)
        except requests.exceptions.ConnectionError:
            return (500, "Service is unavailable.")

        return self.__process_response(res)

    @staticmethod
    def __process_response(res: requests.Response) -> Tuple[int, str]:
        """Precess the request response to response code and response text

        Parameters
        ----------
        res : requests.Response
            request response

        Returns
        -------
        Tuple[int, str]
            Status code and Response text
        """

        response_code = res.status_code
        response_json = res.json()

        if response_code == 200 or response_code == 201:
            response_text = "Success"
        elif response_code == 400:
            response_text = "".join(
                [
                    f"{key}: {', '.join(response_json[key])}"
                    for key in response_json.keys()
                ]
            )
        else:
            response_text = "Service is unavailable"

        return response_code, response_text

    def __str__(self) -> str:
        return f"{self.bank_name}, {self.bank_id} Client"
