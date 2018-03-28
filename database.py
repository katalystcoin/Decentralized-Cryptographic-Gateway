import logging

from sqlalchemy import func, MetaData, Table, Column, Integer, String, DateTime, Float, Text, create_engine

logging.basicConfig(level=logging.DEBUG)

engine = create_engine('sqlite:////home/nikita/Code/aoza/katalyst-exchange-worker/db.sqlite', echo=True)
# engine = create_engine('postgresql://katalyst:1234@localhost/katalyst', echo=True)
metadata = MetaData()

PLATFORM_WAVES = 'waves'
PLATFORM_ETHEREUM = 'ethereum'
STATUS_NEW = 'new'
STATUS_AWAITING_PROCESSING = 'awaiting_processing'
STATUS_DONE = 'done'
STATUS_FAILED = 'failed'
STATUS_INVALID = 'invalid'

transactions = Table('transactions', metadata,
                     Column('id', Integer, primary_key=True),

                     Column('income_tx_id', String(80)),
                     Column('income_address', String(80)),
                     Column('income_amount', Float),
                     Column('income_platform', String(20)),
                     Column('income_exchange_rate', Float),

                     Column('outcome_tx_id', String(80), nullable=True),
                     Column('outcome_address', String(80)),
                     Column('outcome_amount', Float),
                     Column('outcome_platform', String(20)),
                     Column('outcome_exchange_rate', Float),

                     Column('status', String(21), default=STATUS_NEW),
                     Column('status_data', Text, nullable=True),

                     Column('created_at', DateTime, server_default=func.now()),
                     Column('updated_at', DateTime, server_default=func.now())
                     )

last_transactions = Table('last_transactions', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('platform', String(20)),
                          Column('tx_id', String(80)),
                          Column('created_at', DateTime, server_default=func.now()),
                          )

exchange_rates = Table('exchange_rates', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('platform', String(20)),
                       Column('value', Float),
                       Column('created_at', DateTime, server_default=func.now()),
                       )

metadata.create_all(engine)

database_connection = engine.connect()
