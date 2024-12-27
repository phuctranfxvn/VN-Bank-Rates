from fastapi import FastAPI
from datetime import datetime
from .services.techcombank import Techcombank
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
    if bank_name == "techcombank":
        return Techcombank().get_rate(from_currency, to_currency, date_rate)
