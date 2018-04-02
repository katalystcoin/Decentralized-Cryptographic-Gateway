import os

# Ethereum
ETHEREUM_WALLET_ADDRESS = '0xea28d0e43dcf96f9865b05242846ac48d7d83040'
ETHERSCAN_API_KEY = 'HY7QTYCHBUH36KFCI17YSZBDASMXHES1H9'
ETHERSCAN_URL_PATTERN = 'https://api-rinkeby.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey={api_key}'

# Waves
WAVES_WALLET_ADDRESS = '3Mxs7HBE7PuQG4eLc1AnsR4q5ibogc4jNCF'
WAVES_WALLET_PRIVATE_KEY = '5MWFbj6Bjksx73BSPiJ8GVwgEwnzxv1ADfcsS2xfQhMA'
WAVESNODES_URL_PATTERN = 'https://testnode3.wavesnodes.com/transactions/address/{address}/limit/100'

# Tx processing
DISABLE_TRANSACTION_CHECK = os.getenv('DISABLE_TRANSACTION_CHECK', True)

# Logging
LOGS_PATH = os.getenv('LOGS_PATH', '/tmp')
