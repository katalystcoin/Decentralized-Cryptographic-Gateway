import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database init
engine = create_engine(os.getenv('DATABASE_URL'), echo=False)
Session = sessionmaker(bind=engine)
session = Session()

PLATFORM_ETHEREUM = 'ethereum'
PLATFORM_WAVES = 'waves'
