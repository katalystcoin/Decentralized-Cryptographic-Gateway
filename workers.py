import logging

from katalyst_exchange.config import ETHEREUM_WALLET_ADDRESS, WAVES_WALLET_ADDRESS
from katalyst_exchange.exchange import exchange_txs
from katalyst_exchange.parser import load_txs
from katalyst_exchange.waves import get_waves_txs
from katalyst_exchange.ethereum import get_ethereum_txs

if __name__ == '__main__':

    print(12)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

    tx_processing_log = logging.getLogger('tx_processing')
    tx_processing_log_fh = logging.FileHandler('tx_processing.log')
    tx_processing_log.addHandler(tx_processing_log_fh)

    data_loading_log = logging.getLogger('data_loading')
    data_loading_log_fh = logging.FileHandler('data_loading.log')
    data_loading_log.addHandler(data_loading_log_fh)

    # пытаемся получить нужные данные
    load_txs(get_ethereum_txs, ETHEREUM_WALLET_ADDRESS)
    load_txs(get_waves_txs, WAVES_WALLET_ADDRESS)

    # производим обмен
    exchange_txs()
