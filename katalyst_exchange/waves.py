import logging
import os

import re

import base58
import pywaves
import requests

from katalyst_exchange import PLATFORM_ETHEREUM, PLATFORM_WAVES
from katalyst_exchange.models import ExchangeTx


def send_waves_tx(tx, from_address, from_address_private_key):
    """
    Sending transaction to the blockchain.
    :param tx: Exchange transaction
    :type tx: ExchangeTx
    :param from_address: The address from which it we send
    :type from_address: str
    :param from_address_private_key: Private key for sender wallet (must be in Waves node configuration)
    :type from_address_private_key: str
    :return: Transaction hash
    :rtype: str
    """
    logging.getLogger('data_loading').info('Sending Waves tx %s', tx)

    pywaves.setNode(node=os.getenv('WAVES_NODE_URL'), chain=os.getenv('WAVES_NODE_CHAIN'))
    my_address = pywaves.Address(from_address, privateKey=from_address_private_key)
    response = my_address.sendWaves(recipient=pywaves.Address(tx.outcome_address), amount=int(tx.outcome_amount))

    logging.getLogger('data_loading').info('Tx sent successfully')
    logging.getLogger('data_loading').debug('Node response dump: %s', response)

    return response['id']


def get_waves_txs(address):
    """
    Get the list of recent transactions from Waves. Here we use third party service wavesnode.net.
    :rtype: list(ExchangeTx)
    """
    logging.getLogger('data_loading').info('Trying to get Waves txs')

    try:
        resp = requests.get(os.getenv('WAVESNODES_URL_PATTERN').format(address=address), timeout=30).json()
    except Exception as e:
        logging.getLogger('data_loading').exception('Failed get txs data: %s', e, exc_info=False)
        return []

    for obj in resp[0]:

        logging.debug('Result item dump: %s', obj)

        in_tx_id = obj['id']

        # we are interesting only in 4 type
        if obj['type'] != 4:
            yield in_tx_id
            continue

        out_address = base58.b58decode(obj['attachment']).decode()

        assert type(out_address) is str

        # we must validate receiver address and skip transaction aggregation if it is invalid
        p = re.compile(r'^0x[a-fA-F0-9]{40}$')  # data example: 0x81b7e08f65bdf5648606c89998a9cc8164397647
        if not p.match(out_address):
            yield in_tx_id
            continue

        in_amount = int(obj['amount'])
        in_address = obj['sender']

        yield ExchangeTx(income_tx_id=in_tx_id, income_amount=in_amount,
                         income_address=in_address, income_platform=PLATFORM_WAVES,
                         outcome_address=out_address, outcome_platform=PLATFORM_ETHEREUM)
