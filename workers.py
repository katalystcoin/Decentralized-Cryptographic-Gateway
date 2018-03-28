import logging
from abc import ABC

import base58
import urllib3
from sqlalchemy import desc

from database import exchange_rates, last_transactions, database_connection, transactions, PLATFORM_WAVES, \
    PLATFORM_ETHEREUM, STATUS_FAILED, STATUS_AWAITING_PROCESSING

import requests


def get_actual_exchange_rate(connection, platform):
    """
    Получение актуального курса обмена для запрошенной платформы.
    :param connection: Подключение к БД
    :type connection: sqlalchemy.engine.Connection
    :param platform: Название платформы
    :type platform: str
    :return:
    """
    assert platform in [PLATFORM_WAVES, PLATFORM_ETHEREUM]

    return connection.execute(exchange_rates.select()).fetchone()['value']


def get_last_tx_id(connection, platform):
    """
    Получение актуального курса обмена для запрошенной платформы.
    :param connection: Подключение к БД
    :type connection: sqlalchemy.engine.Connection
    :param platform: Название платформы
    :type platform: str
    :return:
    """
    assert platform in [PLATFORM_WAVES, PLATFORM_ETHEREUM]

    tx = connection.execute(last_transactions.select().order_by(desc(last_transactions.c.id))).fetchone()

    return tx['tx_id'] if tx is not None else None


class AbstractTx(ABC):
    def __init__(self, tx_id, sender, receiver, amount):
        self.tx_id = None
        self.sender = None
        self.receiver = None
        self.amount = None


def get_waves_txs():
    data = requests.get(
        'https://testnode2.wavesnodes.com/transactions/address/3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3/limit/100',
        timeout=30).json()


last_tx_id = get_last_tx_id(database_connection, PLATFORM_WAVES)

logging.info('Last tx id "%s"', last_tx_id)

# пытаемся получить нужные данные
data = None
try:
    data = requests.get(
        'https://testnode2.wavesnodes.com/transactions/address/3MqtveWsgTE6jHzed32g8pp2YL7dkL8JvS3/limit/100',
        timeout=30).json()
except (requests.exceptions.RequestException, urllib3.exceptions.NewConnectionError) as e:
    logging.exception('Failed to connect to link', exc_info=False)
    exit(1)

new_last_tx_id = None

for tx in data[0]:  # проходимся по транзакциям

    logging.debug('Processing tx "%s"', tx['id'])

    # Если мы дошли до транзакции, которая у нас отмечена последней обработанной, значит новых транзакций для нас нету.
    if tx['id'] == last_tx_id:
        logging.debug('Current tx already processed, finishing')
        break

    if new_last_tx_id is None:  # если последняя транзакция не определена, выставляем по первой
        logging.debug('New last processed tx is "%s"', tx['id'])
        new_last_tx_id = tx['id']

    # если тип транзакции не тот, то скипаем
    if tx['type'] != 4:
        # @todo invalid status
        logging.debug('Invalid type')
        continue

    # если получатель некорректно укзан, то скипаем
    if not base58.b58decode(tx['attachment']):
        logging.debug('Empty receiver')
        continue

    r = database_connection.execute(transactions.insert(),
                                    income_tx_id=tx['id'],
                                    income_address=tx['sender'],
                                    income_amount=tx['amount'],
                                    income_platform=PLATFORM_WAVES,
                                    income_exchange_rate=1,
                                    outcome_address=base58.b58decode(tx['attachment']),
                                    outcome_amount=tx['amount'],
                                    outcome_platform=PLATFORM_ETHEREUM,
                                    outcome_exchange_rate=1
                                    )

    tx_id = r.inserted_primary_key[0]

    logging.debug('Transaction recorded %d', tx_id)

    # отправляем ответный перевод
    try:
        logging.info('Creating exchange transaction')
        # raise Exception('ttttt')
    except Exception as e:
        # если не получилось, помечаем её как свалившуюся
        database_connection.execute(transactions.update(transactions.c.id == tx_id), status=STATUS_FAILED,
                                    status_data=str(e))
        logging.exception('Failed to create exchange transaction %s', str(e), exc_info=False)
    else:
        # дописываем данные ответной транзакции
        database_connection.execute(transactions.update(transactions.c.id == tx_id), outcome_tx_id='123',
                                    status=STATUS_AWAITING_PROCESSING)
        logging.info('Exchange transaction has been created successfully')

if new_last_tx_id:
    database_connection.execute(last_transactions.insert(), platform=PLATFORM_WAVES, tx_id=new_last_tx_id)

# https://api-ropsten.etherscan.io/api?module=account&action=txlist&address=0xBA0c849aeb80289CB4A8A7EF21F0FB36217673CC&startblock=0&endblock=99999999&page=1&offset=100&sort=desc&apikey=HY7QTYCHBUH36KFCI17YSZBDASMXHES1H9
