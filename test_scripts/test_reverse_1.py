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
