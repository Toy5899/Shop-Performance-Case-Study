## Shop Performance Analysis

## Project Overview

This project analyses the performance of an online shop from January 2024 to June 2026.

The purpose of the analysis was to understand sales performance, customer behaviour, product performance, payment performance and the effect of discounts.

The project involved cleaning and combining four datasets, analysing the data using Python and Pandas, and creating an interactive dashboard in Looker Studio.

---

## Tools Used

- Python
- Pandas
- Databricks
- Looker Studio
- GitHub

---

## Datasets

The analysis used four datasets:

- Customers
- Orders
- Products
- Payments

The datasets were joined using:

- CustomerID
- ProductID
- OrderID

After cleaning and joining the datasets, the final analysis dataset contained 49,860 rows.

---

## Data Cleaning

The following data-cleaning steps were performed:

- Removed 120 duplicate order records.
- Removed records with missing OrderDate and Quantity.
- Removed 25 records with invalid quantities of zero or below.
- Filled missing Discount values with 0.
- Replaced missing PaymentMethod values with "Unknown".
- Filled missing customer Age values using the median age of 41.
- Standardised inconsistent city names.
- Removed payment records with missing PaymentDate.
- Checked relationships between Orders, Customers, Products and Payments.
- Retained unmatched information where appropriate and labelled missing categorical information as "Unknown".

---

## Data Preparation

The four datasets were combined to create one dataset for analysis.

Revenue was calculated as:

Revenue = Quantity × UnitPrice × (1 - Discount)

Actual Revenue was also created.

Only orders with:

- Status = Completed
- PaymentStatus = Paid

were counted as Actual Revenue.

Cancelled, Returned, Failed and Refunded transactions were excluded from Actual Revenue.

Year, Month and YearMonth fields were also created from OrderDate to support trend analysis.

---

## Key Performance Indicators

The main KPIs were:

- Total Actual Revenue: 2,990,114.95
- Completed & Paid Orders: 42,721
- Average Order Value: 69.99

---

## Key Findings

### Revenue Performance

Revenue remained relatively stable throughout 2024 and 2025.

March 2024 recorded the highest monthly actual revenue at 114,176.80.

Revenue declined during the first half of 2026, with February 2026 recording the lowest monthly actual revenue at 64,512.90.

### Product Performance

The top revenue-generating products were:

1. Headphones – 292,207.50
2. Office Chair – 288,261.00
3. Tablet – 243,789.00

Notebook recorded the highest sales volume with 8,858 units sold.

### Category Performance

Electronics generated the highest actual revenue at 1,511,908.80.

Accessories recorded the highest sales volume with 30,013 units sold.

This shows that the categories selling the most units are not necessarily the categories generating the most revenue.

### Customer Performance

Tehran generated the highest actual revenue at 822,877.65.

Regular customers were the highest-value customer segment, generating 1,659,781.55 in actual revenue.

### Operational Performance

91.99% of orders were completed successfully.

Cancelled orders accounted for 4.94% of orders, while returned orders accounted for 3.07%.

Together, cancelled and returned orders represented 8.01% of orders.

Failed payments accounted for 3.85% of payment attempts.

Among known payment methods, CardToCard had the highest failure rate at approximately 3.90%, while Cash had the lowest at approximately 3.65%.

### Discount Analysis

Higher discounts did not significantly increase the average number of units purchased.

Average revenue decreased as discount levels increased.

This suggests that larger discounts reduced revenue without meaningfully increasing order size.

---

## Dashboard

An interactive Looker Studio dashboard was created to present the results.

The dashboard includes:

- Total Actual Revenue
- Completed & Paid Orders
- Average Order Value
- Monthly Actual Revenue Trend
- Actual Revenue by Product
- Units Sold by Product
- Actual Revenue by Category
- Units Sold by Category
- Actual Revenue by City
- Actual Revenue by Customer Segment
- Order Status Distribution
- Payment Failure Rate by Payment Method
- Average Revenue by Discount Level
- Performance Summary
- Data Cleaning Decisions
- Business Recommendations

---

## Business Recommendations

### 1. Prioritise High-Value Products

Focus on strong revenue-generating products such as Headphones, Office Chairs and Tablets. Electronics should remain a key focus, while high-volume Accessories can support cross-selling opportunities.

### 2. Review the Discount Strategy

Higher discounts did not significantly increase the number of units purchased, while average revenue decreased as discounts increased. The business should consider more targeted promotions rather than relying on large discounts.

### 3. Investigate the 2026 Revenue Decline

Investigate the decline in revenue during the first half of 2026. Product, customer and operational performance during this period should be reviewed, while cancellations, returns and failed payments should also be monitored.

---

## Conclusion

The analysis shows that the online shop generated approximately 2.99 million in actual revenue from 42,721 completed and paid orders.

Electronics was the strongest revenue-generating category, while Accessories led in units sold. Regular customers and Tehran contributed the most value.

The analysis also identified opportunities to improve the discount strategy, reduce operational losses and investigate the revenue decline observed during the first half of 2026.hop-Performance-Case-Study
