import requests
import re
import ssl
import json
from datetime import datetime
from requests.adapters import HTTPAdapter

# Create a custom SSL context with legacy renegotiation enabled
context = ssl.create_default_context()
context.options |= ssl.OP_LEGACY_SERVER_CONNECT  # Enable legacy renegotiation


class CustomHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = context
        return super(CustomHttpAdapter, self).init_poolmanager(*args, **kwargs)


API_URL = "https://bidv.com.vn/ServicesBIDV/ExchangeDetailServlet"


class Bidv:
    def get_data_from_bidv(self, date_rate):
        session = requests.Session()
        session.mount('https://', CustomHttpAdapter())

        payload = json.dumps({
            "data": date_rate.strftime("%d/%m/%Y")
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = session.post(API_URL, headers=headers, data=payload)
        response.raise_for_status()  # Raise HTTP errors, if any
        return json.loads(response.text)

    def get_all_rates(self, date_rate):
        result = []
        try:
            data = self.get_data_from_bidv(date_rate=date_rate)
            currency_rate_data = data["data"]
            data_time = data["day_vi"] + " " + data["hour"]
            data_time = datetime.strptime(data_time, "%d/%m/%Y %H:%M")
            data_time = data_time.strftime("%Y-%m-%d %H:%M:%S")
            for line in currency_rate_data:
                sell_value = line.get("ban", '0').replace(",", "")
                sell_value = sell_value != '-' and float(sell_value) or None
                buy_cash = line.get("muaTm", '0').replace(",", "")
                buy_cash = buy_cash != '-' and float(buy_cash) or None
                buy_transfer = line.get("muaCk", '0').replace(",", "")
                buy_transfer = buy_transfer != '-' and float(
                    buy_transfer) or None

                result.append({
                    "updated_time": data_time,
                    "currency_code": line["currency"].replace(" ", ""),
                    "sell_cash": sell_value,
                    "sell_transfer": sell_value,
                    "buy_cash": buy_cash,
                    "buy_transfer": buy_transfer,
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
                "message": "Unable to connect to BIDV to get rates",
            }

    def get_rate(self, from_currency: str, to_currency: str, date_rate: datetime):
        from_currency, to_currency = from_currency.upper(), to_currency.upper()

        try:
            data = self.get_data_from_bidv(date_rate=date_rate)
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
                return {"status": "error", "code": 10, "message": "No data or invalid currency code"}

            return {"status": "success", "code": 200, "result": result}

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "code": 10,
                "message": "Unable to connect to BIDV to get rates",
            }

    def get_exchange_rate_data(self, data: dict, from_currency: str):
        search_label = False
        requested_from_currency = from_currency
        # Special Case of USD
        if from_currency.startswith("USD"):
            search_label = from_currency.replace("USD", "")
            from_currency = "USD"

        currency_rate_data = data["data"]
        data_time = data["day_vi"] + " " + data["hour"]
        data_time = datetime.strptime(data_time, "%d/%m/%Y %H:%M")
        data_time = data_time.strftime("%Y-%m-%d %H:%M:%S")
        found_line = False
        for line in currency_rate_data:
            if requested_from_currency == line["currency"].upper():
                found_line = line
                break

            elif search_label and search_label.isdigit() and from_currency == "USD":
                pattern = r'\((.*?)\)'
                match = re.search(pattern, line["currency"])
                if match:
                    usd_keys = match.group(1).split("-")
                    if int(search_label) in map(int, usd_keys):
                        found_line = line
                        break

        if found_line:
            sell_value = found_line.get("ban", '0').replace(",", "")
            sell_value = sell_value != '-' and float(sell_value) or None
            buy_cash = found_line.get("muaTm", '0').replace(",", "")
            buy_cash = buy_cash != '-' and float(buy_cash) or None
            buy_transfer = found_line.get("muaCk", '0').replace(",", "")
            buy_transfer = buy_transfer != '-' and float(buy_transfer) or None

            return {
                "updated_time": data_time,
                "sell_cash": sell_value,
                "sell_transfer": sell_value,
                "buy_cash": buy_cash,
                "buy_transfer": buy_transfer,
            }

        return {}
