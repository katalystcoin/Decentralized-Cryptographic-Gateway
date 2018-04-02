import logging

from sqlalchemy import desc

from katalyst_exchange import session
from katalyst_exchange.models import ExchangeTx, LastSeenTransaction


def load_txs(fnc, address):
    logging.getLogger('data_loading').info('Trying to get transactions for "%s" with "%s"', address, fnc.__name__)

    # получаем данные от транзакциях из блокчейна
    txs = fnc(address)

    # "вспоминаем" последнюю транзакцию, с которой мы работали
    last_tx_id = session.query(LastSeenTransaction.tx_id) \
        .filter(LastSeenTransaction.address == address) \
        .order_by(desc(LastSeenTransaction.id)) \
        .group_by(LastSeenTransaction.address) \
        .scalar()

    logging.getLogger('data_loading').debug('Last seen transaction id "%s"', last_tx_id)

    new_last_tx_id = None

    for tx in txs:  # проходимся по транзакциям

        # Если мы дошли до транзакции, которая у нас отмечена последней обработанной,
        # значит новых транзакций для нас нету.
        tx_id = tx.income_tx_id if isinstance(tx, ExchangeTx) else tx

        logging.getLogger('data_loading').info('Processing tx "%s"', tx_id)

        # если первая полученная транзакция у нас сохранена, как последняя выполненная, значит нового ничего нету
        if tx_id == last_tx_id:
            logging.getLogger('data_loading').debug('Current tx already processed, finishing')
            break

        if new_last_tx_id is None:  # если последняя транзакция не определена, выставляем её первой
            logging.getLogger('data_loading').debug('New last seen tx is "%s"', tx_id)
            new_last_tx_id = tx_id

        # если итерируемое не является объектом транзакции, то нас эти данные не интересуют
        if not isinstance(tx, ExchangeTx):
            continue

        # работаем с транзакцией
        session.add(tx)

        # сохраняем
        session.commit()

        logging.getLogger('data_loading').debug('Transaction recorded %d', tx.id)
    else:
        logging.getLogger('data_loading').info('There is no new transactions')

    # если последняя транзакция определена, то "запоминаем" её
    if new_last_tx_id:
        new_last_tx = LastSeenTransaction(tx_id=new_last_tx_id, address=address)
        session.add(new_last_tx)

    session.flush()
