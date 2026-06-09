import pandas as pd



# LOAD DATA


df = pd.read_csv("data/WA_Fn-UseC_-Accounts-Receivable.csv")


# DATA OVERVIEW


print("\nDataset Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# EXECUTIVE KPIs


total_invoice_value = df["InvoiceAmount"].sum()

avg_days_to_settle = df["DaysToSettle"].mean()

late_invoices = (df["DaysLate"] > 0).sum()

late_payment_rate = (late_invoices / len(df)) * 100

total_customers = df["customerID"].nunique()

print("\n===== EXECUTIVE KPI DASHBOARD =====")

print(f"Total Invoice Value: ${total_invoice_value:,.2f}")
print(f"Average Days To Settle: {avg_days_to_settle:.2f}")
print(f"Late Invoices: {late_invoices}")
print(f"Late Payment Rate: {late_payment_rate:.2f}%")
print(f"Total Customers: {total_customers}")


# CUSTOMER RISK ANALYSIS


customer_risk = df.groupby("customerID").agg(
    TotalInvoiceAmount=("InvoiceAmount", "sum"),
    AvgDaysLate=("DaysLate", "mean"),
    TotalInvoices=("invoiceNumber", "count")
)

customer_risk = customer_risk.sort_values(
    by="AvgDaysLate",
    ascending=False
)

print("\n===== TOP 10 RISKIEST CUSTOMERS =====")
print(customer_risk.head(10))


# CUSTOMER RISK SCORING


def assign_risk(avg_days_late):
    if avg_days_late >= 10:
        return "High"
    elif avg_days_late >= 5:
        return "Medium"
    else:
        return "Low"

customer_risk["RiskLevel"] = customer_risk["AvgDaysLate"].apply(assign_risk)

print("\n===== CUSTOMER RISK SCORES =====")
print(
    customer_risk[
        ["TotalInvoiceAmount", "AvgDaysLate", "RiskLevel"]
    ].head(15)
)


# COLLECTIONS PRIORITY ENGINE


def assign_priority(row):

    if row["TotalInvoiceAmount"] > 1500 and row["AvgDaysLate"] > 10:
        return "Critical"

    elif row["TotalInvoiceAmount"] > 1000 and row["AvgDaysLate"] > 5:
        return "High"

    elif row["AvgDaysLate"] > 2:
        return "Medium"

    else:
        return "Low"


customer_risk["Priority"] = customer_risk.apply(
    assign_priority,
    axis=1
)

print("\n===== COLLECTIONS PRIORITY LIST =====")

print(
    customer_risk[
        [
            "TotalInvoiceAmount",
            "AvgDaysLate",
            "RiskLevel",
            "Priority"
        ]
    ].head(15)
)


# DISPUTE IMPACT ANALYSIS


dispute_analysis = df.groupby("Disputed").agg(
    AvgDaysToSettle=("DaysToSettle", "mean"),
    InvoiceCount=("invoiceNumber", "count"),
    TotalInvoiceValue=("InvoiceAmount", "sum")
)

print("\n===== DISPUTE IMPACT ANALYSIS =====")
print(dispute_analysis)


# COUNTRY PERFORMANCE ANALYSIS


country_analysis = df.groupby("countryCode").agg(
    AvgDaysLate=("DaysLate", "mean"),
    TotalInvoiceValue=("InvoiceAmount", "sum"),
    InvoiceCount=("invoiceNumber", "count")
)

country_analysis = country_analysis.sort_values(
    by="AvgDaysLate",
    ascending=False
)

print("\n===== TOP 10 COUNTRIES BY PAYMENT DELAY =====")
print(country_analysis.head(10))



# ==========================================
# BUSINESS RECOMMENDATION ENGINE


print("\n===== BUSINESS RECOMMENDATIONS =====")

# Recommendation 1

critical_customers = customer_risk[
    customer_risk["Priority"] == "Critical"
]

print(
    f"\n1. Prioritize collections for "
    f"{len(critical_customers)} critical customers."
)

# Recommendation 2

disputed_avg = dispute_analysis.loc["Yes", "AvgDaysToSettle"]
non_disputed_avg = dispute_analysis.loc["No", "AvgDaysToSettle"]

extra_days = disputed_avg - non_disputed_avg

print(
    f"\n2. Reduce invoice disputes. "
    f"Disputed invoices take "
    f"{extra_days:.2f} extra days to settle."
)

# Recommendation 3

highest_delay_country = country_analysis.index[0]

print(
    f"\n3. Review payment performance in country "
    f"{highest_delay_country}, which has the "
    f"highest average payment delay."
)

# Recommendation 4

high_risk_customers = customer_risk[
    customer_risk["RiskLevel"] == "High"
]

print(
    f"\n4. Monitor "
    f"{len(high_risk_customers)} high-risk customers "
    f"to improve cash collection."
)



# CUSTOMER PORTFOLIO ANALYSIS


customer_portfolio = df.groupby("customerID").agg(
    TotalRevenue=("InvoiceAmount", "sum"),
    AvgDaysLate=("DaysLate", "mean"),
    TotalInvoices=("invoiceNumber", "count")
)

customer_portfolio = customer_portfolio.sort_values(
    by="TotalRevenue",
    ascending=False
)

print("\n===== TOP 10 REVENUE GENERATING CUSTOMERS =====")
print(customer_portfolio.head(10))

# HIGH VALUE RISKY CUSTOMERS


high_value_risky = customer_portfolio[
    customer_portfolio["AvgDaysLate"] > 5
]

high_value_risky = high_value_risky.sort_values(
    by="TotalRevenue",
    ascending=False
)

print("\n===== HIGH VALUE RISKY CUSTOMERS =====")
print(high_value_risky.head(10))


# INVOICE AGING ANALYSIS


def aging_bucket(days_late):

    if days_late <= 0:
        return "Current"

    elif days_late <= 30:
        return "1-30 Days"

    elif days_late <= 60:
        return "31-60 Days"

    elif days_late <= 90:
        return "61-90 Days"

    else:
        return "90+ Days"


df["AgingBucket"] = df["DaysLate"].apply(aging_bucket)

aging_analysis = df.groupby("AgingBucket").agg(
    InvoiceCount=("invoiceNumber", "count"),
    TotalInvoiceValue=("InvoiceAmount", "sum")
)

print("\n===== INVOICE AGING ANALYSIS =====")
print(aging_analysis)


# CUSTOMER HEALTH SCORE


customer_health = df.groupby("customerID").agg(
    TotalRevenue=("InvoiceAmount", "sum"),
    AvgDaysLate=("DaysLate", "mean"),
    TotalInvoices=("invoiceNumber", "count")
)

# Revenue Score
customer_health["RevenueScore"] = (
    customer_health["TotalRevenue"]
    / customer_health["TotalRevenue"].max()
) * 40

# Payment Behaviour Score
customer_health["PaymentScore"] = (
    1 - (
        customer_health["AvgDaysLate"]
        / customer_health["AvgDaysLate"].max()
    )
) * 40

# Activity Score
customer_health["ActivityScore"] = (
    customer_health["TotalInvoices"]
    / customer_health["TotalInvoices"].max()
) * 20

customer_health["HealthScore"] = (
    customer_health["RevenueScore"]
    + customer_health["PaymentScore"]
    + customer_health["ActivityScore"]
)

def classify_health(score):

    if score >= 75:
        return "Healthy"

    elif score >= 50:
        return "Watchlist"

    else:
        return "At Risk"

customer_health["CustomerStatus"] = (
    customer_health["HealthScore"]
    .apply(classify_health)
)

customer_health = customer_health.sort_values(
    by="HealthScore",
    ascending=False
)

print("\n===== CUSTOMER HEALTH SCORES =====")
print(
    customer_health[
        [
            "TotalRevenue",
            "AvgDaysLate",
            "HealthScore",
            "CustomerStatus"
        ]
    ].head(15)
)


# AUTOMATED INSIGHTS


print("\n===== AUTOMATED BUSINESS INSIGHTS =====")

print(
    f"\n• {late_payment_rate:.2f}% of invoices are paid late."
)

print(
    f"\n• Disputed invoices take "
    f"{extra_days:.2f} additional days to settle."
)

worst_customer = (
    customer_health
    .sort_values(by="HealthScore")
    .index[0]
)

worst_score = (
    customer_health
    .sort_values(by="HealthScore")
    .iloc[0]["HealthScore"]
)

print(
    f"\n• Customer {worst_customer} "
    f"has the lowest health score "
    f"({worst_score:.2f})."
)

print(
    f"\n• Country {highest_delay_country} "
    f"shows the highest payment delays."
)


# ==========================================
# EXECUTIVE SUMMARY REPORT


print("\n")
print("=" * 60)
print("ACCOUNTS RECEIVABLE INTELLIGENCE REPORT")
print("=" * 60)

print(f"\nTotal Invoice Value: ${total_invoice_value:,.2f}")
print(f"Total Customers: {total_customers}")
print(f"Average Collection Time: {avg_days_to_settle:.2f} days")
print(f"Late Payment Rate: {late_payment_rate:.2f}%")

print(
    f"\nDisputed invoices require "
    f"{extra_days:.2f} additional days to settle."
)

print(
    f"\nCritical Priority Customers: "
    f"{len(critical_customers)}"
)

print(
    f"High Risk Customers: "
    f"{len(high_risk_customers)}"
)

print(
    f"\nHighest Delay Country: "
    f"{highest_delay_country}"
)

worst_customer = (
    customer_health
    .sort_values(by="HealthScore")
    .index[0]
)

worst_score = (
    customer_health
    .sort_values(by="HealthScore")
    .iloc[0]["HealthScore"]
)

print(
    f"\nMost At-Risk Customer: "
    f"{worst_customer}"
)

print(
    f"Customer Health Score: "
    f"{worst_score:.2f}"
)

print("\nRecommended Actions:")

print("- Prioritize critical customers for collections.")
print("- Reduce invoice disputes to improve cash flow.")
print("- Monitor high-risk customers closely.")
print("- Review collection strategy in high-delay countries.")
print("- Focus on customers with low health scores.")



# EXPORT REPORTS


customer_risk.to_csv(
    "reports/customer_risk_report.csv"
)

country_analysis.to_csv(
    "reports/country_analysis.csv"
)

customer_health.to_csv(
    "reports/customer_health_report.csv"
)

high_value_risky.to_csv(
    "reports/high_value_risky_customers.csv"
)

aging_analysis.to_csv(
    "reports/aging_analysis.csv"
)

print("\nReports exported successfully!")