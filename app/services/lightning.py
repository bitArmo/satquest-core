from breez_sdk_liquid import LiquidNetwork, default_config, ConnectRequest,  connect, BindingLiquidSdk, InputType, EventListener, SdkEvent, PrepareReceiveRequest, ReceiveAmount, PaymentMethod, PrepareReceiveResponse, ReceivePaymentRequest, PrepareSendRequest, PayAmount, PrepareSendResponse, SendPaymentRequest, PrepareLnUrlPayRequest, LnUrlPayRequest, PrepareLnUrlPayResponse
from mnemonic import Mnemonic
import os
from os.path import exists
import logging
import time
from typing import Union, Optional

API_KEY = os.getenv("BREEZ_API_KEY")

class SdkListener(EventListener):
    """
    A listener class for handling Breez SDK events.

    This class extends the EventListener from breez_sdk_liquid and implements
    custom event handling logic, particularly for tracking successful payments.

    Attributes:
        paid (list): A list to store destinations of successful payments.
    """

    def __init__(self):
        """
        Initialize the SdkListener.

        Sets up an empty list to track paid destinations.
        """
        self.synced = False
        self.paid = []

    def on_event(self, event):
        if isinstance(event, SdkEvent.SYNCED):
            self.synced = True
        else:
            print(event)
        if isinstance(event, SdkEvent.PAYMENT_SUCCEEDED):
            if event.details.destination:
                self.paid.append(event.details.destination)
    
    def is_paid(self, destination: str):
        return destination in self.paid
    
    def is_synced(self):
        return self.synced
    
class LightningService:
    def __init__(self):
        self.API_KEY = API_KEY
        if not self.API_KEY:
            raise ValueError("BREEZ_API_KEY environment variable is not set")
            
        self.mnemonic = self.read_mnemonic()
        self.sdk = self.initialize_connection(self.API_KEY, self.mnemonic)
        if not self.sdk:
            raise RuntimeError("Failed to initialize Breez SDK")
            
        self.listener = SdkListener()
        try:
            self.sdk.add_event_listener(self.listener)
        except Exception as e:
            raise RuntimeError(f"Failed to add event listener: {e}")

    def initialize_connection(self, API_KEY, mnemonic):
        config = default_config(network = LiquidNetwork.MAINNET, breez_api_key = API_KEY)
        config.working_directory = "./breez_lightning_liquid"

        try:
            connect_request = ConnectRequest(config = config, mnemonic = mnemonic.strip())  
            sdk = connect(connect_request)
            print("Connected to the network")
            return sdk
        except Exception as e:
            logging.error(f"Error connecting to the network: {e}")
            return None
        
    def is_paid(self, destination: str):
        return self.listener.is_paid(destination)

    def is_synced(self):
        return self.listener.is_synced()
    
    def disconnect(self):
        try:
            self.sdk.disconnect()
        except Exception as error:
            logging.error(error)
            raise

    def generate_mnemonic(self):
        mnemo = Mnemonic("english")
        return mnemo.generate(strength=128)
    
    def read_mnemonic(self):
        if exists('phrase'):
            with open('phrase') as f:
                mnemonic = f.readline().strip()
                if not mnemonic:
                    mnemonic = self.generate_mnemonic()
                    with open('phrase', 'w') as f:
                        f.write(mnemonic)
                f.close()
                return mnemonic
        else:
            mnemonic = self.generate_mnemonic()
            with open('phrase', 'w') as f:
                f.write(mnemonic)
                f.close()
            return mnemonic

    def get_node_info(self):
        try:
            self.wait_for_synced()
            node_info = self.sdk.get_info()
            return node_info
        except Exception as e:
            logging.error(f"Error getting node info: {e}")
            return None
        
    def get_balance(self):
        try:
            node_info = self.sdk.get_info()
            return node_info.wallet_info.balance_sat
        except Exception as e:
            logging.error(f"Error getting balance: {e}")
            return None
    def get_lightning_limits(self):
        try:
            limits = self.sdk.fetch_lightning_limits()
            return limits
        except Exception as e:
            logging.error(f"Error getting lightning limits: {e}")
            return None
    
    # RECEIVE PAYMENT METHODS
    def prepare_receive_lightning_payment(self, amount: Optional[int] = None): # amount in satoshis
        try:
            current_limit = self.sdk.fetch_lightning_limits()
            if not current_limit.receive.min_sat <= amount <= current_limit.receive.max_sat:
                raise Exception("Amount is out of limit range")
            optional_amount = ReceiveAmount.BITCOIN(amount) if amount else None
            prepare_request = PrepareReceiveRequest(payment_method = PaymentMethod.LIGHTNING, amount = optional_amount)
            prepare_response = self.sdk.prepare_receive_payment(prepare_request)
            return prepare_response
        except Exception as e:
            logging.error(f"Error receiving payment: {e}")
            raise
        
    def receive_payment(self,  prepare_response: PrepareReceiveResponse):
        try:
            req = ReceivePaymentRequest(prepare_response=prepare_response)
            res = self.sdk.receive_payment(req)
            destination = res.destination
            if destination:
                print(f"Payment at {destination}")
                print('Waiting for payment:', res.destination)
                self.wait_for_payment(destination = res.destination)
            else:
                print("Payment failed")
        except Exception as error:
            logging.error(error)
            raise
        
    # SEND PAYMENT METHODS
    def prepare_send_payment(self, destination: str, amount: PayAmount = PayAmount.DRAIN):
        try:
            if amount != PayAmount.DRAIN:
                amount = PayAmount.BITCOIN(amount)
            prepare_request = PrepareSendRequest(destination=destination, amount = amount)
            prepare_response = self.sdk.prepare_send_payment(prepare_request)
            return prepare_response
        except Exception as e:
            logging.error(f"Error preparing send payment: {e}")
            raise
    def prepare_lnurl_pay(self, destination: str):
        try:
            parsed_input = self.sdk.parse(destination)
            if isinstance(parsed_input, InputType.LN_URL_PAY):
                amount = PayAmount.BITCOIN(1800)
                optional_comment = "<comment>"
                optional_validate_success_action_url = True
                req = PrepareLnUrlPayRequest(data = parsed_input.data, amount = amount, bip353_address = parsed_input.bip353_address, comment = optional_comment, validate_success_action_url = optional_validate_success_action_url)
                prepare_response = self.sdk.prepare_lnurl_pay(req)
                return prepare_response
            else:
                raise Exception("Invalid destination")
        except Exception as error:
            logging.error(error)
            raise
    def send_lnurl_pay(self, prepare_response: PrepareLnUrlPayResponse):
        try:
            req = LnUrlPayRequest(prepare_response=prepare_response)
            res = self.sdk.lnurl_pay(req)
            return res
        except Exception as error:
            logging.error(error)
            raise
        
    def send_payment(self, prepare_response: PrepareSendResponse):
        try:
            req = SendPaymentRequest(prepare_response=prepare_response)
            res = self.sdk.send_payment(req)
            if res.payment.destination:
                print('Sending payment:', res.payment.destination)
                self.wait_for_payment(res.payment.destination)
            return res
        except Exception as e:
            logging.error(f"Error sending payment: {e}")
            raise

    def fee_in_sats(self, prepare_response: Union[PrepareReceiveResponse, PrepareSendResponse]):
        try:
            return prepare_response.fees_sat
        except Exception as e:
            logging.error(f"Error getting fee in sats: {e}")
            return None
        
    def wait_for_payment(self, destination: str):
        while True:
            if self.is_paid(destination):
                break
            time.sleep(1)

    def wait_for_synced(self):
        while True:
            if self.is_synced():
                break
            time.sleep(1)

if __name__ == "__main__":
    lightning_service = LightningService()
    print(lightning_service.get_node_info())
    req = lightning_service.prepare_lnurl_pay(destination="mo_harchegani@sats.mobi")
    print(req)
    res = lightning_service.send_lnurl_pay(req)
    print(res)
