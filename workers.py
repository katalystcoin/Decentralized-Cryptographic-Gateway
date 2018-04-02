from katalyst_exchange.config import ETHEREUM_WALLET_ADDRESS, WAVES_WALLET_ADDRESS

from katalyst_exchange.exchange import exchange_txs
from katalyst_exchange.parser import load_txs
from katalyst_exchange.ethereum import get_ethereum_txs
from katalyst_exchange.waves import get_waves_txs

# пытаемся получить нужные данные
load_txs(get_ethereum_txs, ETHEREUM_WALLET_ADDRESS)
load_txs(get_waves_txs, WAVES_WALLET_ADDRESS)

# производим обмен
exchange_txs()
