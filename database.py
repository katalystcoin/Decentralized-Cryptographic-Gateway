import logging

from sqlalchemy import func, MetaData, Table, Column, Integer, String, DateTime, Float, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base

logging.basicConfig(level=logging.DEBUG)

engine = create_engine('sqlite:////home/nikita/Code/aoza/katalyst-exchange-worker/db.sqlite', echo=True)
# engine = create_engine('postgresql://katalyst:1234@localhost/katalyst', echo=True)
metadata = MetaData()

PLATFORM_WAVES = 'waves'
PLATFORM_ETHEREUM = 'ethereum'

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

Base = declarative_base()


class Tx(Base):
    STATUS_NEW = 'new'
    STATUS_AWAITING_PROCESSING = 'awaiting_processing'
    STATUS_DONE = 'done'
    STATUS_FAILED = 'failed'
    STATUS_INVALID = 'invalid'

    __tablename__ = 'transactions'

    income_tx_id = Column(String(80))
    income_address = Column(String(80))
    income_amount = Column(Float)
    income_platform = Column(String(20))
    income_exchange_rate = Column(Float)

    outcome_tx_id = Column(String(80))
    outcome_address = Column(String(80))
    outcome_amount = Column(Float)
    outcome_platform = Column(String(20))
    outcome_exchange_rate = Column(Float)

    status = Column(String(20), default=STATUS_NEW)
    status_data = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_onupdate=func.now())

    def __repr__(self):
        return "<Tx(name='%s', fullname='%s', password='%s')>" % (self.income_address,
                                                                  self.outcome_address, self.status)


Base.metadata.create_all(engine)

database_connection = engine.connect()
