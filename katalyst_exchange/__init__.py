import logging

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from katalyst_exchange.config import LOGS_PATH
from katalyst_exchange.ethereum import send_ethereum_tx
from katalyst_exchange.models import Base
from katalyst_exchange.waves import send_waves_tx

##
# Database init
##
engine = create_engine(os.getenv('DATABASE_URL'), echo=False)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

##
# Logging
##
logging.basicConfig(level=logging.DEBUG)

global_log = logging.getLogger()

tx_processing_log = logging.getLogger('tx_processing')

data_loading_log = logging.getLogger('data_loading')
data_loading_log.addHandler(logging.FileHandler(LOGS_PATH + '/tx.log'))


