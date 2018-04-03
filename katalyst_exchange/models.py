from sqlalchemy import Column, Integer, String, DateTime, func, Float, Text, desc
from sqlalchemy.ext.declarative import declarative_base

from katalyst_exchange import session, engine
from katalyst_exchange import PLATFORM_ETHEREUM, PLATFORM_WAVES

Base = declarative_base()


class LastSeenTransaction(Base):
    """
    Last seen transaction from blockchain.
    """
    __tablename__ = 'last_seen_transactions'
    id = Column(Integer, primary_key=True)
    address = Column(String(80))
    tx_id = Column(String(80))

    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return "<LastSeenTransaction(address='%s', tx_id='%s', created_at='%s')>" % (self.address,
                                                                                     self.tx_id, self.created_at)


class ExchangeRate(Base):
    """
    Exchange rate.
    """
    __tablename__ = 'exchange_rates'
    id = Column(Integer, primary_key=True)
    platform = Column(String(20))
    value = Column(Float)

    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return "<ExchangeRate(platform='%s', value='%s', created_at='%s')>" % (self.platform,
                                                                               self.value,
                                                                               self.created_at)


class ExchangeTx(Base):
    """
    Exchange transaction.
    """
    STATUS_NEW = 'new'
    STATUS_AWAITING_PROCESSING = 'awaiting_processing'
    STATUS_DONE = 'done'
    STATUS_FAILED = 'failed'
    STATUS_INVALID = 'invalid'

    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)

    income_tx_id = Column(String(80), comment='Income transaction ID')
    income_address = Column(String(80), comment='Sender address')
    income_amount = Column(Integer, comment='Income amount')
    income_platform = Column(String(20), comment='Platform where sender walled located')
    income_exchange_rate = Column(Float, nullable=True, comment='Exchange rate to base currency (buying)')

    outcome_tx_id = Column(String(80), nullable=True, comment='Outcome transaction ID')
    outcome_address = Column(String(80), comment='Receiver address')
    outcome_amount = Column(Integer, nullable=True, comment='Outcome amount')
    outcome_platform = Column(String(20), comment='Platform where receiver walled located')
    outcome_exchange_rate = Column(Float, nullable=True, comment='Exchange rate to base currency (selling)')

    status = Column(String(20), default=STATUS_NEW, comment='Transaction status')
    status_data = Column(Text, nullable=True, comment='Mostly description for \'fail\' status')

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_onupdate=func.now())

    def __repr__(self):
        return "<ExchangeTx(id='%s', " \
               "income_address='%s', " \
               "outcome_address='%s', " \
               "income_amount='%s', " \
               "outcome_amount='%s', " \
               "status='%s')>" % (self.id,
                                  self.income_address,
                                  self.outcome_address,
                                  self.income_amount,
                                  self.outcome_amount,
                                  self.status)


def get_actual_exchange_rate(platform):
    """
    Actual exchange rate for platform.
    :param platform: Platform name
    :type platform: str
    :return: Actual exchange rate
    :rtype: ExchangeRate
    """
    assert platform in [PLATFORM_WAVES, PLATFORM_ETHEREUM]

    return session.query(ExchangeRate).filter(ExchangeRate.platform == platform) \
        .order_by(desc(ExchangeRate.id)) \
        .limit(1) \
        .one()


Base.metadata.create_all(engine)
