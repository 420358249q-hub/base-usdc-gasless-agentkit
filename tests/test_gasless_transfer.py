import os
import sys
import pytest
from eth_account import Account
from web3 import Web3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base_agentkit_usdc import (
    BaseGaslessUsdcClient,
    BASE_CHAIN_ID,
    BASE_USDC_MAINNET,
    create_transfer_authorization_data,
    sign_authorization
)

def test_prepare_authorization():
    user = Account.create()
    recipient = Account.create()
    amount = 10_000_000 # 10 USDC

    typed_data, nonce = create_transfer_authorization_data(
        from_address=user.address,
        to_address=recipient.address,
        amount_atomic=amount,
        chain_id=BASE_CHAIN_ID,
        usdc_address=BASE_USDC_MAINNET
    )

    assert typed_data["primaryType"] == "TransferWithAuthorization"
    assert typed_data["domain"]["chainId"] == BASE_CHAIN_ID
    assert typed_data["domain"]["verifyingContract"] == BASE_USDC_MAINNET
    assert typed_data["message"]["from"] == user.address
    assert typed_data["message"]["to"] == recipient.address
    assert typed_data["message"]["value"] == amount
    assert len(nonce) == 32

def test_sign_authorization():
    user = Account.create()
    recipient = Account.create()
    amount = 1_000_000 # 1 USDC

    typed_data, nonce = create_transfer_authorization_data(
        from_address=user.address,
        to_address=recipient.address,
        amount_atomic=amount
    )

    v, r, s = sign_authorization(user.key.hex(), typed_data)
    assert v in (27, 28)
    assert len(r) == 32
    assert len(s) == 32

def test_client_initialization():
    client = BaseGaslessUsdcClient()
    assert client.chain_id == BASE_CHAIN_ID
    assert client.usdc_address == Web3.to_checksum_address(BASE_USDC_MAINNET)
