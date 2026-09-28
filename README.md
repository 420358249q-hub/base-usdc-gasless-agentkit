# Base AgentKit: Gasless USDC Transfer (EIP-3009 & Paymaster)

This module provides an unabridged, production-ready implementation of **Gasless USDC Transfers** on Base Mainnet (`8453`) and Base Sepolia (`84532`).

## Why Gasless Transfer?
Standard ERC-20 transfers require the sender to hold native ETH on Base to pay gas fees. This creates severe onboarding friction for autonomous AI agents and new users.
USDC on Base (contract `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`) implements **EIP-3009 (`transferWithAuthorization`)**, allowing users to sign an off-chain EIP-712 payload. Any relayer, paymaster, or agent can broadcast the transaction, paying a fraction of a cent in L2 gas, while the sender pays **0 ETH**.

---

## Architecture

```
[ Zero-ETH User / Agent ]
           │
           ▼
    1. Creates TransferWithAuthorization Typed Data
    2. Signs EIP-712 Offline (v, r, s)
           │
           ▼
   [ Relayer / Paymaster / Sponsor ]
           │
           ▼
    3. Calls USDC.transferWithAuthorization(from, to, value, validAfter, validBefore, nonce, v, r, s)
           │
           ▼
    4. Base L2 Contract settles transfer without touching user's ETH balance
```

## Quickstart

```bash
# 1. Install dependencies
pip install web3 eth-account pytest

# 2. Run the interactive demonstration
python examples/run_gasless_demo.py

# 3. Run unit tests
pytest tests/
```

## Production Parameters
* **Base Mainnet Chain ID**: `8453`
* **Base USDC Address**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
* **EIP-712 Domain Name**: `USD Coin`
* **EIP-712 Domain Version**: `2`
