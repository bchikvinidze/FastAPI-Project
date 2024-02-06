Project was developed fully using TDD.

Before running the code, run mypy --install-types
run python -m library.runner --host 127.0.0.1 --port 9000 from path right above library folder.

After running above command, write http://127.0.0.1:9000/docs in your browser to access the docs.

Bitcoin to USD API: https://www.blockchain.com/explorer/api/exchange_rates_api

Things left to do:
1) ✅ `GET /wallets/{address}/transactions`
2) ✅ `GET /statistics`
3) ✅ mypy fixes
4) ✅  tests are all in 1 file, maybe redistribute to few files? I got 1 point deduction last time for this
5) ❗some tests are too heavy. find a way to make them shorter and easier to read
6) ✅Some errors are not informative: add input information in output messages, not just static message string.
7) ✅ ~~Serialization is dargveving Single responsibility - think about how to solve this proble. (comment in the beginning of hw)~~
8) 🔶ar gvchirdeba mara tu gindat In-Memory repository shegidzliat sheqmnat. wina davalebashi ar gamiketebia ar iyo sachiro da arc aq gvchirdeba.
9) ❗Service.py-shi Service class could be decomposed into multiple smaller classes and we will have better S from SOLID. : In Progress
10) ❗proeqtis README-s dawera - ra failshi ra xdeba.
11) ✅  test_transactions_get- es dasaweria da shesabamisad cvlilebebi transactionis get-stvis Service class-shi. 
12) ❗test transaction from own to another wallet(fee is correct)


## Intro

The aim of the project is to create an HTTP API for the "Bitcoin Wallet" application.

Worry not, we will not do any blockchain operations. Instead, we will use SQLite for persistence. However, (fingers crossed) at this point you have enough knowledge to create a solution that one can (relatively) easily extend to use Postgres/MySQL or even the real blockchain.

Concurrency is also out of scope. You do not have to solve the so-called "double spending" issue, but you are very much encouraged to think about how you would tackle it.

## API Spec

`POST /users`
  - Registers user
  - Returns API key that can authenticate all subsequent requests for this user

`POST /wallets`
  - Requires API key
  - Create BTC wallet 
  - Deposits 1 BTC (or 100000000 satoshis) automatically to the new wallet
  - User may register up to 3 wallets
  - Returns wallet address and balance in BTC and USD

`GET /wallets/{address}`
  - Requires API key
  - Returns wallet address and balance in BTC and USD

`POST /transactions`
  - Requires API key
  - Makes a transaction from one wallet to another
  - Transaction is free if the same user is the owner of both wallets
  - System takes a 1.5% (of the transferred amount) fee for transfers to the foreign wallets

`GET /transactions`
  - Requires API key
  - Returns list of transactions

`GET /wallets/{address}/transactions`
  - Requires API key
  - returns transactions related to the wallet

`GET /statistics`
  - Requires pre-set (hard coded) Admin API key
  - Returns the total number of transactions and platform profit

## Technical requirements
  
- Python 3.11
- [FastAPI](https://fastapi.tiangolo.com/) as a web framework
- [SQLite](https://docs.python.org/3/library/sqlite3.html) for persistence
- Use publicaly available API of your choice for BTC -> USD conversion
- Decide the structure of the requests and responses yourselves
- Use "X-API-KEY" HTTP header to pass and validate API key on server side
- Implement only API endpoints (UI is out of scope)
- Concurrancy is out of scope

## Testing

Provide automated tests that will falsify regressions (change in behaviour) in your software artifacts.
