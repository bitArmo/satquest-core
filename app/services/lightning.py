from breez_sdk_liquid import LiquidNetwork, default_config, ConnectRequest,  connect, BindingLiquidSdk, InputType, EventListener, SdkEvent, PrepareReceiveRequest, ReceiveAmount, PaymentMethod, PrepareReceiveResponse, ReceivePaymentRequest, PrepareSendRequest, PayAmount, PrepareSendResponse, SendPaymentRequest
from mnemonic import Mnemonic
import os
from os.path import exists
import logging
import time
from typing import Union

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
        self.mnemonic = self.read_mnemonic()
        self.sdk = self.initialize_connection(self.API_KEY, self.mnemonic)
        self.listener = SdkListener()
        self.sdk.add_event_listener(self.listener)

    def initialize_connection(self, API_KEY, mnemonic):
        config = default_config(network = LiquidNetwork.MAINNET, breez_api_key = API_KEY)
        config.working_directory = "./breez_lightning_liquid"

        try:
            connect_request = ConnectRequest(config = config, mnemonic = mnemonic.strip())  
            sdk = connect(connect_request)
            print("Connected to the network")
            return sdk
        except Exception as e:
            print(f"Error connecting to the network: {e}")
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
    
    def prepare_receive_payment(self, amount): # amount in satoshis
        try:
            current_limit = self.sdk.fetch_lightning_limits()
            print(current_limit)
            if not current_limit.receive.min_sat <= amount <= current_limit.receive.max_sat:
                raise Exception("Amount is out of range")
            optional_amount = ReceiveAmount.BITCOIN(amount)
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
        
    def prepare_send_payment(self, destination: str, amount: PayAmount = PayAmount.DRAIN):
        try:
            prepare_request = PrepareSendRequest(destination=destination, amount = amount)
            prepare_response = self.sdk.prepare_send_payment(prepare_request)
            return prepare_response
        except Exception as e:
            logging.error(f"Error preparing send payment: {e}")
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