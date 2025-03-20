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


How to get optimal input base on previous data :

First to get understanding,we use same data above on here. 

we are going to create a simple script to explain this demo :

```
import json
```

Second extract the data :

```
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
```
data = json.loads(raw_data)
```

# ✅ Extract original transaction input (amount_start) and final output (amount_end):
```
original_input = float(data["amount_start"].split()[0])
amount_end = float(data["amount_end"].split()[0])
```

# ✅ Swap Fee (0.25% per swap) can set any base on docs or contract 
```
FEE_RATE = 0.997  # 0.25% deducted per swap
```

# ✅ Reverse Transfer Order for Backward Calculation

```
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
```
optimal_starting_input = calculate_optimal_input(amount_end, transfers)
```

# ✅ Compare Original Input vs. New Calculated Input
```
input_difference = optimal_starting_input - original_input
percentage_difference = (input_difference / original_input) * 100 if original_input != 0 else 0

print(f"\n🔥 Optimal Starting Input: {optimal_starting_input:.8f} WBNB")
print(f"🔍 Comparison: Original TX Input = {original_input:.8f} WBNB, New Optimal Input = {optimal_starting_input:.8f} WBNB")
print(f"⚖️ Difference: {input_difference:.8f} WBNB ({percentage_difference:.4f}%)")

```

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

```
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

Extra Information : How to fetch fees on V3 using venomlab studio style :
#Learning_fetch

Install graphql-request: Run the following command in your project directory to install the graphql-request package:

```
npm install graphql-request
```
Run your test scripts:
```
node fetchPairsWithMultipleFees.js
```

Fetching 1000 pairs with fees:

```
const { GraphQLClient, gql } = require('graphql-request');

// The PancakeSwap V3 Subgraph Endpoint
const endpoint = 'https://api.thegraph.com/subgraphs/name/pancakeswap/pairs';

// Initialize the GraphQL client
const client = new GraphQLClient(endpoint);

// GraphQL query to fetch pairs with their fee tiers
const query = gql`
  {
    pairs(first: 1000) {
      id
      token0 {
        symbol
      }
      token1 {
        symbol
      }
      feeTier
      liquidity
      volumeUSD
    }
  }
`;

// Function to fetch and process pairs
async function fetchPairsWithMultipleFees() {
  try {
    const data = await client.request(query);
    const pairs = data.pairs;

    // Filter pairs with multiple fee tiers
    const feeGroups = {};

    pairs.forEach(pair => {
      const feeTier = pair.feeTier;
      const pairKey = `${pair.token0.symbol}-${pair.token1.symbol}`;

      if (!feeGroups[pairKey]) {
        feeGroups[pairKey] = new Set();
      }

      feeGroups[pairKey].add(feeTier);
    });

    // Output pairs with multiple fee tiers
    console.log('Pairs with Multiple Fee Tiers:');
    for (const pair in feeGroups) {
      if (feeGroups[pair].size > 1) {
        console.log(`${pair} has the following fee tiers: ${[...feeGroups[pair]].join(', ')}`);
      }
    }

  } catch (error) {
    console.error('Error fetching data from PancakeSwap V3 Subgraph:', error);
  }
}

// Run the function
fetchPairsWithMultipleFees();
```

If you have problem package ,try using mjs module :

```
import { GraphQLClient, gql } from 'graphql-request';

// The PancakeSwap V3 Subgraph Endpoint
const endpoint = 'https://api.thegraph.com/subgraphs/name/pancakeswap/pairs';

// Initialize the GraphQL client
const client = new GraphQLClient(endpoint);

// GraphQL query to fetch pairs with their fee tiers
const query = gql`
  {
    pairs(first: 1000) {
      id
      token0 {
        symbol
      }
      token1 {
        symbol
      }
      feeTier
      liquidity
      volumeUSD
    }
  }
`;

// Function to fetch and process pairs
async function fetchPairsWithMultipleFees() {
  try {
    const data = await client.request(query);
    const pairs = data.pairs;

    // Filter pairs with multiple fee tiers
    const feeGroups = {};

    pairs.forEach(pair => {
      const feeTier = pair.feeTier;
      const pairKey = `${pair.token0.symbol}-${pair.token1.symbol}`;

      if (!feeGroups[pairKey]) {
        feeGroups[pairKey] = new Set();
      }

      feeGroups[pairKey].add(feeTier);
    });

    // Output pairs with multiple fee tiers
    console.log('Pairs with Multiple Fee Tiers:');
    for (const pair in feeGroups) {
      if (feeGroups[pair].size > 1) {
        console.log(`${pair} has the following fee tiers: ${[...feeGroups[pair]].join(', ')}`);
      }
    }

  } catch (error) {
    console.error('Error fetching data from PancakeSwap V3 Subgraph:', error);
  }
}

// Run the function
fetchPairsWithMultipleFees();
```




