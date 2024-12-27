import requests
import re
from datetime import datetime

API_URL = "https://www.vietcombank.com.vn/api/exchangerates?date=%(rate_date)s"



class Vietcombank:
    def get_rate(self, from_currency: str, to_currency: str, date_rate: datetime):
        url = API_URL % {"rate_date": date_rate.strftime("%Y-%m-%d")}
        from_currency, to_currency = from_currency.upper(), to_currency.upper()
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if to_currency != "VND":
                currency1_vnd_rate = self.get_exchange_rate_data(
                    data, from_currency)
                currency2_vnd_rate = self.get_exchange_rate_data(
                    data, to_currency)

                result = {
                    key: round(
                        currency1_vnd_rate[key] / currency2_vnd_rate[key], 2)
                    if currency1_vnd_rate[key] and currency2_vnd_rate[key]
                    else None
                    for key in currency1_vnd_rate
                }
            else:
                result = self.get_exchange_rate_data(
                    data, from_currency)

            if not result:
                return {
                    "status": "error",
                    "code": 10,
                    "message": "No data or invalid currency code"
                }

            return {
                "status": "success",
                "code": 200,
                "result": result
            }

        except requests.exceptions.RequestException:
            return {
                "status": "error",
                "code": 10,
                "message": "Unable to connect to Techcombank to get rates",
            }

    def get_exchange_rate_data(self, data: list, from_currency: str):

        rate_data = data.get("Data")
        updated_time = data.get("UpdatedDate")
        updated_time = datetime.fromisoformat(updated_time)
        updated_time = updated_time.strftime("%Y-%m-%d %H:%M:%S")
                    
        for line in rate_data:
            if line["currencyCode"].upper() == from_currency:
                return {
                    "updated_time": updated_time,
                    "sell_cash": float(line.get("sell", 0)) or None,
                    "sell_transfer": float(line.get("sell", 0)) or None,
                    "buy_cash": float(line.get("cash", 0)) or None,
                    "buy_transfer": float(line.get("transfer", 0)) or None,
                }

        return {}
