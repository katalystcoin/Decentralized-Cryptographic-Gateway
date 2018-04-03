import logging

from sqlalchemy import desc

from katalyst_exchange import session
from katalyst_exchange.models import ExchangeTx, LastSeenTransaction


def load_txs(fnc, address):
    logging.getLogger('data_loading').info('Trying to get transactions for "%s" with "%s"', address, fnc.__name__)

    # get data from transactions from the blockchain
    txs = fnc(address)

    # let remember about last seen transaction
    last_tx_id = session.query(LastSeenTransaction.tx_id) \
        .filter(LastSeenTransaction.address == address) \
        .order_by(desc(LastSeenTransaction.id)) \
        .limit(1)\
        .scalar()

    logging.getLogger('data_loading').debug('Last seen transaction id "%s"', last_tx_id)

    new_last_tx_id = None

    for tx in txs:
        # if transaction without receiver data it is string value, not object
        tx_id = tx.income_tx_id if isinstance(tx, ExchangeTx) else tx

        logging.getLogger('data_loading').info('Processing transaction blockchain id "%s"', tx_id)
        logging.getLogger('data_loading').debug('Processing transaction dump: %s', tx)

        # there is no new data for us if processed transaction id same with id of last seen transaction in blockchain
        if tx_id == last_tx_id:
            logging.getLogger('data_loading').info('Current transaction already processed. Finishing processing')
            break

        if new_last_tx_id is None:  # if last seen transaction not defined, this will be as last seen
            logging.getLogger('data_loading').debug('New last seen transaction id "%s"', tx_id)
            new_last_tx_id = tx_id

        # we do not interesting in information without receiver data and we do not save any data from it
        if not isinstance(tx, ExchangeTx):
            continue

        # save transaction
        session.add(tx)

        session.commit()  # here we save data without "batch saving"

        logging.getLogger('data_loading').info('Transaction created and saved with id %d', tx.id)
    else:
        logging.getLogger('data_loading').info('There is no new data. Finishing processing')

    # saving new last seen transaction id if it calculated
    if new_last_tx_id:
        new_last_tx = LastSeenTransaction(tx_id=new_last_tx_id, address=address)
        session.add(new_last_tx)

    session.flush()
