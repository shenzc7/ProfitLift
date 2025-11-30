# ProfitLift Demo Script (1-minute walkthrough)

## Step 1: Launch Application
1. Double-click `ProfitLift.exe`.
2. Wait for the splash screen and welcome dashboard.

## Step 2: Upload Sample Data
1. Click **Upload New Data** on the home screen.
2. Drag and drop `sample_1k.csv`.
3. Click **Start Import**.
4. Watch the balloons animation upon success!

## Step 3: View Rules
1. Navigate to **Rules** via the sidebar.
2. Adjust **Min Confidence** to 0.4.
3. Select **Time of Day: Morning**.
4. Observe how the rules change to show breakfast items.

## Step 4: View Bundles
1. Go to **Bundles** page.
2. Point out the "High Margin" tags on the cards.
3. Explain the "Expected Margin" metric to the stakeholder.

## Step 5: Run What-If
1. Go to **What-If** page.
2. Enter Trigger: `milk`.
3. Enter Promoted: `cookies`.
4. Set Discount: `10%`.
5. Click **Run Simulation**.
6. Show the **Incremental Margin** projection.

## Step 6: Export Results
*(Note: Export functionality is part of the native Streamlit dataframe toolbar)*
1. Go back to **Rules**.
2. Hover over the table and click the download icon (CSV) to save the report.
