import logging
import os
from sqlalchemy.orm.exc import NoResultFound

from katalyst_exchange import session, PLATFORM_ETHEREUM, PLATFORM_WAVES
from katalyst_exchange.ethereum import send_ethereum_tx
from katalyst_exchange.waves import send_waves_tx
from katalyst_exchange.models import ExchangeTx, get_actual_exchange_rate


def exchange_txs():
    """
    Transactions processing.
    """
    # get all transactions with status "new"
    txs = session.query(ExchangeTx).filter(ExchangeTx.status == ExchangeTx.STATUS_NEW).all()  # type: list[ExchangeTx]

    for tx in txs:

        logging.getLogger('tx_processing').info('Working with %s', tx)

        # currency exchange rate for incoming and outcome currencies
        try:
            income_exchange_rate = get_actual_exchange_rate(tx.income_platform).value
            outcome_exchange_rate = get_actual_exchange_rate(tx.outcome_platform).value
        except NoResultFound:  # if suddenly we could not get exchange rates
            logging.getLogger('tx_processing').critical('Missed exchange rate for one of platforms %s',
                                                        [tx.income_platform, tx.outcome_platform])
            continue

        tx.income_exchange_rate = income_exchange_rate
        tx.outcome_exchange_rate = outcome_exchange_rate
        tx.outcome_amount = int(tx.income_amount * income_exchange_rate / outcome_exchange_rate)

        logging.getLogger('tx_processing').debug('Calculating outcome amount %s', {
            'income_amount': tx.income_amount,
            'income_exchange_rate': income_exchange_rate,
            'outcome_exchange_rate': outcome_exchange_rate
        })

        # let send reverse transaction
        try:
            logging.getLogger('tx_processing').info('Creating exchange transaction')

            if tx.outcome_platform == PLATFORM_ETHEREUM:
                outcome_tx_id = send_ethereum_tx(tx, os.getenv('ETHEREUM_WALLET_ADDRESS'))
            elif tx.outcome_platform == PLATFORM_WAVES:
                outcome_tx_id = send_waves_tx(tx, os.getenv('WAVES_WALLET_ADDRESS'),
                                              os.getenv('WAVES_WALLET_PRIVATE_KEY'))
            else:
                raise ValueError('Unknown platform "{}"' % tx.outcome_platform)

        except Exception as e:
            tx.status = ExchangeTx.STATUS_FAILED
            tx.status_data = str(e)

            logging.getLogger('tx_processing').exception('Failed to create exchange transaction "%s"', str(e),
                                                         exc_info=False)
        else:
            # marking transaction as "done" if we will not check transaction state in future
            tx.status = ExchangeTx.STATUS_DONE if os.getenv('DISABLE_TRANSACTION_CHECK', True) \
                else ExchangeTx.STATUS_AWAITING_PROCESSING
            tx.outcome_tx_id = outcome_tx_id

            logging.getLogger('tx_processing').info('Exchange transaction has been created successfully')

    session.commit()
