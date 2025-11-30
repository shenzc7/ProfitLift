# ProfitLift User Manual

## Installation
1. Download the `ProfitLift-Setup.exe` installer.
2. Run the installer and follow the prompts.
3. Launch **ProfitLift** from your Desktop or Start Menu.

## Getting Started
When you first open ProfitLift, you will see the Welcome Dashboard. This gives you a high-level view of your data's potential.

## Using the Dashboard

### Rules Page
This is your deep-dive tool.
- **Filters**: Use the sidebar to narrow down by Store, Time of Day, or Day Type.
- **Table**: The results table shows the Antecedent (Trigger) and Consequent (Recommendation).
- **Metrics**: Pay attention to **Lift** (strength) and **Profit Score** (value).

### Bundles Page
This page provides ready-to-go recommendations.
- **Cards**: Each card represents a bundle opportunity.
- **Narrative**: Read the plain-English explanation to understand *why* this bundle works.
- **Tags**: Look for "High Uplift" tags for the most impactful opportunities.

### What-If Simulator
Planning a promotion? Test it here first.
1. **Trigger**: What customers are already buying (e.g., Burgers).
2. **Promoted**: What you want to sell more of (e.g., Buns).
3. **Discount**: How much are you cutting the price?
4. **Result**: The tool predicts if the volume increase justifies the margin cut.

## Exporting Data
You can export any data grid to CSV by hovering over the top-right corner of the table and clicking the **Download** icon.

## Troubleshooting
- **Import Errors**: Ensure your CSV matches the format in `DATA_FORMAT.md`.
- **No Rules Found**: Try lowering the "Min Support" or "Min Confidence" sliders.
- **App Won't Start**: Check if port 8000 or 8501 is in use.
