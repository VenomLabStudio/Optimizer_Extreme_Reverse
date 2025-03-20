# Optimizer_Extreme_Reverse
This script calculates the optimal starting input and output from Backtrack V10 data MEV for a multi-hop token swap by working backward from the final output amount


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

```
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


