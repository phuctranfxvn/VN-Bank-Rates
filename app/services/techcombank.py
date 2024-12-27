import requests
import re
from datetime import datetime

API_URL = (
    "https://techcombank.com/content/techcombank/web/vn/en/cong-cu-tien-ich/"
    "ty-gia/_jcr_content.exchange-rates.%(rate_date)s.integration.json"
)


class Techcombank:

    def get_data_from_techcombank(self, date_rate):
        url = API_URL % {"rate_date": date_rate.strftime("%Y-%m-%d")}
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_all_rates(self, date_rate):
        result = []
        try:
            data = self.get_data_from_techcombank(date_rate=date_rate).get(
                "exchangeRate", {}).get("data", [])
            for line in data:
                updated_time = None
                if line.get("inputDate"):
                    dt_obj = datetime.strptime(
                        line.get("inputDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
                    updated_time = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                currency_code = line["sourceCurrency"]

                if currency_code == "USD":
                    currency_code = line["label"].replace(" ", "")

                result.append({
                    "updated_time": updated_time,
                    "currency_code": currency_code,
                    "sell_cash": float(line.get("askRateTM", 0)) or None,
                    "sell_transfer": float(line.get("askRate", 0)) or None,
                    "buy_cash": float(line.get("bidRateTM", 0)) or None,
                    "buy_transfer": float(line.get("bidRateCK", 0)) or None,
                })

            return {
                "status": "success",
                "code": 200,
                "result": result
            }

        except:
            return {
                "status": "error",
                "code": 10,
                "message": "Unable to connect to Techcombank to get rates",
            }

    def get_rate(self, from_currency: str, to_currency: str, date_rate: datetime):
        url = API_URL % {"rate_date": date_rate.strftime("%Y-%m-%d")}
        from_currency, to_currency = from_currency.upper(), to_currency.upper()
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json().get("exchangeRate", {}).get("data", [])

            if to_currency != "VND":
                currency1_vnd_rate = self.get_exchange_rate_data(
                    data, from_currency, "VND")
                currency2_vnd_rate = self.get_exchange_rate_data(
                    data, to_currency, "VND")

                result = {
                    key: round(
                        currency1_vnd_rate[key] / currency2_vnd_rate[key], 2)
                    if currency1_vnd_rate[key] and currency2_vnd_rate[key]
                    else None
                    for key in currency1_vnd_rate
                }
            else:
                result = self.get_exchange_rate_data(
                    data, from_currency, to_currency)

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

    def get_exchange_rate_data(self, data: list, from_currency: str, to_currency: str):
        search_label = False

        # Special Case of USD
        if from_currency.startswith("USD"):
            search_label = from_currency.replace("USD", "") or "1"
            from_currency = "USD"

        for line in data:
            # Special case for USD. We have
            # USD (1, 2)
            # USD (5, 10, 20)
            # USD (50, 100)
            if search_label and line["sourceCurrency"].upper() == "USD":
                label = line.get("label", "")
                pattern = r"\d{1,3}(?:,\d{1,3})*"
                match = re.search(pattern, label)
                if match and int(search_label) not in map(int, match.group().split(",")):
                    continue

            if (
                line["sourceCurrency"].upper() == from_currency
                and line["targetCurrency"].upper() == to_currency
            ):
                # Get Updated Time and format to %Y-%m-%d %H:%M:%S
                updated_time = None
                if line.get("inputDate"):
                    dt_obj = datetime.strptime(
                        line.get("inputDate"), "%Y-%m-%dT%H:%M:%S.%fZ")
                    updated_time = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
                return {
                    "updated_time": updated_time,
                    "sell_cash": float(line.get("askRateTM", 0)) or None,
                    "sell_transfer": float(line.get("askRate", 0)) or None,
                    "buy_cash": float(line.get("bidRateTM", 0)) or None,
                    "buy_transfer": float(line.get("bidRateCK", 0)) or None,
                }

        return {}
