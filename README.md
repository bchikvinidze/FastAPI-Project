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
