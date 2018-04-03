import logging
import os

if __name__ == '__main__':

    logging.basicConfig(level=os.getenv('LOG_LEVEL'), format=os.getenv('LOG_GLOBAL_FORMAT'))

    tx_processing_log = logging.getLogger('tx_processing')
    tx_processing_log_fh = logging.FileHandler(os.getenv('LOG_TX_PROCESSING_FILE'))
    tx_processing_log_fh.setFormatter(logging.Formatter(os.getenv('LOG_TX_PROCESSING_FORMAT')))
    tx_processing_log.addHandler(tx_processing_log_fh)

    data_loading_log = logging.getLogger('data_loading')
    data_loading_log_fh = logging.FileHandler(os.getenv('LOG_DATA_LOADING_FILE'))
    data_loading_log_fh.setFormatter(logging.Formatter(os.getenv('LOG_DATA_LOADING_FORMAT')))
    data_loading_log.addHandler(data_loading_log_fh)

    logging.info('Starting')

    from katalyst_exchange.exchange import exchange_txs
    from katalyst_exchange.parser import load_txs
    from katalyst_exchange.waves import get_waves_txs
    from katalyst_exchange.ethereum import get_ethereum_txs

    # пытаемся получить нужные данные
    load_txs(get_ethereum_txs, os.getenv('ETHEREUM_WALLET_ADDRESS'))
    load_txs(get_waves_txs, os.getenv('WAVES_WALLET_ADDRESS'))

    # производим обмен
    exchange_txs()

    logging.info('Finished')
