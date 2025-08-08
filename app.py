import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Setup model
model = genai.GenerativeModel("gemini-1.5-flash")
# LLM interaction
def get_mortgage_advice(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Mortgage calculator
def calculate_monthly_payment(principal, annual_rate, years):
    r = annual_rate / 12 / 100
    n = years * 12
    if r == 0: return principal / n
    monthly = principal * r * (1 + r)**n / ((1 + r)**n - 1)
    return monthly

# Generate amortization schedule
def amortization_schedule(principal, rate, years, monthly_payment):
    r = rate / 12 / 100
    balance = principal
    schedule = []
    for i in range(years * 12):
        interest = balance * r
        principal_payment = monthly_payment - interest
        balance -= principal_payment
        schedule.append((i + 1, balance, principal_payment, interest))
        if balance <= 0:
            break
    return schedule

# UI
st.set_page_config(page_title="Mortgage Advisor", layout="centered")
st.title("🏠 Mortgage Advisor Copilot")
st.markdown("Ask mortgage-related questions and view visual breakdowns 📊")

with st.form("mortgage_form"):
    home_price = st.number_input("🏷 Home Price ($)", value=500000)
    down_payment = st.number_input("💰 Down Payment ($)", value=100000)
    interest_rate = st.number_input("📉 Interest Rate (%)", value=6.5)
    term_years = st.selectbox("📆 Loan Term (Years)", [15, 20, 30])
    user_query = st.text_area("❓ Ask a question about your mortgage")

    submitted = st.form_submit_button("Get Advice")

if submitted:
    loan_amount = home_price - down_payment
    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, term_years)
    st.success(f"📊 Estimated Monthly Payment: ${monthly_payment:.2f}")

    # Amortization
    schedule = amortization_schedule(loan_amount, interest_rate, term_years, monthly_payment)
    months = [x[0] for x in schedule]
    balances = [x[1] for x in schedule]
    principal_paid = [x[2] for x in schedule]
    interest_paid = [x[3] for x in schedule]

    # Pie Chart: Total Principal vs Total Interest
    total_interest = sum(interest_paid)
    total_principal = sum(principal_paid)

    fig1, ax1 = plt.subplots()
    ax1.pie([total_principal, total_interest], labels=["Principal", "Interest"], autopct='%1.1f%%')
    ax1.set_title("💸 Total Payment Breakdown")
    st.pyplot(fig1)

    # Line Graph: Balance over time
    fig2, ax2 = plt.subplots()
    ax2.plot(months, balances, label="Remaining Balance", color='blue')
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Balance ($)")
    ax2.set_title("📉 Mortgage Amortization Schedule")
    ax2.grid(True)
    st.pyplot(fig2)

    # Send prompt to Gemini
    full_prompt = f"""
    You are a mortgage advisor bot.

    Given the following mortgage:
    - Home price: ${home_price}
    - Down payment: ${down_payment}
    - Interest rate: {interest_rate}%
    - Loan term: {term_years} years
    - Loan amount: ${loan_amount}
    - Monthly payment: ${monthly_payment:.2f}
    - Total interest paid: ${total_interest:.2f}
    - Total principal paid: ${total_principal:.2f}

    User question: {user_query}

    Provide advice in simple, friendly language.
    """
    st.markdown("### 🧠 AI Mortgage Advice")
    response = get_mortgage_advice(full_prompt)
    st.write(response)
