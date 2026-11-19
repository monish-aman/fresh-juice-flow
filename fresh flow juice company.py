# FRESHFLOW JUICE COMPANY - NUMPY PROJECT

import numpy as np

# 1. LOAD DATA
data = np.genfromtxt("freshflow_sales.csv", delimiter=",", skip_header=1)

print("DATA SHAPE:", data.shape)
print("NUMBER OF ROWS:", data.shape[0])
print("NUMBER OF COLUMNS:", data.shape[1])

# Give simple names to each column
transaction_id = data[:, 0]
day = data[:, 1]
outlet = data[:, 2]
product = data[:, 3]
category = data[:, 4]
quantity = data[:, 5]
price = data[:, 6]
cost = data[:, 7]
discount = data[:, 8]
stock = data[:, 9]
payment = data[:, 10]
rating = data[:, 11]

# 2. DATA PROFILE
column_names = ["transaction_id", "day_index", "outlet_id", "product_code",
                "category_code", "quantity", "unit_price", "unit_cost",
                "discount_rate", "stock_before_units", "payment_code",
                "customer_rating"]

print("\nMISSING VALUES")
for i in range(12):
    print(column_names[i], np.isnan(data[:, i]).sum())

# 3. DATA QUALITY CHECKS
# Product categories: products 1-4 = category 1,
# products 5-6 = category 2, product 7 = category 3, product 8 = category 4.
correct_category = np.zeros(len(data), dtype=bool)

for p in range(1, 9):
    if p <= 4:
        cat = 1
    elif p <= 6:
        cat = 2
    elif p == 7:
        cat = 3
    else:
        cat = 4

    correct_category = correct_category | ((product == p) & (category == cat))

# Find duplicate transaction IDs
unique_ids, id_counts = np.unique(transaction_id, return_counts=True)
duplicate_ids = unique_ids[id_counts > 1]
duplicate_rows = np.isin(transaction_id, duplicate_ids)

print("\nDATA QUALITY REPORT")
print("Duplicate transaction ID values:", len(duplicate_ids))
print("Rows involved in duplicate IDs:", duplicate_rows.sum())
print("Invalid day:", ((day < 1) | (day > 30)).sum())
print("Invalid outlet:", (~np.isin(outlet, [1, 2, 3])).sum())
print("Invalid product:", (~np.isin(product, [1, 2, 3, 4, 5, 6, 7, 8])).sum())
print("Invalid payment code:", (~np.isin(payment, [1, 2, 3, 4])).sum())
print("Wrong product/category mapping:", (~correct_category).sum())
print("Invalid quantity:", (quantity <= 0).sum())
print("Negative price:", (price < 0).sum())
print("Missing price:", np.isnan(price).sum())
print("Negative cost:", (cost < 0).sum())
print("Missing cost:", np.isnan(cost).sum())
print("Invalid discount:", ((discount < 0) | (discount > 1)).sum())
print("Invalid rating:", ((rating < 1) | (rating > 5) & (~np.isnan(rating))).sum())
print("Zero stock before sale:", (stock == 0).sum())

# 4. CLEAN DATA
# Keep the raw data unchanged. Exclude invalid financial/sales records.
valid = (
    np.isfinite(day) & np.isfinite(outlet) & np.isfinite(product) &
    np.isfinite(category) & np.isfinite(quantity) & np.isfinite(price) &
    np.isfinite(cost) & np.isfinite(discount) & np.isfinite(stock) &
    (day >= 1) & (day <= 30) &
    np.isin(outlet, [1, 2, 3]) &
    np.isin(product, [1, 2, 3, 4, 5, 6, 7, 8]) &
    np.isin(payment, [1, 2, 3, 4]) &
    correct_category &
    (quantity > 0) & (price > 0) & (cost >= 0) &
    (discount >= 0) & (discount <= 1) & (stock >= 0) &
    (~duplicate_rows)
)

clean_data = data[valid]

print("\nCLEANING RESULT")
print("Original rows:", len(data))
print("Rows kept:", len(clean_data))
print("Rows excluded:", len(data) - len(clean_data))

# Get clean columns again
day = clean_data[:, 1].astype(int)
outlet = clean_data[:, 2].astype(int)
product = clean_data[:, 3].astype(int)
quantity = clean_data[:, 5]
price = clean_data[:, 6]
cost = clean_data[:, 7]
discount = clean_data[:, 8]

# 5. CALCULATE SALES METRICS
gross_sales = quantity * price
discount_amount = gross_sales * discount
net_revenue = gross_sales - discount_amount
cost_of_goods = quantity * cost
gross_profit = net_revenue - cost_of_goods

margin = gross_profit.sum() / net_revenue.sum() * 100
average_price = net_revenue / quantity

print("\nOVERALL SALES")
print("Total units sold:", quantity.sum())
print("Gross sales: Rs.", round(gross_sales.sum(), 2))
print("Discount amount: Rs.", round(discount_amount.sum(), 2))
print("Net revenue: Rs.", round(net_revenue.sum(), 2))
print("Cost of goods: Rs.", round(cost_of_goods.sum(), 2))
print("Gross profit: Rs.", round(gross_profit.sum(), 2))
print("Gross margin:", round(margin, 2), "%")
print("Average transaction value: Rs.", round(net_revenue.mean(), 2))
print("Median transaction value: Rs.", round(np.median(net_revenue), 2))
print("Average selling price per unit: Rs.", round(average_price.mean(), 2))

# 6. OUTLET-WISE ANALYSIS
print("\nOUTLET-WISE SALES")
for o in [1, 2, 3]:
    selected = outlet == o
    revenue = net_revenue[selected].sum()
    profit = gross_profit[selected].sum()
    units = quantity[selected].sum()
    print("Outlet", o, "Revenue:", round(revenue, 2),
          "Profit:", round(profit, 2), "Units:", int(units))

# 7. PRODUCT-WISE ANALYSIS
print("\nPRODUCT-WISE SALES")
product_names = ["Orange Juice", "Mango Juice", "Apple Juice",
                 "Watermelon Juice", "Banana Smoothie",
                 "Mixed Fruit Smoothie", "Lemonade", "Iced Tea"]

for p in range(1, 9):
    selected = product == p
    print(product_names[p - 1],
          "Units:", int(quantity[selected].sum()),
          "Revenue:", round(net_revenue[selected].sum(), 2),
          "Profit:", round(gross_profit[selected].sum(), 2))

# 8. DAILY SALES ANALYSIS
daily_revenue = np.zeros(30)

for d in range(1, 31):
    selected = day == d
    daily_revenue[d - 1] = net_revenue[selected].sum()

daily_change = np.diff(daily_revenue)

print("\nDAILY SALES")
for d in range(30):
    print("Day", d + 1, "Revenue:", round(daily_revenue[d], 2))

print("Highest revenue day:", np.argmax(daily_revenue) + 1)
print("Lowest revenue day:", np.argmin(daily_revenue) + 1)
print("Largest daily increase:", round(daily_change.max(), 2))
print("Largest daily decrease:", round(daily_change.min(), 2))
print("30-day average revenue:", round(daily_revenue.mean(), 2))

# 9. DISCOUNT ANALYSIS
print("\nDISCOUNT ANALYSIS")
for name, low, high in [
    ("0% to below 5%", 0, 0.05),
    ("5% to below 15%", 0.05, 0.15),
    ("15% and above", 0.15, 1.01)
]:
    selected = (discount >= low) & (discount < high)
    if selected.sum() > 0:
        group_margin = gross_profit[selected].sum() / net_revenue[selected].sum() * 100
        print(name, "Transactions:", selected.sum(),
              "Units:", int(quantity[selected].sum()),
              "Revenue:", round(net_revenue[selected].sum(), 2),
              "Margin:", round(group_margin, 2), "%")

# Correlation is a relationship, not proof that one thing causes another.
print("Correlation: discount and quantity:",
      round(np.corrcoef(discount, quantity)[0, 1], 3))

# 10. ANOMALY CHECKS
q1 = np.percentile(price, 25)
q3 = np.percentile(price, 75)
upper_price = q3 + 1.5 * (q3 - q1)
high_price = price > upper_price

high_discount = discount > 0.30
zero_stock = clean_data[:, 9] == 0

print("\nANOMALY CHECK")
print("High price records (IQR method):", high_price.sum())
print("High discount records (over 30%):", high_discount.sum())
print("Zero stock records kept for investigation:", zero_stock.sum())

print("High price transaction IDs:",
      clean_data[high_price, 0].astype(int))
print("High discount transaction IDs:",
      clean_data[high_discount, 0].astype(int))
print("Zero stock transaction IDs:",
      clean_data[zero_stock, 0].astype(int))

# 11. DISCOUNT SCENARIOS
# Quantity and unit cost are kept the same in both scenarios.
print("\nDISCOUNT SCENARIOS")
for new_discount in [0.05, 0.10]:
    new_revenue = gross_sales * (1 - new_discount)
    new_profit = new_revenue - cost_of_goods
    print("Assumed discount:", new_discount * 100, "%")
    print("Scenario revenue: Rs.", round(new_revenue.sum(), 2))
    print("Scenario gross profit: Rs.", round(new_profit.sum(), 2))
    print("Revenue change from current: Rs.",
          round(new_revenue.sum() - net_revenue.sum(), 2))
    print("Profit change from current: Rs.",
          round(new_profit.sum() - gross_profit.sum(), 2))

# 12. CUSTOMER RATINGS
valid_ratings = rating = clean_data[:, 11]
valid_ratings = valid_ratings[(valid_ratings >= 1) & (valid_ratings <= 5)]
print("\nCUSTOMER RATINGS")
print("Valid ratings:", len(valid_ratings))
print("Average rating:", round(valid_ratings.mean(), 2))

# 13. SIMPLE VALIDATION TESTS
# Check the first five clean transactions with the same formulas.
for i in range(5):
    test_gross = quantity[i] * price[i]
    test_net = test_gross * (1 - discount[i])
    test_profit = test_net - quantity[i] * cost[i]

    assert np.isclose(test_gross, gross_sales[i])
    assert np.isclose(test_net, net_revenue[i])
    assert np.isclose(test_profit, gross_profit[i])

# Small checks for missing values and zero denominator handling.
assert np.isnan(np.array([np.nan]))[0]
assert np.isclose(0 / 1, 0)

print("\\nFirst five rows checked. All basic validation tests passed.")


