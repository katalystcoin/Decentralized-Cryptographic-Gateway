#!/usr/bin/env bash

export DATABASE_URL="sqlite:////home/nikita/Code/aoza/katalyst-exchange-worker/db.sqlite"
# export DATABASE_URL=postgresql://katalyst:1234@localhost/katalyst

export ETHEREUM_WALLET_ADDRESS="0xea28d0e43dcf96f9865b05242846ac48d7d83040"
export ETHERSCAN_API_KEY="HY7QTYCHBUH36KFCI17YSZBDASMXHES1H9"
export ETHERSCAN_URL_PATTERN="https://api-rinkeby.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey={api_key}"

export WAVES_WALLET_ADDRESS="3Mxs7HBE7PuQG4eLc1AnsR4q5ibogc4jNCF"
export WAVES_WALLET_PRIVATE_KEY="5MWFbj6Bjksx73BSPiJ8GVwgEwnzxv1ADfcsS2xfQhMA"
export WAVESNODES_URL_PATTERN="https://testnode3.wavesnodes.com/transactions/address/{address}/limit/100"

export LOGS_PATH=.


#python test.py
python workers.py