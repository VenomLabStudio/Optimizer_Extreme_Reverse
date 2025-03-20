# Optimizer_Extreme_Reverse
This script calculates the optimal starting input and output from Backtrack V10 data MEV for a multi-hop token swap by working backward from the final output amount

![Alt text](reverse.webp)



Understanding the concept "REVERSE BACKTRACK" when able to use when NOT to Use.
_______________________________________________________________________________
Prepared by VenomLab Studio || MEV BACKTRACK V10 || MR.MARKI

When to Use Reserves vs. When Not to Use Reserves
In DeFi swaps, reserves refer to the liquidity pool balances of tokens in an AMM (Automated Market Maker) like Uniswap or PancakeSwap. Whether we need to use reserves depends on the swap calculation method:

✅ When to Use Reserves:
When calculating swap amounts using AMM formulas:

If using the constant product formula
```
(x * y = k)
```
we must use reserve balances to calculate precise amounts.
Example:
```
amount_out = (reserve_out * amount_in) / (reserve_in + amount_in) (adjusted for fees)
```
When estimating slippage and price impact:

Slippage depends on the size of the swap relative to the reserves.
Large swaps significantly shift the price, requiring reserve-based calculations.
When simulating a trade without on-chain execution:

Off-chain calculations (e.g., pricing models) need reserves to predict the expected output.
______________________________________________________________________________________________


❌ When NOT to Use Reserves:
When analyzing a completed swap (post-trade analysis):

If transaction data already contains the exact amounts swapped, reserves are not needed.
We only need to work backward from the final output to find the required input.
When optimizing for a better starting input:

Instead of using pool reserves, we can reverse the swap flow (accounting for fees) using the actual transaction data.
This method works when we already know the amounts received in each step.
When dealing with token transfers instead of direct swaps:

If a transaction involves multiple transfers without interacting with a liquidity pool, reserves are unnecessary.
Why This Script Does NOT Use Reserves
The script analyzes a completed swap using recorded transaction amounts.
We already have the exact output received at each step.
Instead of estimating swap amounts using reserves, we reverse-calculate the input needed with a simple fee-adjusted division.
Thus, reserves are not required for this type of post-swap input optimization. 🚀

for this example,we are using data extract from BACKTRACK V10 (MEV SEARCHER) :

```json
 "transaction_time": "2 seconds ago",
        "gas_price": "1.00 Gwei",
        "gas_limit": "591450 gas",
        "gas_used": "0.000199416 Gwei",
        "transaction_status": " [32mSuccess [0m",
        "total_bep20_transfers": "4",
        "date_today": "14/03/2025",
        "current_time": "6:04:10 pm",
        "timestamp": "3 seconds ago // Displaying the formatted timestamp",
        "total_tokens": "3",
        "total_pools": "4",
        "total_swaps": "4",
        "total_addresses": "7",
        "amount_start": "0.00381093 WBNB",
        "amount_end": "0.00436520 WBNB",
        "profit_loss": "$0.321136",
        "percentage_pnl": "+14.54",
        "transaction_path": " [38;5;189m [1mswap 1: WBNB > swap 2: wSHIB > swap 3: wBTC > swap 4: WBNB [0m // Fluorescent baby blue and bold for the path",
        "transfers": [
            {
                "transfer_number": 1,
                "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
                "to": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B (pancakeswap_v2, wSHIB / WBNB)",
                "amount": "0.003810931158961923 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            },
            {
                "transfer_number": 2,
                "from": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B",
                "to": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3 (pancakeswap_v2, wSHIB / wBTC)",
                "amount": "29968166569.407544 wSHIB",
                "token_name": "wShiba",
                "token_address": "0"
            },
            {
                "transfer_number": 3,
                "from": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3",
                "to": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861 (pancakeswap_v2, wBTC / WBNB)",
                "amount": "13091859.15557748 wBTC",
                "token_name": "wBitcoin",
                "token_address": "0"
            },
            {
                "transfer_number": 4,
                "from": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861",
                "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c (Unknown DEX, Unknown Token Pool)",
                "amount": "0.004365196915818284 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            }
        ]
    }
]
```
This mev data showing profit with +14% gaining from mev arbitrage.But do you know we can imporve the trade size by using formula :
________________________________________________________________________________________________________________________________

## Summary of Used Formulas

| #  | Formula | Purpose |
|----|---------|---------|
| 1  | `optimal_input = amount_out / FEE_RATE` | Reverse swap fee effect |
| 2  | `price_change = optimal_input - previous_input` | Compute absolute input change |
| 3  | `percentage_change = (price_change / previous_input) × 100` | Show relative change per swap |
| 4  | `input_difference = optimal_starting_input - original_input` | Compare total input difference |
| 5  | `percentage_difference = (input_difference / original_input) × 100` | Show efficiency gain (%) |


How to get optimal input base on previous data :

First to get understanding,we use same data above on here. 

we are going to create a simple script to explain this demo :

```python
import json
```

Second extract the data :

```json
# ✅ Given Raw Transaction Data
raw_data = """
{
    "amount_start": "0.00381093 WBNB",
    "amount_end": "0.00436520 WBNB",
    "transfers": [
        {
            "transfer_number": 1,
            "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
            "to": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B",
            "amount": "0.003810931158961923 WBNB"
        },
        {
            "transfer_number": 2,
            "from": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B",
            "to": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3",
            "amount": "29968166569.407544 wSHIB"
        },
        {
            "transfer_number": 3,
            "from": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3",
            "to": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861",
            "amount": "13091859.15557748 wBTC"
        },
        {
            "transfer_number": 4,
            "from": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861",
            "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
            "amount": "0.004365196915818284 WBNB"
        }
    ]
}
"""
```

# ✅ Parse JSON Data:
```python
data = json.loads(raw_data)
```

# ✅ Extract original transaction input (amount_start) and final output (amount_end):
```python
original_input = float(data["amount_start"].split()[0])
amount_end = float(data["amount_end"].split()[0])
```

# ✅ Swap Fee (0.25% per swap) can set any base on docs or contract 
```python
FEE_RATE = 0.997  # 0.25% deducted per swap
```

# ✅ Reverse Transfer Order for Backward Calculation

```python
transfers = data["transfers"][::-1]  

def calculate_optimal_input(amount_out, swaps):
    """Calculate the required starting input to get the desired output."""
    optimal_input = amount_out  

    for i, swap in enumerate(swaps):
        # Extract the output amount of the current swap
        output_amount = float(swap["amount"].split()[0])

        if output_amount > 0:
            previous_input = optimal_input  # Store previous value
            optimal_input /= FEE_RATE  # Reverse the fee deduction

            # Compare previous and latest input price
            price_change = optimal_input - previous_input
            percentage_change = (price_change / previous_input) * 100 if previous_input != 0 else 0

            print(f"Step {i+1}: Needed input = {optimal_input:.8f} (Before: {previous_input:.8f}, Change: {price_change:.8f} WBNB, {percentage_change:.4f}%)")
        else:
            print(f"⚠️ Warning: Zero output detected at step {i+1}!")

    return optimal_input
```
# ✅ Compute & Display Optimal Input
```python
optimal_starting_input = calculate_optimal_input(amount_end, transfers)
```

# ✅ Compare Original Input vs. New Calculated Input
```python
input_difference = optimal_starting_input - original_input
percentage_difference = (input_difference / original_input) * 100 if original_input != 0 else 0

print(f"\n🔥 Optimal Starting Input: {optimal_starting_input:.8f} WBNB")
print(f"🔍 Comparison: Original TX Input = {original_input:.8f} WBNB, New Optimal Input = {optimal_starting_input:.8f} WBNB")
print(f"⚖️ Difference: {input_difference:.8f} WBNB ({percentage_difference:.4f}%)")

```

![Demo GIF](data.gif)


Full Scripts :

```python
import json

# ✅ Given Raw Transaction Data
raw_data = """
{
    "amount_start": "0.00381093 WBNB",
    "amount_end": "0.00436520 WBNB",
    "transfers": [
        {
            "transfer_number": 1,
            "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
            "to": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B",
            "amount": "0.003810931158961923 WBNB"
        },
        {
            "transfer_number": 2,
            "from": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B",
            "to": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3",
            "amount": "29968166569.407544 wSHIB"
        },
        {
            "transfer_number": 3,
            "from": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3",
            "to": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861",
            "amount": "13091859.15557748 wBTC"
        },
        {
            "transfer_number": 4,
            "from": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861",
            "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
            "amount": "0.004365196915818284 WBNB"
        }
    ]
}
"""

# ✅ Parse JSON Data
data = json.loads(raw_data)

# ✅ Extract original transaction input (amount_start) and final output (amount_end)
original_input = float(data["amount_start"].split()[0])
amount_end = float(data["amount_end"].split()[0])

# ✅ Swap Fee (0.25% per swap)
FEE_RATE = 0.997  # 0.25% deducted per swap

# ✅ Reverse Transfer Order for Backward Calculation
transfers = data["transfers"][::-1]  

def calculate_optimal_input(amount_out, swaps):
    """Calculate the required starting input to get the desired output."""
    optimal_input = amount_out  

    for i, swap in enumerate(swaps):
        # Extract the output amount of the current swap
        output_amount = float(swap["amount"].split()[0])

        if output_amount > 0:
            previous_input = optimal_input  # Store previous value
            optimal_input /= FEE_RATE  # Reverse the fee deduction

            # Compare previous and latest input price
            price_change = optimal_input - previous_input
            percentage_change = (price_change / previous_input) * 100 if previous_input != 0 else 0

            print(f"Step {i+1}: Needed input = {optimal_input:.8f} (Before: {previous_input:.8f}, Change: {price_change:.8f} WBNB, {percentage_change:.4f}%)")
        else:
            print(f"⚠️ Warning: Zero output detected at step {i+1}!")

    return optimal_input

# ✅ Compute & Display Optimal Input
optimal_starting_input = calculate_optimal_input(amount_end, transfers)

# ✅ Compare Original Input vs. New Calculated Input
input_difference = optimal_starting_input - original_input
percentage_difference = (input_difference / original_input) * 100 if original_input != 0 else 0

print(f"\n🔥 Optimal Starting Input: {optimal_starting_input:.8f} WBNB")
print(f"🔍 Comparison: Original TX Input = {original_input:.8f} WBNB, New Optimal Input = {optimal_starting_input:.8f} WBNB")
print(f"⚖️ Difference: {input_difference:.8f} WBNB ({percentage_difference:.4f}%)")
```

Output Reponse :

```python
PS D:\New folder> python computeIn.py
Step 1: Needed input = 0.00437834 (Before: 0.00436520, Change: 0.00001314 WBNB, 0.3009%)
Step 2: Needed input = 0.00439151 (Before: 0.00437834, Change: 0.00001317 WBNB, 0.3009%)
Step 3: Needed input = 0.00440472 (Before: 0.00439151, Change: 0.00001321 WBNB, 0.3009%)
Step 4: Needed input = 0.00441798 (Before: 0.00440472, Change: 0.00001325 WBNB, 0.3009%)

🔥 Optimal Starting Input: 0.00441798 WBNB
🔍 Comparison: Original TX Input = 0.00381093 WBNB, New Optimal Input = 0.00441798 WBNB
⚖️ Difference: 0.00060705 WBNB (15.9291%)
```

By comparing the original input
```
🔍 Comparison: Original TX Input = 0.00381093 WBNB, New Optimal Input = 0.00441798 WBNB
```

The script performs backward calculations starting from the final output to determine how much input is required initially, considering the fee deducted at each swap step.

__________________________________________________________________________________________________________________________________________________________________________________________________

Instead manually hardcode the fees in the script,we are going to get actual gas fees and etc by using :

Transaction Fee Calculation: The actual transaction fee is computed using the formula:
```
Transaction Fee=Gas Price×Gas Used
```
# PancakeSwap Swap Fees

## PancakeSwap V2

The standard swap fee on PancakeSwap V2 is **0.25%**.

### Breakdown of the fee:
- **0.17%**: Goes to **liquidity providers (LPs)**.
- **0.03%**: Contributes to the **PancakeSwap treasury**.
- **0.05%**: Sent to the **auto-compounding liquidity pool** for **LP rewards**.

### Example:

- If you swap 100 USDT for 1000 BNB, a fee of **0.25%** will be deducted (0.25 USDT).

---

## PancakeSwap V3

PancakeSwap V3 offers **flexible fees** depending on the risk profile of the liquidity pool:

### Fee Tiers:
- **0.05%**: For **low-risk assets** (e.g., stablecoins).
- **0.25%**: For **medium-risk assets** (e.g., common trading pairs).
- **1%**: For **high-risk assets** (e.g., volatile or less liquid pairs).

### Example:

- If you swap between two stablecoins, the fee could be as low as **0.05%**.
- If you swap between two highly volatile tokens, the fee could be as high as **1%**.

---

### Summary:

- **PancakeSwap V2 Fee**: **0.25%** (Standard fee, split between LPs, treasury, and rewards).
- **PancakeSwap V3 Fee**: **0.05% - 1%** (Flexible, based on liquidity pool risk profile).

For more details, check out the [PancakeSwap Documentation](https://pancakeswap.finance).


Fetching Actual Gas Fees: The gas price and gas used are dynamically fetched using the Web3 provider

```
(w3.eth.getTransaction(transaction_hash)), which provides real-time data for the transaction.
```
Conversion to BNB: The fee is converted from Wei to BNB (or from Gwei to the native token) to match the transaction format.

________________________________________________________________________________________________________________________________

==============================================================================================================================


#Example Raw Json Data from BACKTRACKV10 (MEV SEARCHER)

```json
[
    {
        "detection": "Matching Transaction MEV ARBITRAGE Detected",
        "transfers": []
    },
    {
        "detection": "Matching Transaction MEV ARBITRAGE Detected",
        "from": "0x000000000E9e87cB030A951f10062810bdC1B117",
        "value_sent": "0.0 ETH",
        "transaction_link": "https://bscscan.com/tx/0x1553d95b1afc6c610bb0aad6a49b74f27301f10951979b32e21ec1afda965e0d",
        "transaction_time": "2 seconds ago",
        "gas_price": "1.00 Gwei",
        "gas_limit": "591450 gas",
        "gas_used": "0.000199416 Gwei",
        "transaction_status": " [32mSuccess [0m",
        "total_bep20_transfers": "4",
        "date_today": "14/03/2025",
        "current_time": "6:04:10 pm",
        "timestamp": "3 seconds ago // Displaying the formatted timestamp",
        "total_tokens": "3",
        "total_pools": "4",
        "total_swaps": "4",
        "total_addresses": "7",
        "amount_start": "0.00381093 WBNB",
        "amount_end": "0.00436520 WBNB",
        "profit_loss": "$0.321136",
        "percentage_pnl": "+14.54",
        "transaction_path": " [38;5;189m [1mswap 1: WBNB > swap 2: wSHIB > swap 3: wBTC > swap 4: WBNB [0m // Fluorescent baby blue and bold for the path",
        "transfers": [
            {
                "transfer_number": 1,
                "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
                "to": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B (pancakeswap_v2, wSHIB / WBNB)",
                "amount": "0.003810931158961923 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            },
            {
                "transfer_number": 2,
                "from": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B",
                "to": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3 (pancakeswap_v2, wSHIB / wBTC)",
                "amount": "29968166569.407544 wSHIB",
                "token_name": "wShiba",
                "token_address": "0"
            },
            {
                "transfer_number": 3,
                "from": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3",
                "to": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861 (pancakeswap_v2, wBTC / WBNB)",
                "amount": "13091859.15557748 wBTC",
                "token_name": "wBitcoin",
                "token_address": "0"
            },
            {
                "transfer_number": 4,
                "from": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861",
                "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c (Unknown DEX, Unknown Token Pool)",
                "amount": "0.004365196915818284 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            }
        ]
    },
    {
        "detection": "Matching Transaction MEV ARBITRAGE Detected",
        "from": "0x00000000009e560932B2D1B4161c7ccD7F5c1FAb",
        "value_sent": "0.0 ETH",
        "transaction_link": "https://bscscan.com/tx/0x4df3532f2053b8d0a8feef0c2237dfbc4402ec2bf27f2c7c690674c4a2e95950",
        "transaction_time": "1 second ago",
        "gas_price": "1.00 Gwei",
        "gas_limit": "1019898 gas",
        "gas_used": "0.0003187 Gwei",
        "transaction_status": " [32mSuccess [0m",
        "total_bep20_transfers": "6",
        "date_today": "14/03/2025",
        "current_time": "6:27:41 pm",
        "timestamp": "1 second ago // Displaying the formatted timestamp",
        "total_tokens": "3",
        "total_pools": "5",
        "total_swaps": "6",
        "total_addresses": "8",
        "amount_start": "245.84 USDT",
        "amount_end": "0.427612 WBNB",
        "profit_loss": "$2.16",
        "percentage_pnl": "+0.88",
        "transaction_path": " [38;5;189m [1mswap 1: USDT > swap 2: RED > swap 3: RED > swap 4: WBNB > swap 5: USDT > swap 6: WBNB [0m // Fluorescent baby blue and bold for the path",
        "transfers": [
            {
                "transfer_number": 1,
                "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
                "to": "0x0eF6FC9Aa0A48AADa260ae93C6a6A0Ce59794e34 (pancakeswap_v2, RED / USDT)",
                "amount": "245.840941721450159647 USDT",
                "token_name": "Tether USD",
                "token_address": "0"
            },
            {
                "transfer_number": 2,
                "from": "0x0eF6FC9Aa0A48AADa260ae93C6a6A0Ce59794e34",
                "to": "0xB0ec48CC71D9e1F6811db88366E24269528267C5 (Unknown DEX, Unknown Token Pool)",
                "amount": "12600.592612850694493259 RED",
                "token_name": "RED",
                "token_address": "0"
            },
            {
                "transfer_number": 3,
                "from": "0x0eF6FC9Aa0A48AADa260ae93C6a6A0Ce59794e34",
                "to": "0x34A4AbE4722D535279f6211e029A046EdF2B6ae4 (pancakeswap_v2, RED / WBNB)",
                "amount": "2507517.929957288204158625 RED",
                "token_name": "RED",
                "token_address": "0"
            },
            {
                "transfer_number": 4,
                "from": "0x34A4AbE4722D535279f6211e029A046EdF2B6ae4",
                "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c (Unknown DEX, Unknown Token Pool)",
                "amount": "0.427612061029644369 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            },
            {
                "transfer_number": 5,
                "from": "0x172fcD41E0913e95784454622d1c3724f546f849",
                "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c (Unknown DEX, Unknown Token Pool)",
                "amount": "247.735082834813280822 USDT",
                "token_name": "Tether USD",
                "token_address": "0"
            },
            {
                "transfer_number": 6,
                "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
                "to": "0x172fcD41E0913e95784454622d1c3724f546f849 (pancakeswap-v3-bsc, USDT / WBNB 0.01%)",
                "amount": "0.427612061029644369 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            }
        ]
    },
    {
        "detection": "Matching Transaction MEV ARBITRAGE Detected",
        "from": "0x00000000009f30BF58f8CC15772009F1f2F841f6",
        "value_sent": "0.0 ETH",
        "transaction_link": "https://bscscan.com/tx/0x456fe5721450a996bee5ffd3096a1a6fba00cd8282efffb8fef8f4a902500da9",
        "transaction_time": "2 seconds ago",
        "gas_price": "0.00 Gwei",
        "gas_limit": "242625 gas",
        "gas_used": "0.000174566 Gwei",
        "transaction_status": " [32mSuccess [0m",
        "total_bep20_transfers": "3",
        "date_today": "14/03/2025",
        "current_time": "8:46:45 pm",
        "timestamp": "8 seconds ago // Displaying the formatted timestamp",
        "total_tokens": "3",
        "total_pools": "4",
        "total_swaps": "6",
        "total_addresses": "7",
        "amount_start": "0.137766 WBNB",
        "amount_end": "79.77 USDT",
        "profit_loss": "$0.120037",
        "percentage_pnl": "+0.15",
        "transaction_path": " [38;5;189m [1mswap 1: WBNB > swap 2: USDC > swap 3: USDT > swap 4: USDC > swap 5: WBNB > swap 6: USDT [0m // Fluorescent baby blue and bold for the path",
        "transfers": [
            {
                "transfer_number": 1,
                "from": "0xc322439592F9729FE956CB019B0D7bCe9A72589E",
                "to": "0x250691ec7fEFC329b3134DD86883658BEfF776D0 (pancakeswap_v2, Holi / WBNB)",
                "amount": "45736.819826639857721526 Holi",
                "token_name": "Holi",
                "token_address": "0"
            },
            {
                "transfer_number": 2,
                "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
                "to": "0xc322439592F9729FE956CB019B0D7bCe9A72589E (pancakeswap-v3-bsc, Holi / WBNB 0.25%)",
                "amount": "0.00421333015442372 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            },
            {
                "transfer_number": 3,
                "from": "0x250691ec7fEFC329b3134DD86883658BEfF776D0",
                "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c (Unknown DEX, Unknown Token Pool)",
                "amount": "0.005009237125451256 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            }
        ]
    }
]
```
To fetch data mev from Server backtrack V10 you need to have unique token api and rpc.Please contact Team VenomLab Studio.
 or using SDK Libraries "sdk_venom"

Fetching Data from data.json in JavaScript
Fetching data from a data.json file can be done using JavaScript in both Node.js and browser environments. Below are different methods based on your use case.

| Use Case           | Method                          |
|--------------------|--------------------------------|
| Browser (Frontend) | `fetch()`                      |
| Node.js (Sync)    | `fs.readFileSync()`            |
| Node.js (Async)   | `fs.promises.readFile()`       |
| Node.js (CommonJS) | `require('./data.json')`      |
| Node.js (ES Modules) | `import fs from 'fs'`       |
| Remote JSON (API) | `axios.get('url')`            |

##### Assume you have Backtrack V10  
All data extract from BacktrackV10  fetched will be saved into memory, including a log report in `.txt` and `data.json`.

This step if your directories doesn't have "data.json"

Now we build simple script using python turn data on log report .txt into json format and sent into data.json

```python
import json
import os
import re

# File paths
input_file = r"D:\New folder\infotx.txt"
output_file = r"D:\New folder\data.json"

# Regular expressions for transaction details
patterns = {
    "method": r"➡️ Method: (.+)",
    "from": r"➡️ From: (.+)",
    "to": r"➡️ To: (.+)",
    "value_sent": r"➡️ Value Sent: (.+)",
    "transaction_hash": r"➡️ Transaction Hash: (.+)",
    "transaction_link": r"➡️ Transaction Link: (.+)",
    "transaction_time": r"➡️ Transaction Time: (.+)",
    "gas_price": r"➡️ Gas Price: (.+)",
    "gas_limit": r"➡️ Gas Limit: (.+)",
    "gas_used": r"➡️ Gas Used \(Tx Fees\): (.+)",
    "transaction_status": r"➡️ Transaction Status: (.+)",
    "total_bep20_transfers": r"🪙 \[Total BEP20 Token Transfers\]: (\d+)"
}

# Regex patterns for transaction summary details
summary_patterns = {
    "date_today": r"🗓️ \*\*Date Today\*\*: (.+)",
    "current_time": r"⏰ \*\*Current Time\*\*: (.+)",
    "timestamp": r"🕒 \*\*Timestamp\*\*: (.+)",
    "total_tokens": r"🔹 \*\*Total Tokens Involved\*\*: (\d+) Token\(s\)",
    "total_pools": r"💰 \*\*Total Pools\*\*: (\d+) Pool\(s\)",
    "total_swaps": r"🔄 \*\*Total Leg Swaps\*\*: (\d+) Swap\(s\)",
    "total_addresses": r"🤖 \*\*Total Smart Contracts \(Addresses\)\*\*: (\d+) Address\(es\)",
    "amount_start": r"💸 \*\*Amount Start\*\*: (.+?) \(Converted: (.+?) USD\)",
    "amount_end": r"💰 \*\*Amount End\*\*: (.+?) \(Converted: (.+?) USD\)",
    "profit_loss": r"💹 \*\*Profit/Loss\*\*: (.+?) USD",
    "percentage_pnl": r"📊 \*\*Percentage PnL\*\*: (.+?)%",
    "transaction_path": r"🌐 \*\*Transaction Path\*\*: (.+)"
}

# Regex pattern for individual token transfers
transfer_pattern = re.compile(
    r"🔹 Transfer (\d+):\s*"
    r"➡️ From: (.+?)\s*"
    r"➡️ To: (.+?)\s*"
    r"➡️ Amount: (.+?)\s*"
    r"➡️ Token Name: (.+?)\s*"
    r"➡️ Token Address: (.+?)\s*",
    re.DOTALL
)

# Pattern for splitting multiple transactions
transaction_split_pattern = r"📡 \[Matching Transaction MEV ARBITRAGE Detected\]:=*"

# Read the file content
with open(input_file, "r", encoding="utf-8") as file:
    content = file.read()

# Split content into multiple transactions
transaction_blocks = re.split(transaction_split_pattern, content)
transactions = []

for block in transaction_blocks:
    if block.strip():  # Ignore empty blocks
        transaction_data = {"detection": "Matching Transaction MEV ARBITRAGE Detected"}

        # Extract general transaction details
        for key, pattern in patterns.items():
            match = re.search(pattern, block)
            if match:
                transaction_data[key] = match.group(1)

        # Extract summary details
        for key, pattern in summary_patterns.items():
            match = re.search(pattern, block)
            if match:
                transaction_data[key] = match.group(1)

        # Extract transfer details
        transfers = []
        for match in transfer_pattern.finditer(block):
            transfers.append({
                "transfer_number": int(match.group(1)),
                "from": match.group(2),
                "to": match.group(3),
                "amount": match.group(4),
                "token_name": match.group(5),
                "token_address": match.group(6)
            })

        transaction_data["transfers"] = transfers
        transactions.append(transaction_data)

# Load existing JSON data if the file already exists
if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as json_file:
        try:
            existing_data = json.load(json_file)
            if isinstance(existing_data, list):
                existing_data.extend(transactions)
            else:
                existing_data = transactions  # Overwrite if incorrect format
        except json.JSONDecodeError:
            existing_data = transactions  # Handle broken JSON file
else:
    existing_data = transactions

# Save to JSON file
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(existing_data, json_file, indent=4)

print(f"[LOG] Extracted {len(transactions)} transactions saved to {output_file}")
```

on your data.json will look something like this :
```json
 "transaction_time": "2 seconds ago",
        "gas_price": "1.00 Gwei",
        "gas_limit": "591450 gas",
        "gas_used": "0.000199416 Gwei",
        "transaction_status": " [32mSuccess [0m",
        "total_bep20_transfers": "4",
        "date_today": "14/03/2025",
        "current_time": "6:04:10 pm",
        "timestamp": "3 seconds ago // Displaying the formatted timestamp",
        "total_tokens": "3",
        "total_pools": "4",
        "total_swaps": "4",
        "total_addresses": "7",
        "amount_start": "0.00381093 WBNB",
        "amount_end": "0.00436520 WBNB",
        "profit_loss": "$0.321136",
        "percentage_pnl": "+14.54",
        "transaction_path": " [38;5;189m [1mswap 1: WBNB > swap 2: wSHIB > swap 3: wBTC > swap 4: WBNB [0m // Fluorescent baby blue and bold for the path",
        "transfers": [
            {
                "transfer_number": 1,
                "from": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c",
                "to": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B (pancakeswap_v2, wSHIB / WBNB)",
                "amount": "0.003810931158961923 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            },
            {
                "transfer_number": 2,
                "from": "0x74C2F69FB0CB5Df4317A538B51C0A8186F31c08B",
                "to": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3 (pancakeswap_v2, wSHIB / wBTC)",
                "amount": "29968166569.407544 wSHIB",
                "token_name": "wShiba",
                "token_address": "0"
            },
            {
                "transfer_number": 3,
                "from": "0xADE812e9302dC9AE52F961A60DD30e16889b2Ab3",
                "to": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861 (pancakeswap_v2, wBTC / WBNB)",
                "amount": "13091859.15557748 wBTC",
                "token_name": "wBitcoin",
                "token_address": "0"
            },
            {
                "transfer_number": 4,
                "from": "0x62EA4676582a373dDC2FEACdd7a1F0b339206861",
                "to": "0xB5CB0555A1D28C9DfdbC14017dae131d5c1cc19c (Unknown DEX, Unknown Token Pool)",
                "amount": "0.004365196915818284 WBNB",
                "token_name": "Wrapped BNB",
                "token_address": "0"
            }
        ]
    },
```

You also can create your own file.txt insert all data transaction you had into "thisfile.txt" any name,than use code above to extract into data.json.

now we are going to create new scripts without hardcoding fixed data into the file,instead fetching directly from raw data.json 

>Only Read Single Transaction data and return single data compute:

```python
import json

# ✅ Load Data from data.json
with open("data.json", "r") as file:
    all_data = json.load(file)

# ✅ Select the first transaction entry
data = all_data[0]  # Assuming we take the first transaction from the list

# ✅ Extract original transaction input (amount_start) and final output (amount_end)
original_input = float(data["amount_start"].split()[0])
amount_end = float(data["amount_end"].split()[0])

# ✅ Swap Fee (0.25% per swap)
FEE_RATE = 0.997  # 0.25% deducted per swap

# ✅ Reverse Transfer Order for Backward Calculation
transfers = data["transfers"][::-1]  

def calculate_optimal_input(amount_out, swaps):
    """Calculate the required starting input to get the desired output."""
    optimal_input = amount_out  

    for i, swap in enumerate(swaps):
        # Extract the output amount of the current swap
        output_amount = float(swap["amount"].split()[0])

        if output_amount > 0:
            previous_input = optimal_input  # Store previous value
            optimal_input /= FEE_RATE  # Reverse the fee deduction

            # Compare previous and latest input price
            price_change = optimal_input - previous_input
            percentage_change = (price_change / previous_input) * 100 if previous_input != 0 else 0

            print(f"Step {i+1}: Needed input = {optimal_input:.8f} (Before: {previous_input:.8f}, Change: {price_change:.8f} WBNB, {percentage_change:.4f}%)")
        else:
            print(f"⚠️ Warning: Zero output detected at step {i+1}!")

    return optimal_input

# ✅ Compute & Display Optimal Input
optimal_starting_input = calculate_optimal_input(amount_end, transfers)

# ✅ Compare Original Input vs. New Calculated Input
input_difference = optimal_starting_input - original_input
percentage_difference = (input_difference / original_input) * 100 if original_input != 0 else 0

print(f"\n🔥 Optimal Starting Input: {optimal_starting_input:.8f} WBNB")
print(f"🔍 Comparison: Original TX Input = {original_input:.8f} WBNB, New Optimal Input = {optimal_starting_input:.8f} WBNB")
print(f"⚖️ Difference: {input_difference:.8f} WBNB ({percentage_difference:.4f}%)")
```

>Output Response from run above:
```javascript
PS D:\New folder> python computein.py
Step 1: Needed input = 0.00437834 (Before: 0.00436520, Change: 0.00001314 WBNB, 0.3009%)
Step 2: Needed input = 0.00439151 (Before: 0.00437834, Change: 0.00001317 WBNB, 0.3009%)
Step 3: Needed input = 0.00440472 (Before: 0.00439151, Change: 0.00001321 WBNB, 0.3009%)
Step 4: Needed input = 0.00441798 (Before: 0.00440472, Change: 0.00001325 WBNB, 0.3009%)

🔥 Optimal Starting Input: 0.00441798 WBNB
🔍 Comparison: Original TX Input = 0.00381093 WBNB, New Optimal Input = 0.00441798 WBNB
⚖️ Difference: 0.00060705 WBNB (15.9291%)
```

>Multi handling reading data transaction on data.json:

```python
import json

# ✅ Load Data from data.json
with open("data.json", "r") as file:
    all_data = json.load(file)

# ✅ Swap Fee (0.25% per swap)
FEE_RATE = 0.997  # 0.25% deducted per swap

def calculate_optimal_input(transaction, idx):
    """Calculate the required starting input to get the desired output."""

    # ✅ Get transaction hash safely
    tx_hash = transaction.get("hash", f"Unknown_TX_{idx}")

    original_input = float(transaction["amount_start"].split()[0])
    amount_end = float(transaction["amount_end"].split()[0])

    transfers = transaction.get("transfers", [])[::-1]  # Reverse transfers list

    print(f"📌 Transaction {idx}: Hash {tx_hash}")

    if not transfers:
        print("  ⚠️ Warning: No transfer data found! Skipping...\n")
        return

    optimal_input = amount_end  
    for i, swap in enumerate(transfers):
        output_amount = float(swap["amount"].split()[0])

        if output_amount > 0:
            previous_input = optimal_input  # Store previous value
            optimal_input /= FEE_RATE  # Reverse the fee deduction

            # Compare previous and latest input price
            price_change = optimal_input - previous_input
            percentage_change = (price_change / previous_input) * 100 if previous_input != 0 else 0

            print(f"  Step {i+1}: Needed input = {optimal_input:.8f} (Before: {previous_input:.8f}, Change: {price_change:.8f} WBNB, {percentage_change:.4f}%)")
        else:
            print(f"  ⚠️ Warning: Zero output detected at step {i+1}!")

    # ✅ Compare Original Input vs. New Calculated Input
    input_difference = optimal_input - original_input
    percentage_difference = (input_difference / original_input) * 100 if original_input != 0 else 0

    print(f"\n  🔥 Optimal Starting Input: {optimal_input:.8f} WBNB")
    print(f"  🔍 Comparison: Original TX Input = {original_input:.8f} WBNB, New Optimal Input = {optimal_input:.8f} WBNB")
    print(f"  ⚖️ Difference: {input_difference:.8f} WBNB ({percentage_difference:.4f}%)\n")
    print("="*60)

# ✅ Process all transactions in data.json
print("\n🚀 Processing Multiple Transactions...\n")
for idx, transaction in enumerate(all_data, start=1):
    calculate_optimal_input(transaction, idx)
```

Output Response from multi reading transaction :

```python
🚀 Processing Multiple Transactions...

📌 Transaction 1: Hash Unknown_TX_1
  Step 1: Needed input = 0.00437834 (Before: 0.00436520, Change: 0.00001314 WBNB, 0.3009%)
  Step 2: Needed input = 0.00439151 (Before: 0.00437834, Change: 0.00001317 WBNB, 0.3009%)
  Step 3: Needed input = 0.00440472 (Before: 0.00439151, Change: 0.00001321 WBNB, 0.3009%)
  Step 4: Needed input = 0.00441798 (Before: 0.00440472, Change: 0.00001325 WBNB, 0.3009%)

  🔥 Optimal Starting Input: 0.00441798 WBNB
  🔍 Comparison: Original TX Input = 0.00381093 WBNB, New Optimal Input = 0.00441798 WBNB
  ⚖️ Difference: 0.00060705 WBNB (15.9291%)

============================================================
📌 Transaction 2: Hash Unknown_TX_2
  Step 1: Needed input = 0.42889870 (Before: 0.42761200, Change: 0.00128670 WBNB, 0.3009%)
  Step 2: Needed input = 0.43018926 (Before: 0.42889870, Change: 0.00129057 WBNB, 0.3009%)
  Step 3: Needed input = 0.43148372 (Before: 0.43018926, Change: 0.00129445 WBNB, 0.3009%)
  Step 4: Needed input = 0.43278206 (Before: 0.43148372, Change: 0.00129835 WBNB, 0.3009%)
  Step 5: Needed input = 0.43408431 (Before: 0.43278206, Change: 0.00130225 WBNB, 0.3009%)
  Step 6: Needed input = 0.43539049 (Before: 0.43408431, Change: 0.00130617 WBNB, 0.3009%)

  🔥 Optimal Starting Input: 0.43539049 WBNB
  🔍 Comparison: Original TX Input = 245.84000000 WBNB, New Optimal Input = 0.43539049 WBNB
  ⚖️ Difference: -245.40460951 WBNB (-99.8229%)

============================================================
📌 Transaction 3: Hash Unknown_TX_3
  Step 1: Needed input = 80.01003009 (Before: 79.77000000, Change: 0.24003009 WBNB, 0.3009%)
  Step 2: Needed input = 80.25078244 (Before: 80.01003009, Change: 0.24075235 WBNB, 0.3009%)
  Step 3: Needed input = 80.49225922 (Before: 80.25078244, Change: 0.24147678 WBNB, 0.3009%)

  🔥 Optimal Starting Input: 80.49225922 WBNB
  🔍 Comparison: Original TX Input = 0.13776600 WBNB, New Optimal Input = 80.49225922 WBNB
  ⚖️ Difference: 80.35449322 WBNB (58326.7956%)

============================================================
```


####Now as you can see there is small issue about optimal input has highly high or highly low jump.Why this happen? 
>Because the data tx on amountIN and amountOUT
start with different currency wbnb and usdt or usdt wbnb.Script above only works if amount start and ending have same currency such as wbnb >wbnb / usdt>usdt /Busd>Busd.

>Now we need to adjust

handle cases where the start currency and end currency differ (e.g., WBNB → USDT). This requires normalizing the values using real-time exchange rates (e.g., WBNB to USD conversion).

Solution Approach:
>Identify Currency Type → Extract the currency symbol (e.g., WBNB, USDT) from amount_start and amount_end.
>Use a Price Feed → Convert all values to a common base unit (e.g., USD).
>Adjust Calculation → If the start and end currencies are different, normalize them using the price.



