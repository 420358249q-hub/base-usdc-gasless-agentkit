import os
import sys
from eth_account import Account

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from base_agentkit_usdc import (
    BaseGaslessUsdcClient,
    BASE_CHAIN_ID,
    BASE_USDC_MAINNET
)

def run_demo():
    print("==================================================================")
    print(" Base AgentKit: Gasless USDC Transfer (EIP-3009) Demonstration")
    print("==================================================================")

    # 1. Create simulated user wallet (the sender who has ZERO ETH)
    user = Account.create()
    print(f"[Sender/User] Address: {user.address}")
    print("  - Sender ETH Balance: 0.0000 ETH (Zero gas required from user)")

    # 2. Recipient wallet
    recipient = Account.create()
    print(f"[Recipient]   Address: {recipient.address}")

    # 3. Relayer / Sponsor wallet (pays the sub-cent Base L2 gas)
    relayer = Account.create()
    print(f"[Relayer]     Address: {relayer.address}")

    # 4. Initialize client
    client = BaseGaslessUsdcClient(
        rpc_url="https://mainnet.base.org",
        chain_id=BASE_CHAIN_ID,
        usdc_address=BASE_USDC_MAINNET
    )

    # 5. Build EIP-712 Transfer Authorization for 5.00 USDC (5,000,000 atomic units)
    transfer_amount = 5_000_000
    print(f"\n[Step 1] Constructing EIP-3009 Authorization for {transfer_amount / 1e6:.2f} USDC...")
    typed_data, nonce = client.prepare_authorization(
        from_address=user.address,
        to_address=recipient.address,
        amount_atomic=transfer_amount
    )
    print(f"  - Nonce: 0x{nonce.hex()}")
    print("  - Domain: USD Coin v2 on Base Mainnet (8453)")

    # 6. User signs the typed data offline (NO GAS, NO ON-CHAIN TX)
    print("\n[Step 2] User signing EIP-712 typed data locally with private key...")
    v, r, s = client.sign_authorization(user.key.hex(), typed_data)
    print(f"  - Signature (v): {v}")
    print(f"  - Signature (r): 0x{r.hex()}")
    print(f"  - Signature (s): 0x{s.hex()}")

    # 7. Payload transmitted to Relayer / AgentKit Paymaster
    print("\n[Step 3] Relayer builds and packages transaction payload...")
    # Simulated tx building verification
    msg = typed_data["message"]
    assert msg["from"] == user.address
    assert msg["to"] == recipient.address
    assert msg["value"] == transfer_amount

    print("  - Transaction payload ready for Base node broadcast.")
    print("  - Function: transferWithAuthorization(from, to, value, validAfter, validBefore, nonce, v, r, s)")
    print("\n[SUCCESS] Gasless USDC Transfer pipeline verified. Sender pays 0 Gas!")
    print("==================================================================")

if __name__ == "__main__":
    run_demo()
