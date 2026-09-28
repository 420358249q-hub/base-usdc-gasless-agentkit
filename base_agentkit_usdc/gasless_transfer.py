from typing import Dict, Any, Optional, Tuple
from web3 import Web3
from eth_account import Account
from .signer import (
    BASE_CHAIN_ID,
    BASE_USDC_MAINNET,
    create_transfer_authorization_data,
    sign_authorization
)

# USDC ABI excerpt for EIP-3009 transferWithAuthorization
USDC_EIP3009_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "from", "type": "address"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "value", "type": "uint256"},
            {"internalType": "uint256", "name": "validAfter", "type": "uint256"},
            {"internalType": "uint256", "name": "validBefore", "type": "uint256"},
            {"internalType": "bytes32", "name": "nonce", "type": "bytes32"},
            {"internalType": "uint8", "name": "v", "type": "uint8"},
            {"internalType": "bytes32", "name": "r", "type": "bytes32"},
            {"internalType": "bytes32", "name": "s", "type": "bytes32"}
        ],
        "name": "transferWithAuthorization",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "authorizer", "type": "address"},
            {"internalType": "bytes32", "name": "nonce", "type": "bytes32"}
        ],
        "name": "authorizationState",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class BaseGaslessUsdcClient:
    """
    High-level client for executing gasless USDC transfers on Base.
    Allows user/agent wallets with ZERO ETH balance to send USDC,
    while a relayer / sponsor submits the signed EIP-3009 transaction.
    """
    def __init__(
        self,
        rpc_url: str = "https://mainnet.base.org",
        chain_id: int = BASE_CHAIN_ID,
        usdc_address: str = BASE_USDC_MAINNET,
        w3: Optional[Web3] = None
    ):
        self.chain_id = chain_id
        self.usdc_address = Web3.to_checksum_address(usdc_address)
        self.w3 = w3 or Web3(Web3.HTTPProvider(rpc_url))
        self.contract = self.w3.eth.contract(address=self.usdc_address, abi=USDC_EIP3009_ABI)

    def prepare_authorization(
        self,
        from_address: str,
        to_address: str,
        amount_atomic: int,
        valid_after: int = 0,
        valid_before: int = 0,
        nonce: bytes = None
    ) -> Tuple[Dict[str, Any], bytes]:
        return create_transfer_authorization_data(
            from_address=Web3.to_checksum_address(from_address),
            to_address=Web3.to_checksum_address(to_address),
            amount_atomic=amount_atomic,
            valid_after=valid_after,
            valid_before=valid_before,
            nonce=nonce,
            chain_id=self.chain_id,
            usdc_address=self.usdc_address
        )

    def sign_authorization(self, private_key: str, typed_data: Dict[str, Any]):
        return sign_authorization(private_key, typed_data)

    def is_nonce_used(self, authorizer: str, nonce: bytes) -> bool:
        """Checks if the authorization nonce has already been consumed."""
        return self.contract.functions.authorizationState(
            Web3.to_checksum_address(authorizer),
            nonce
        ).call()

    def build_relayer_transaction(
        self,
        relayer_address: str,
        authorization_data: Dict[str, Any],
        v: int,
        r: bytes,
        s: bytes
    ) -> Dict[str, Any]:
        """Builds the unsigned transaction payload for the relayer to broadcast."""
        msg = authorization_data["message"]
        tx = self.contract.functions.transferWithAuthorization(
            Web3.to_checksum_address(msg["from"]),
            Web3.to_checksum_address(msg["to"]),
            msg["value"],
            msg["validAfter"],
            msg["validBefore"],
            bytes.fromhex(msg["nonce"][2:]),
            v,
            r,
            s
        ).build_transaction({
            "from": Web3.to_checksum_address(relayer_address),
            "chainId": self.chain_id,
            "nonce": self.w3.eth.get_transaction_count(Web3.to_checksum_address(relayer_address)),
            "gas": 100000
        })
        return tx
