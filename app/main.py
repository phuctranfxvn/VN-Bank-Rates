from fastapi import FastAPI
from datetime import datetime
from . import services

# App
app = FastAPI(title="VN Currency Rates",
              description="Get currency rates", version="1.0")


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Microservice"}

# Main roots for banks


@app.get("/currency_rate/{bank_name}/{from_currency}/{to_currency}/{date_rate}")
def get_currency_rate(bank_name: str, from_currency: str, to_currency: str, date_rate: str):
    date_rate = datetime.strptime(date_rate, "%Y%m%d")
    bank_name = bank_name.lower()
    try:
        bank_module = getattr(services, bank_name)
        BankClass = getattr(bank_module, bank_name.capitalize())
    except:
        return {
            "status": "error",
            "code": 1,
            "message": "Bank {0} is not available".format(bank_name)
        }
    return BankClass().get_rate(from_currency, to_currency, date_rate)

@app.get("/all_currency_rate/{bank_name}/{date_rate}")
def get_all_currency_rate(bank_name: str, date_rate: str):
    date_rate = datetime.strptime(date_rate, "%Y%m%d")
    bank_name = bank_name.lower()
    try:
        bank_module = getattr(services, bank_name)
        BankClass = getattr(bank_module, bank_name.capitalize())
    except:
        return {
            "status": "error",
            "code": 1,
            "message": "Bank {0} is not available".format(bank_name)
        }
    return BankClass().get_all_rates(date_rate)
