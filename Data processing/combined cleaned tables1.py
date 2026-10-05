# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///

# Import Pandas for working with our datasets
import pandas as pd
import numpy as np

# Load the cleaned Orders table
orders = pd.read_csv("/Volumes/casestudy4/orders/cleaned_csv_files/cleaned_orders.csv")

# Load the cleaned Products table
products = pd.read_csv("/Volumes/casestudy4/products/cleaned_csv_files/cleaned_products.csv")

# Load the cleaned Customers table
customers = pd.read_csv("/Volumes/casestudy4/customers/cleaned_csv_files/cleaned_customers.csv")

# Load the cleaned Payments table
payments = pd.read_csv("/Volumes/casestudy4/payments/cleaned_csv_files/cleaned_payments.csv")

# Check the number of rows and columns in each cleaned table
print("Orders:", orders.shape)
print("Products:", products.shape)
print("Customers:", customers.shape)
print("Payments:", payments.shape)

# COMMAND ----------

# Check for exact duplicate rows in the Orders table
# This confirms that the cleaned Orders data has no duplicate records
orders.duplicated().sum()

# COMMAND ----------

# Remove exact duplicate rows from the Orders table
# This prevents duplicate records from affecting our analysis and joins
orders = orders.drop_duplicates().copy()

# Check the Orders shape after removing duplicates
orders.shape

# COMMAND ----------

# Check for any remaining missing values in the Orders table
# This confirms that our previous cleaning has carried over correctly
orders.isnull().sum()

# COMMAND ----------

# Remove rows with missing OrderDate
# OrderDate is needed for monthly and yearly trend analysis
orders = orders.dropna(subset=["OrderDate"]).copy()

# Remove rows with missing Quantity
# Quantity is required to calculate revenue
orders = orders.dropna(subset=["Quantity"]).copy()

# Fill missing Discount values with 0
# We are treating missing discounts as no discount
orders["Discount"] = orders["Discount"].fillna(0)

# Fill missing PaymentMethod values with "Unknown"
# We keep these orders instead of guessing the payment method
orders["PaymentMethod"] = orders["PaymentMethod"].fillna("Unknown")

# Remove invalid quantities of 0 or below
# Valid order quantities should be greater than 0
orders = orders[orders["Quantity"] > 0].copy()

# Convert OrderDate to a proper datetime format
# This will be needed later for Year and Month analysis
orders["OrderDate"] = pd.to_datetime(
    orders["OrderDate"],
    errors="coerce"
)

# Check that the Orders table is now clean
print("Orders shape:", orders.shape)
print("\nMissing values:")
print(orders.isnull().sum())

# COMMAND ----------

# MAGIC %md
# MAGIC joining the products and orders table

# COMMAND ----------

# Joining the Orders table to the Products table using ProductID
orders_products = orders.merge(
    products,
    on="ProductID",
    how="left"
)

# Check the shape after the join
# We want to compare this with the 49,860 Orders rows
print("Orders before join:", orders.shape)
print("Orders + Products after join:", orders_products.shape)

# COMMAND ----------

# Check whether any orders failed to match with a product
orders_products[["ProductName", "Category", "UnitPrice"]].isnull().sum()

# COMMAND ----------

# Join the Customers table to the Orders + Products table
# CustomerID is the common field connecting Orders and Customers
# This adds customer information such as Age, City, SignupDate,
# and CustomerSegment to each order

orders_products_customers = orders_products.merge(
    customers,
    on="CustomerID",
    how="left"
)

# Check the row count before and after the join
# The row count should still make sense after adding customer information

print("Before Customers join:", orders_products.shape)
print("After Customers join:", orders_products_customers.shape)

# COMMAND ----------

# Check whether any orders failed to match with a customer
# Missing customer information would indicate a broken CustomerID link

orders_products_customers[
    ["Age", "City", "SignupDate", "CustomerSegment"]
].isnull().sum()

# COMMAND ----------

# Check which CustomerIDs in Orders do not exist in the Customers table
# This specifically tests for broken links between Orders and Customers

broken_customer_links = orders_products[
    ~orders_products["CustomerID"].isin(customers["CustomerID"])
]

# Count the number of order rows with an unmatched CustomerID
print("Broken CustomerID links:", len(broken_customer_links))

# COMMAND ----------

# Display the order records with CustomerIDs
# that do not exist in the Customers table

broken_customer_links[
    ["OrderID", "CustomerID", "OrderDate", "ProductID"]
].head(30)

# COMMAND ----------

# Handle orders with CustomerIDs that do not exist in the Customers table
# We keep these orders because they still contain useful sales information
# Their customer details are labelled as "Unknown"

orders_products_customers["City"] = (
    orders_products_customers["City"].fillna("Unknown")
)

orders_products_customers["CustomerSegment"] = (
    orders_products_customers["CustomerSegment"].fillna("Unknown")
)

# Check the customer-related missing values again
orders_products_customers[
    ["Age", "City", "SignupDate", "CustomerSegment"]
].isnull().sum()

# COMMAND ----------

# Fill missing Age values with the median age
# We previously chose median because it is a sensible value
# for replacing missing numerical age values

customers["Age"] = customers["Age"].fillna(customers["Age"].median())

# Update missing Age values in the joined dataset
# This fills ages for customers that exist in the Customers table
# but keeps the unmatched CustomerID 999999 without a made-up age

age_lookup = customers.set_index("CustomerID")["Age"]

orders_products_customers["Age"] = (
    orders_products_customers["CustomerID"].map(age_lookup)
)

# Check the customer-related missing values again
orders_products_customers[
    ["Age", "City", "SignupDate", "CustomerSegment"]
].isnull().sum()

# COMMAND ----------

# Check how many Payment OrderIDs do not exist in the Orders table
# This helps us identify broken links before joining Payments

broken_payment_links = payments[
    ~payments["OrderID"].isin(orders["OrderID"])
]

# Count the broken OrderID links
print("Broken Payment OrderID links:", len(broken_payment_links))

# COMMAND ----------

# Display the payment records whose OrderID
# does not exist in the cleaned Orders table
# This allows us to inspect the broken links before deciding how to handle them

broken_payment_links[
    ["PaymentID", "OrderID", "PaymentDate", "PaymentStatus"]
].head(20)

# COMMAND ----------

# Check how many unique OrderIDs are affected by the broken payment links
# This tells us whether the 105 payment records represent 105 different orders

print(
    "Broken payment records:",
    len(broken_payment_links)
)

print(
    "Unique broken OrderIDs:",
    broken_payment_links["OrderID"].nunique()
)

# COMMAND ----------

# Check which cleaned Orders do not have a matching payment record
# This checks the relationship from Orders to Payments before the final join

orders_without_payment = orders_products_customers[
    ~orders_products_customers["OrderID"].isin(payments["OrderID"])
]

# Count orders without a matching payment record
print("Orders without matching payment:", len(orders_without_payment))

# COMMAND ----------

# Join the Payments table to the Orders + Products + Customers dataset
# OrderID is the common field connecting Orders and Payments
# This adds PaymentDate and PaymentStatus to our main dataset

final_data = orders_products_customers.merge(
    payments,
    on="OrderID",
    how="left"
)

# Check the row count before and after the Payments join
# The row count should remain 49,860 because every cleaned order
# has one matching payment record

print("Before Payments join:", orders_products_customers.shape)
print("After Payments join:", final_data.shape)

# COMMAND ----------

# Check for missing values in the payment fields after the join
# This confirms that every cleaned order received its payment information

final_data[
    ["PaymentID", "PaymentDate", "PaymentStatus"]
].isnull().sum()

# COMMAND ----------

# Calculate revenue for each order
# Revenue = Quantity × UnitPrice × (1 - Discount)
# The discount is deducted from the original selling price

final_data["Revenue"] = (
    final_data["Quantity"]
    * final_data["UnitPrice"]
    * (1 - final_data["Discount"])
)

# Display the first few rows to check the Revenue calculation
final_data[
    ["Quantity", "UnitPrice", "Discount", "Revenue"]
].head()

# COMMAND ----------

# Make sure OrderDate is stored as a proper datetime
# This allows us to extract Year and Month correctly
final_data["OrderDate"] = pd.to_datetime(
    final_data["OrderDate"],
    errors="coerce"
)

# Create Year from OrderDate
# This will help us analyse yearly sales performance
final_data["Year"] = final_data["OrderDate"].dt.year

# Create Month from OrderDate
# This gives us the month name for monthly analysis
final_data["Month"] = final_data["OrderDate"].dt.month_name()

# Display a few rows to check the new columns
final_data[
    ["OrderDate", "Year", "Month"]
].head()

# COMMAND ----------

# MAGIC %md
# MAGIC inspecting the actual combination of orders status and payment status

# COMMAND ----------

# Check how Order Status and Payment Status relate to each other
# This will help us decide which orders should count as actual revenue

status_check = pd.crosstab(
    final_data["Status"],
    final_data["PaymentStatus"]
)

# Display the results
status_check

# COMMAND ----------

# Create ActualRevenue based on completed and successfully paid orders
# Only orders that are both Completed and Paid count as actual revenue
# Cancelled, Returned, Failed, and Refunded transactions contribute 0

final_data["ActualRevenue"] = np.where(
    (final_data["Status"] == "Completed") &
    (final_data["PaymentStatus"] == "Paid"),
    final_data["Revenue"],
    0
)

# Check the Revenue and ActualRevenue columns
final_data[
    ["Status", "PaymentStatus", "Revenue", "ActualRevenue"]
].head(10)

# COMMAND ----------

# Check the final size of our analysis dataset
print("Final dataset shape:", final_data.shape)

# Check the total calculated order value
print("Total Revenue:", final_data["Revenue"].sum())

# Check the actual recognised revenue
# Only Completed + Paid transactions contribute to this amount
print("Actual Revenue:", final_data["ActualRevenue"].sum())

# Check that our newly created analysis columns have no unexpected missing values
print("\nMissing values in analysis columns:")
print(
    final_data[
        ["Revenue", "ActualRevenue", "Year", "Month"]
    ].isnull().sum()
)

# COMMAND ----------

# Calculate total actual revenue
# We use ActualRevenue because only Completed + Paid orders count as revenue
total_revenue = final_data["ActualRevenue"].sum()

# Count the number of unique completed and paid orders
# We use unique OrderID so that each order is counted only once
successful_orders = final_data[
    (final_data["Status"] == "Completed") &
    (final_data["PaymentStatus"] == "Paid")
]

number_of_orders = successful_orders["OrderID"].nunique()

# Calculate Average Order Value (AOV)
# AOV = Total Revenue divided by the number of successful orders
average_order_value = total_revenue / number_of_orders

# Display the three main KPIs
print("Total Revenue:", round(total_revenue, 2))
print("Number of Orders:", number_of_orders)
print("Average Order Value:", round(average_order_value, 2))

# COMMAND ----------

# Create a Year-Month column from OrderDate
# This keeps each month in the correct year for trend analysis
final_data["YearMonth"] = final_data["OrderDate"].dt.to_period("M")

# Calculate Actual Revenue for each month
# Only Completed + Paid transactions contribute to ActualRevenue
monthly_revenue = (
    final_data.groupby("YearMonth")["ActualRevenue"]
    .sum()
    .reset_index()
)

# Display the monthly revenue trend
monthly_revenue

# COMMAND ----------

# Find the month with the highest Actual Revenue
# idxmax() identifies the row containing the maximum revenue value
best_month = monthly_revenue.loc[
    monthly_revenue["ActualRevenue"].idxmax()
]

# Find the month with the lowest Actual Revenue
# idxmin() identifies the row containing the minimum revenue value
worst_month = monthly_revenue.loc[
    monthly_revenue["ActualRevenue"].idxmin()
]

# Display the results
print("Best Month:")
print(best_month)

print("\nWorst Month:")
print(worst_month)

# COMMAND ----------

# Calculate Actual Revenue by product
# This helps us identify the highest and lowest revenue-generating products

product_revenue = (
    final_data.groupby("ProductName")["ActualRevenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Display all products from highest to lowest revenue
product_revenue

# COMMAND ----------

# Filter the dataset to successful sales only
# This keeps only Completed + Paid transactions
successful_sales = final_data[
    (final_data["Status"] == "Completed") &
    (final_data["PaymentStatus"] == "Paid")
].copy()

# Calculate the total number of units sold for each product
product_units = (
    successful_sales.groupby("ProductName")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Display products from highest to lowest units sold
product_units

# COMMAND ----------

# Calculate Actual Revenue by product category
# This shows which categories generate the most revenue

category_revenue = (
    final_data.groupby("Category")["ActualRevenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Display categories from highest to lowest revenue
category_revenue

# COMMAND ----------

# Calculate total units sold by category
# We use successful_sales so only Completed + Paid sales are included

category_units = (
    successful_sales.groupby("Category")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Display categories from highest to lowest units sold
category_units

# COMMAND ----------

# Calculate Actual Revenue by customer city
# This helps us identify which cities bring the most value to the shop

city_revenue = (
    final_data.groupby("City")["ActualRevenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Display cities from highest to lowest Actual Revenue
city_revenue

# COMMAND ----------

# Standardize inconsistent city names
# "tehran" is corrected to "Tehran"
# "Mashad" is corrected to "Mashhad"

final_data["City"] = final_data["City"].replace({
    "tehran": "Tehran",
    "Mashad": "Mashhad"
})

# Recalculate Actual Revenue by city after cleaning the city names
city_revenue = (
    final_data.groupby("City")["ActualRevenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Display the corrected city revenue results
city_revenue

# COMMAND ----------

# Calculate Actual Revenue by customer segment
# This helps identify which customer segment brings the most value

segment_revenue = (
    final_data.groupby("CustomerSegment")["ActualRevenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

# Display customer segments from highest to lowest Actual Revenue
segment_revenue

# COMMAND ----------

# Count the number of unique orders for each order status
# Using nunique() ensures each OrderID is counted only once

order_status = (
    final_data.groupby("Status")["OrderID"]
    .nunique()
    .reset_index(name="NumberOfOrders")
)

# Calculate the total number of unique orders
total_orders = final_data["OrderID"].nunique()

# Calculate the percentage share of each order status
order_status["Percentage"] = (
    order_status["NumberOfOrders"] / total_orders * 100
).round(2)

# Display the results
order_status

# COMMAND ----------

# Count payments by payment status
# This shows how many payments were Paid, Failed, or Refunded

payment_status = (
    payments.groupby("PaymentStatus")["PaymentID"]
    .count()
    .to_frame("NumberOfPayments")
    .reset_index()
)

# Calculate the total number of payment attempts
total_payments = payment_status["NumberOfPayments"].sum()

# Calculate the percentage share of each payment status
payment_status["Percentage"] = (
    payment_status["NumberOfPayments"]
    / total_payments
    * 100
).round(2)

# Display the payment status results
payment_status

# COMMAND ----------

# Create a summary of payment methods
# Count the total number of payment attempts for each method
# Count how many of those attempts failed

payment_method_failure = (
    final_data.groupby("PaymentMethod")
    .agg(
        TotalPayments=("PaymentStatus", "count"),
        FailedPayments=("PaymentStatus", lambda x: (x == "Failed").sum())
    )
    .reset_index()
)

# Calculate the failure rate for each payment method
# Failure Rate = Failed Payments / Total Payments × 100
payment_method_failure["FailureRate"] = (
    payment_method_failure["FailedPayments"]
    / payment_method_failure["TotalPayments"]
    * 100
).round(2)

# Sort from the highest failure rate to the lowest
payment_method_failure = payment_method_failure.sort_values(
    "FailureRate",
    ascending=False
)

# Display the results
payment_method_failure

# COMMAND ----------

# Analyse successful sales by discount level
# We use successful_sales so only Completed + Paid orders are included

discount_analysis = (
    successful_sales.groupby("Discount")
    .agg(
        NumberOfOrders=("OrderID", "nunique"),
        AverageQuantity=("Quantity", "mean"),
        AverageRevenue=("ActualRevenue", "mean"),
        TotalRevenue=("ActualRevenue", "sum")
    )
    .reset_index()
)

# Round the values to make the results easier to read
discount_analysis["AverageQuantity"] = (
    discount_analysis["AverageQuantity"].round(2)
)

discount_analysis["AverageRevenue"] = (
    discount_analysis["AverageRevenue"].round(2)
)

discount_analysis["TotalRevenue"] = (
    discount_analysis["TotalRevenue"].round(2)
)

# Display the results
discount_analysis

# COMMAND ----------

# Exporting the final cleaned dataset to a CSV file

final_data.to_csv(
    "/Volumes/casestudy4/orders/cleaned_csv_files/final_shop_analysis.csv",
    index=False
)
display (final_data)

# COMMAND ----------

# Import Pandas and NumPy
import pandas as pd
import numpy as np

# Load the cleaned CSV files from the Databricks volume into Pandas DataFrames
orders = pd.read_csv("/Volumes/casestudy4/orders/cleaned_csv_files/cleaned_orders.csv")
products = pd.read_csv("/Volumes/casestudy4/products/cleaned_csv_files/cleaned_products.csv")
customers = pd.read_csv("/Volumes/casestudy4/customers/cleaned_csv_files/cleaned_customers.csv")
payments = pd.read_csv("/Volumes/casestudy4/payments/cleaned_csv_files/cleaned_payments.csv")

# Check that all four tables loaded successfully
print("Orders:", orders.shape)
print("Products:", products.shape)
print("Customers:", customers.shape)
print("Payments:", payments.shape)



# COMMAND ----------

# STEP 1: Join Orders with Products using ProductID
# This adds ProductName, Category and UnitPrice to the Orders data
final_data = orders.merge(
    products,
    on="ProductID",
    how="left"
)

# STEP 2: Join with Customers using CustomerID
# This adds customer information such as Age, City and CustomerSegment
final_data = final_data.merge(
    customers,
    on="CustomerID",
    how="left"
)

# STEP 3: Join with Payments using OrderID

final_data = final_data.merge(
    payments,
    on="OrderID",
    how="left"
)

# Check the size of the final combined dataset
print("Final dataset shape:", final_data.shape)

# Display the first rows of the final combined dataset
display(final_data.head())

# COMMAND ----------

# Check the number of rows and columns in the full combined dataset
print("Final dataset shape:", final_data.shape)

# COMMAND ----------

# Check the current Orders dataset before fixing the final table

print("Orders shape:", orders.shape)

# Check exact duplicate rows
print("Exact duplicate rows:", orders.duplicated().sum())

# Check missing values in each Orders column
print("\nMissing values:")
print(orders.isnull().sum())

# Check invalid Quantity values
print(
    "\nQuantity values of 0 or below:",
    (orders["Quantity"] <= 0).sum()
)

# COMMAND ----------

# CLEAN THE ORDERS DATASET

# 1. Remove exact duplicate rows
orders = orders.drop_duplicates().copy()

# 2. Remove rows where OrderDate is missing

orders = orders.dropna(subset=["OrderDate"]).copy()

# 3. Remove rows where Quantity is missing

orders = orders.dropna(subset=["Quantity"]).copy()

# 4. Fill missing Discount values with 0

orders["Discount"] = orders["Discount"].fillna(0)

# 5. Fill missing PaymentMethod values with "Unknown"

orders["PaymentMethod"] = orders["PaymentMethod"].fillna("Unknown")

# 6. Remove invalid quantities of 0 or below

orders = orders[orders["Quantity"] > 0].copy()

# 7. Convert OrderDate to a proper datetime format
orders["OrderDate"] = pd.to_datetime(
    orders["OrderDate"],
    errors="coerce"
)

# 8. Check the cleaned Orders dataset
print("Cleaned Orders shape:", orders.shape)

print("\nMissing values:")
print(orders.isnull().sum())

print("\nExact duplicates:", orders.duplicated().sum())

print(
    "Invalid quantities:",
    (orders["Quantity"] <= 0).sum()
)

# COMMAND ----------

# JOIN ALL FOUR CLEANED TABLES

# Join Orders with Products
final_data = orders.merge(
    products,
    on="ProductID",
    how="left"
)

# Join Customers
final_data = final_data.merge(
    customers,
    on="CustomerID",
    how="left"
)

# Join Payments
final_data = final_data.merge(
    payments,
    on="OrderID",
    how="left"
)

# Check the size of the combined dataset
print("Final dataset shape:", final_data.shape)

# COMMAND ----------

# CREATE REVENUE COLUMNS

# 1. Calculate Revenue for each order
# Revenue = Quantity × UnitPrice × (1 - Discount)
final_data["Revenue"] = (
    final_data["Quantity"]
    * final_data["UnitPrice"]
    * (1 - final_data["Discount"])
)

# 2. Calculate Actual Revenue
# Only orders that are both Completed and Paid count as actual revenue
# Cancelled, Returned, Failed and Refunded transactions count as 0
final_data["ActualRevenue"] = np.where(
    (final_data["Status"] == "Completed") &
    (final_data["PaymentStatus"] == "Paid"),
    final_data["Revenue"],
    0
)

# 3. Check the size of the dataset after adding the two new columns
print("Final dataset shape:", final_data.shape)

# 4. Check the revenue totals
print("Total Revenue:", round(final_data["Revenue"].sum(), 2))
print("Total Actual Revenue:", round(final_data["ActualRevenue"].sum(), 2))

# 5. Display a sample to check the calculations
display(
    final_data[
        [
            "OrderID",
            "Quantity",
            "UnitPrice",
            "Discount",
            "Status",
            "PaymentStatus",
            "Revenue",
            "ActualRevenue"
        ]
    ].head(10)
)

# COMMAND ----------

# CREATE DATE FIELDS FOR DASHBOARD ANALYSIS

# making sure OrderDate is stored as a proper datetime
final_data["OrderDate"] = pd.to_datetime(
    final_data["OrderDate"],
    errors="coerce"
)

# Create Year from OrderDate
final_data["Year"] = final_data["OrderDate"].dt.year

# Create Month name from OrderDate
final_data["Month"] = final_data["OrderDate"].dt.month_name()

# Create Year-Month for the monthly revenue trend
final_data["YearMonth"] = final_data["OrderDate"].dt.strftime("%Y-%m")

# Check the final dataset
print("Final dataset shape:", final_data.shape)

# Display the new date fields
display(
    final_data[
        ["OrderDate", "Year", "Month", "YearMonth"]
    ].head(10)
)

# COMMAND ----------

# SAVE THE FINAL ANALYSIS DATASET

# Save the completed dataset as a CSV file in the Databricks Volume
# This version includes the joined tables, Revenue, ActualRevenue,
# Year, Month and YearMonth

final_data.to_csv(
    "/Volumes/casestudy4/orders/cleaned_csv_files/final_shop_analysis.csv",
    index=False
)

# Confirming that the file was saved
print("Final dataset saved successfully.")

# Confirming the final size
print("Final dataset shape:", final_data.shape)

# COMMAND ----------

# LOAD AND DISPLAY THE SAVED FINAL CSV

# Load the final saved CSV back into Pandas
final_csv = pd.read_csv(
    "/Volumes/casestudy4/orders/cleaned_csv_files/final_shop_analysis.csv"
)

# Display the complete dataset in Databricks
display(final_csv)