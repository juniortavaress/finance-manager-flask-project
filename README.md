# finance-manager-flask-project
 
# 📊 Personal Finance Manager

A robust personal finance management system built with **Flask**, designed to track bank transactions, manage investment portfolios, and analyze crypto and stock market assets.

## 🚀 Live Demo
The project is currently deployed and can be accessed here:
🔗 [https://FineInvest.pythonanywhere.com/](https://FineInvest.pythonanywhere.com/)

---

## ⚠️ Important Notes (Host Limitations)

Since this project is hosted on a **PythonAnywhere Free Tier**, there are specific operational limitations to keep in mind regarding the live link:

1. **Real-Time Quotes:** Currency and asset price charts may not update. This is because the free host restricts outgoing requests to external APIs that are not on their official "whitelist."
2. **Investment Data Stale-out:** Over time, the investment section may become outdated. The free plan does not support **Schedulers** (cron jobs), making it impossible to automate the daily background tasks required to fetch closing prices for stocks and cryptocurrencies.

*For the full experience, including live API data fetching, it is recommended to run the project locally.*

---

## ✨ Features

* **Secure Authentication:** Full login system with encrypted password handling.
* **Transaction Management:** Record and categorize income and expenses.
* **Investment Dashboard:** Track Stock and Cryptocurrency performance in one place.
* **Data Processing:** Automated handling of brokerage notes and bank statements.
* **Responsive Design:** A modern, clean interface built for a seamless user experience.

## 🛠️ Technologies Used

* **Backend:** Python 3.10+ & Flask
* **Database:** SQLite (SQLAlchemy ORM)
* **Frontend:** HTML, CSS and JavaScript
* **Security:** Flask-Bcrypt & Flask-Login
* **Data Analysis:** Pandas for financial data processing
