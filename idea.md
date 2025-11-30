ProfitLift
Business Requirements Document (BRD)

Prepared by: Shenz
Purpose: A clear, non-technical agreement on what will be built, how it helps day-to-day, and how we
will confirm success.

A. Executive Summary
ProfitLift is a Windows desktop app that helps your team spot the best add-on items and promotions
for each store, season, and time window. It focuses on actions that raise incremental revenue without
pushing low-margin discounts.

B. Business Goals
Raise average basket value with smart, context-aware add-ons.
Improve attach rate where it matters, not just popular items everywhere.
Cut promotion waste by focusing on actions likely to create real lift.
Give the team a weekly, easy-to-read opportunity list they can act on.
C. Scope
In-Scope (Pilot)
Windows app with dashboard pages: Rules, Recommended Bundles, What-If Simulator,
Explanations.
Load data from simple CSV files exported from your systems.
Export opportunity lists to CSV or PDF.
Evaluation report with plain-English findings and next steps.
Out-of-Scope (Pilot)
Direct integration to live POS systems.
Customer PII handling. Loyalty IDs, if used, should be hashed.
Operation playbooks or call-center scripts (can be added after pilot).
D. Who Will Use It and Day-to-Day Flow
Primary Users
Category or Merchandising Manager: reviews weekly opportunities and decides actions.
Trade or Promotions Lead: plans promos using the what-if view.
Store or Regional Lead: checks local suggestions and shares feedback.
Day-to-Day
Monday: open dashboard, filter to target categories, download quick list of top bundles.
Mid-week: try what-if for an upcoming promo; check projected effect.
Friday: confirm actions for next week; export evidence pack if needed.
E. Data We Need (Simple Terms)
Transactions with date and time: lets us compare weekday vs weekend, morning vs evening.
Items in each basket: to learn natural combinations.
Price paid and any discount flag: to estimate real value and avoid wasteful actions.
Store or region: to respect local differences.
Optional margin or cost per item: helps rank by profit, not just popularity.
Privacy Note: we do not need names, phone numbers, or emails. Customer IDs are optional and should be hashed.
F. What the App Shows
Recommended Bundles: items that make sense together for the selected store or time window.
Why It Makes Sense: a one-line explanation in plain English next to each suggestion.
What-If View: try a planned promo window and see projected movement.
Downloadable Lists: export the top actions to share with teams.
G. How We Measure Success
Attach Rate Uplift: did more baskets include the suggested add-on.
Incremental Margin per Basket: did profit go up, not just sales.
Time to Insight: hours from data drop to a clean shortlist.
Team Adoption: did managers actually use the lists in weekly trade meetings.
H. Project Plan and Milestones
Week Milestone
1 Data drop and validation; first look at opportunities.
2 Dashboard walkthrough with your categories.
3 What-if planning and projected effects for chosen promos.
4 Final readout: top actions, projected impact, next steps.
Communication: weekly 30-minute check-in; shared notes and action list after each call.

I. Risks, Assumptions, Responsibilities
Key Risks and Safeguards
Sparse data in some stores: we widen the context so suggestions remain reliable.
Promo timing mismatches: we compare like periods to avoid misleading results.
Low-margin push: ranking respects profit so we do not over-promote weak items.
Assumptions
Pilot runs on exported historical data; no live system connection is required.
If margin or cost is missing, we can start with category-level averages.
Responsibilities
Client: provide the CSV exports and confirm 2 to 3 success metrics.
Shenz (developer): deliver the app, dashboards, weekly updates, and the final report.
Sign-Off
The pilot is complete when the app runs on a Windows laptop, the report shows movement on the
agreed KPIs, and the opportunity list is ready for action.