import logging

from katalyst_exchange import session, PLATFORM_ETHEREUM, PLATFORM_WAVES
from katalyst_exchange.config import DISABLE_TRANSACTION_CHECK
from katalyst_exchange.ethereum import send_ethereum_tx
from katalyst_exchange.waves import send_waves_tx
from katalyst_exchange.models import ExchangeTx, get_actual_exchange_rate


def get_sender(platform):
    """
    Функция для получения транспорта для отправки транзакции передачи средств.
    :param platform: Название платформы
    :type platform: str
    :return:
    """
    if platform == PLATFORM_ETHEREUM:
        return send_ethereum_tx
    if platform == PLATFORM_WAVES:
        return send_waves_tx

    raise ValueError('Unknown platform "{}"' % platform)


def exchange_txs():
    """
    Обработка тех транзакций, о которых мы знаем.
    """
    # берём все обменные транзакции с статусом "new"
    txs = session.query(ExchangeTx).filter(ExchangeTx.status == ExchangeTx.STATUS_NEW).all()  # type: list[ExchangeTx]

    for tx in txs:

        logging.getLogger('tx_processing').info('Working with %s', tx)

        # курс обмена для "входящей" валюты
        income_exchange_rate = get_actual_exchange_rate(tx.income_platform).value

        # курс обмена для "исходящей" валюты
        outcome_exchange_rate = get_actual_exchange_rate(tx.outcome_platform).value

        # вдруг мы не смогли получить курсы обмена
        if income_exchange_rate is None or outcome_exchange_rate is None:
            missed_platform_name = tx.income_platform if income_exchange_rate is None else tx.outcome_platform
            logging.getLogger('tx_processing').critical('Missed exchange rate for %s', missed_platform_name)

        tx.income_exchange_rate = income_exchange_rate
        tx.outcome_exchange_rate = outcome_exchange_rate
        tx.outcome_amount = tx.income_amount * income_exchange_rate / outcome_exchange_rate

        # отправляем ответный перевод
        try:
            logging.getLogger('tx_processing').info('Creating exchange transaction')

            sender = get_sender(tx.outcome_platform)

            outcome_tx_id = sender(tx)

        except Exception as e:
            tx.status = ExchangeTx.STATUS_FAILED
            tx.status_data = str(e)

            logging.getLogger('tx_processing').exception('Failed to create exchange transaction %s', str(e),
                                                         exc_info=False)
        else:
            # если мы не проверяем состояние транзакции в будущем, то помечаем её как успешную
            tx.status = ExchangeTx.STATUS_DONE if DISABLE_TRANSACTION_CHECK else ExchangeTx.STATUS_AWAITING_PROCESSING
            tx.outcome_tx_id = outcome_tx_id

            logging.getLogger('tx_processing').info('Exchange transaction has been created successfully')

    session.commit()
