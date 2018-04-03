import binascii
import logging

import os
import re
import requests
from jsonrpcclient import HTTPClient

from katalyst_exchange import PLATFORM_ETHEREUM, PLATFORM_WAVES
from katalyst_exchange.models import ExchangeTx


def send_ethereum_tx(tx, from_address):
    """
    Sending transaction to the blockchain.
    :param tx: Exchange transaction
    :type tx: ExchangeTx
    :param from_address: The address from which it we send
    :type from_address: str
    :return: Transaction hash
    :rtype: str
    """
    logging.getLogger('data_loading').info('Sending Ethereum tx %s', tx)

    client = HTTPClient(os.getenv('ETHEREUM_NODE_URL'))
    response = client.request('eth_sendTransaction', [{
        'from': from_address,
        'to': tx.outcome_address,  # 0x prefixed value
        'value': '0x' + binascii.hexlify(str(tx.outcome_amount).encode()).decode(),
        'data': '0x' + binascii.hexlify(b'Exchange transaction').decode()
    }])

    logging.getLogger('data_loading').info('Tx sent successfully')
    logging.getLogger('data_loading').debug('Node response dump: %s', response)

    return response


def get_ethereum_txs(address):
    """
    Get the list of recent transactions from Ethereum. Here we use third party service etherscan.io
    :param address: Address for which we want to get transactions
    :type address: str
    :rtype: list(ExchangeTx)
    """
    logging.getLogger('data_loading').info('Trying to get Ethereum txs')

    try:
        resp = requests.get(os.getenv('ETHERSCAN_URL_PATTERN')
                            .format(address=address, api_key=os.getenv('ETHERSCAN_API_KEY')), timeout=30).json()
    except Exception as e:
        logging.getLogger('data_loading').exception('Failed get txs data: %s', e, exc_info=False)
        return []

    for obj in resp['result']:

        logging.debug('Result item dump: %s', obj)

        in_tx_id = obj['hash']

        out_address = binascii.unhexlify(obj['input'][2:]).decode()

        # we must validate receiver address and skip transaction aggregation if it is invalid
        p = re.compile(r'^[a-zA-Z0-9]{35}$')  # data example: 3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3
        if not p.match(out_address):
            yield in_tx_id
            continue

        in_amount = int(obj['value'])
        in_address = obj['from']

        yield ExchangeTx(income_tx_id=in_tx_id, income_amount=in_amount,
                         income_address=in_address, income_platform=PLATFORM_ETHEREUM,
                         outcome_address=out_address, outcome_platform=PLATFORM_WAVES)
