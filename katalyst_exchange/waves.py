import re

import base58
import pywaves
import requests

import katalyst_exchange
from katalyst_exchange.config import WAVES_WALLET_ADDRESS, WAVES_WALLET_PRIVATE_KEY, WAVESNODES_URL_PATTERN
from katalyst_exchange.ethereum import PLATFORM_ETHEREUM
from katalyst_exchange.models import ExchangeTx

PLATFORM_WAVES = 'waves'


def send_waves_tx(tx):
    """

    :param tx: Обменная транзакция
    :type tx: ExchangeTx
    :return: Transaction hash
    :rtype: str
    """
    pywaves.setNode(node='http://127.0.0.1:6869', chain='testnet')
    my_address = pywaves.Address(WAVES_WALLET_ADDRESS, privateKey=WAVES_WALLET_PRIVATE_KEY)
    response = my_address.sendWaves(recipient=pywaves.Address(tx.outcome_address), amount=tx.outcome_amount)

    katalyst_exchange.data_loading_log.debug('Waves response: %s', response)

    return response['id']


def get_waves_txs(address):
    """
    Получение списка последних транзакций из Waves.
    :rtype: list(ExchangeTx)
    """
    try:
        resp = requests.get(
            WAVESNODES_URL_PATTERN.format(address=address),
            timeout=30).json()
    except Exception as e:
        katalyst_exchange.data_loading_log.exception('Failed get data "%s"', e, exc_info=False)
        return []

    for obj in resp[0]:

        in_tx_id = obj['id']

        # если тип транзакции не тот, то скипаем
        if obj['type'] != 4:
            yield in_tx_id
            continue

        out_address = base58.b58decode(obj['attachment']).decode()

        # валидируем ethereum адрес, если получатель некорректно укзан, то скипаем
        p = re.compile(r'^0x[a-fA-F0-9]{40}$')  # 0x81b7e08f65bdf5648606c89998a9cc8164397647
        if not p.match(out_address):
            yield in_tx_id
            continue

        in_amount = obj['amount']
        in_address = obj['sender']

        yield ExchangeTx(income_tx_id=in_tx_id, income_amount=in_amount,
                         income_address=in_address, income_platform=PLATFORM_WAVES,
                         outcome_address=out_address, outcome_platform=PLATFORM_ETHEREUM)
