import numpy as np
import matplotlib.pyplot as plt

# --- 1. USER CONFIGURATION ---

# This script models the risk for a SINGLE CLIENT.
# You must get these inputs from your 'climate_risk_analyzer.py' script.

# Example Client: NOVO HORIZONTE/SP
# (Data from your other script)
CLIENT_NAME = "NOVO HORIZONTE/SP"
CLIMATE_LIKELIHOOD_SCORE = 4  # (Example: A score of 4 out of 5)

# (Data from your business)
# This is the client's TOTAL contribution to your royalties, as a decimal.
ROYALTY_IMPACT = 0.12  # (e.g., 12% of your total royalties)

# --- 2. SIMULATION PARAMETERS ---
N_SIMULATIONS = 10000  # Number of "years" to simulate

# We will model the client's "Yield Loss" based on the climate score.
# This is an assumption, but it's how you translate the score.

# We assume a Likelihood score of 5/5 means an average
# yield loss of 50% in any given "bad" year.
# A score of 4/5 (like our example) means an average loss of 40%.
# This is the "mean" of our simulation.
MEAN_YIELD_LOSS_PERCENT = (CLIMATE_LIKELIHOOD_SCORE / 5.0) * 50.0

# This is the "uncertainty". A lower number means the loss is
# always close to the mean. A higher number means it varies a lot.
STD_DEV_YIELD_LOSS = 15.0

print(f"--- Running Monte Carlo Simulation for: {CLIENT_NAME} ---")
print(f"Climate Likelihood Score: {CLIMATE_LIKELIHOOD_SCORE}/5")
print(f"Royalty Impact (I): {ROYALTY_IMPACT * 100:.1f}%")
print(f"Modeling {N_SIMULATIONS} scenarios...")

# --- 3. RUN SIMULATION ---

simulated_royalty_losses = []

for _ in range(N_SIMULATIONS):
    # Step 1: Simulate the client's yield loss for one year.
    # We use a normal distribution, centered around our "Mean Loss".
    yield_loss = np.random.normal(MEAN_YIELD_LOSS_PERCENT, STD_DEV_YIELD_LOSS)
    
    # Step 2: Clamp the value. Yield loss can't be less than 0% or more than 100%.
    yield_loss = np.clip(yield_loss, 0, 100)
    
    # Step 3: Calculate the direct loss to YOUR business.
    # If the client loses 50% of their yield, you lose 50% of *their* royalty.
    # Your total loss is (yield_loss % * client's royalty impact).
    royalty_loss_as_percent_of_total = (yield_loss / 100.0) * ROYALTY_IMPACT
    
    # Convert to a percentage for the report (e.g., 0.12 -> 12.0)
    simulated_royalty_losses.append(royalty_loss_as_percent_of_total * 100.0)

# --- 4. ANALYZE RESULTS ---

print("\n--- 📊 MONTE CARLO RESULTS 📊 ---")

# Calculate key statistics
average_loss = np.mean(simulated_royalty_losses)
std_dev_loss = np.std(simulated_royalty_losses)
max_loss = np.max(simulated_royalty_losses)

# Value at Risk (VaR) is a key risk metric.
# "VaR 95" answers: "In 95% of scenarios, what is the *maximum* loss I will see?"
# or "What is the loss I can expect to see in the worst 5% of years?"
var_90 = np.percentile(simulated_royalty_losses, 90)
var_95 = np.percentile(simulated_royalty_losses, 95)
var_99 = np.percentile(simulated_royalty_losses, 99)

print(f"\nAverage Annual Royalty Loss from this client: {average_loss:.2f}% (of your total royalties)")
print(f"Maximum Simulated Loss: {max_loss:.2f}%")
print(f"Standard Deviation (Volatility): {std_dev_loss:.2f}%")
print("\nValue at Risk (VaR) - 'How bad can it get?'")
print(f"  90% VaR: You can expect a loss of {var_90:.2f}% or less in 90% of years.")
print(f"  95% VaR: You can expect a loss of {var_95:.2f}% or less in 95% of years.")
print(f"  99% VaR: You can expect a loss of {var_99:.2f}% or less in 99% of years.")

print(f"""
Interpretation: In the worst 5% of years, you should expect to lose at least
{var_95:.2f}% of your *total* annual royalties just from this one client's
climate risk.
""")

# --- 5. VISUALIZE RESULTS ---

print("Generating histogram of possible outcomes...")

plt.figure(figsize=(10, 6))
plt.hist(simulated_royalty_losses, bins=50, density=True, alpha=0.7, label='Simulated Royalty Losses')
plt.axvline(average_loss, color='red', linestyle='dashed', linewidth=2, label=f'Average Loss ({average_loss:.2f}%)')
plt.axvline(var_95, color='orange', linestyle='dashed', linewidth=2, label=f'95% VaR ({var_95:.2f}%)')
plt.title(f'Monte Carlo Simulation of Royalty Loss from {CLIENT_NAME}')
plt.xlabel(f'Percent Loss of Your *Total* Royalties (from this one client)')
plt.ylabel('Probability Density')
plt.legend()
plt.grid(True)
plt.show()

print("--- End of Monte Carlo Simulation ---")