# Vn Currency Rates



## Introduction

Micro service for exchange rates from banks in Vietnam:
- [x] Techcombank
- [ ] Vietcombank
- [x] BIDV
- [ ] Bangkok Bank

## Requirements

Install the requirements for the service

```
pip3 install -r requirements.txt
```

## Start the service

- Development
```
fastapi dev
```

- Production
```
fastapi run
```

## API

```
http://127.0.0.1:8000/currency_rate/{bank-name}/{from-currency}/{to-currency}/{date}

Example:
http://127.0.0.1:8000/currency_rate/techcombank/EUR/vnd/20241227
```

## Contributors
- Tran Thanh Phuc (phuctran.fx.vn@gmail.com)

## Maintainers
- Tran Thanh Phuc (phuctran.fx.vn@gmail.com)

