from sqlalchemy import desc

from katalyst_exchange import session, data_loading_log
from katalyst_exchange.models import ExchangeTx, LastSeenTransaction


def load_txs(fnc, address):
    data_loading_log.info('Trying to get transactions for "%s" with "%s"', address, fnc.__name__)

    # получаем данные от транзакциях из блокчейна
    txs = fnc(address)

    # "вспоминаем" последнюю транзакцию, с которой мы работали
    last_tx_id = session.query(LastSeenTransaction.tx_id) \
        .filter(LastSeenTransaction.address == address) \
        .order_by(desc(LastSeenTransaction.id)) \
        .group_by(LastSeenTransaction.address) \
        .scalar()

    data_loading_log.debug('Last seen transaction id "%s"', last_tx_id)

    new_last_tx_id = None

    for tx in txs:  # проходимся по транзакциям

        # Если мы дошли до транзакции, которая у нас отмечена последней обработанной,
        # значит новых транзакций для нас нету.
        tx_id = tx.income_tx_id if isinstance(tx, ExchangeTx) else tx

        data_loading_log.info('Processing tx "%s"', tx_id)

        # если первая полученная транзакция у нас сохранена, как последняя выполненная, значит нового ничего нету
        if tx_id == last_tx_id:
            data_loading_log.debug('Current tx already processed, finishing')
            break

        if new_last_tx_id is None:  # если последняя транзакция не определена, выставляем её первой
            data_loading_log.debug('New last seen tx is "%s"', tx_id)
            new_last_tx_id = tx_id

        # если итерируемое не является объектом транзакции, то нас эти данные не интересуют
        if not isinstance(tx, ExchangeTx):
            continue

        # работаем с транзакцией
        session.add(tx)

        # сохраняем
        session.commit()

        data_loading_log.debug('Transaction recorded %d', tx.id)
    else:
        data_loading_log.info('There is no new transactions')

    # если последняя транзакция определена, то "запоминаем" её
    if new_last_tx_id:
        new_last_tx = LastSeenTransaction(tx_id=new_last_tx_id, address=address)
        session.add(new_last_tx)

    session.flush()
