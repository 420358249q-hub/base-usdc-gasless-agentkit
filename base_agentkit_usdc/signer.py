import time
import secrets
from typing import Dict, Any, Tuple
from eth_account import Account
from eth_account.messages import encode_typed_data

BASE_CHAIN_ID = 8453
BASE_SEPOLIA_CHAIN_ID = 84532
BASE_USDC_MAINNET = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
BASE_USDC_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"

# EIP-712 Domain for USDC (FiatTokenV2_2)
def get_eip712_domain(chain_id: int = BASE_CHAIN_ID, token_address: str = BASE_USDC_MAINNET) -> Dict[str, Any]:
    return {
        "name": "USD Coin",
        "version": "2",
        "chainId": chain_id,
        "verifyingContract": token_address
    }

# EIP-712 Type Definition for EIP-3009 TransferWithAuthorization
EIP712_TYPES = {
    "TransferWithAuthorization": [
        {"name": "from", "type": "address"},
        {"name": "to", "type": "address"},
        {"name": "value", "type": "uint256"},
        {"name": "validAfter", "type": "uint256"},
        {"name": "validBefore", "type": "uint256"},
        {"name": "nonce", "type": "bytes32"}
    ]
}

def create_transfer_authorization_data(
    from_address: str,
    to_address: str,
    amount_atomic: int,
    valid_after: int = 0,
    valid_before: int = 0,
    nonce: bytes = None,
    chain_id: int = BASE_CHAIN_ID,
    usdc_address: str = BASE_USDC_MAINNET
) -> Tuple[Dict[str, Any], bytes]:
    """Creates the EIP-712 typed data structure for USDC gasless transfer authorization."""
    if valid_before == 0:
        valid_before = int(time.time()) + 3600  # Valid for 1 hour by default
    if nonce is None:
        nonce = secrets.token_bytes(32)

    domain = get_eip712_domain(chain_id, usdc_address)
    message = {
        "from": from_address,
        "to": to_address,
        "value": amount_atomic,
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": "0x" + nonce.hex()
    }

    typed_data = {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"}
            ],
            **EIP712_TYPES
        },
        "primaryType": "TransferWithAuthorization",
        "domain": domain,
        "message": message
    }
    return typed_data, nonce

def sign_authorization(private_key: str, typed_data: Dict[str, Any]) -> Tuple[int, bytes, bytes]:
    """Signs the EIP-712 typed data and returns (v, r, s) signature components."""
    signable = encode_typed_data(full_message=typed_data)
    signed = Account.sign_message(signable, private_key=private_key)
    v = signed.v
    r = signed.r.to_bytes(32, byteorder="big")
    s = signed.s.to_bytes(32, byteorder="big")
    return v, r, s
