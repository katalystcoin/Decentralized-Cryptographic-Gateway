# Katalyst exchange


## Configuration

Main worker and management panel are working as `systemd` services. At first start database structure will be created automatically.


### Requirements

All requirements listed in `requirements.txt` file. It is recommended to use VirtualEnv.


### Systemd services

Main worker service

```ini
[Unit]
Description="Katalyst exchange worker"

After=network.target

[Service]
Type=simple

User=user
Group=group

WorkingDirectory=/opt/katalyst-exchange-worker

# Virtualenv
Environment="PATH=/opt/katalyst-exchange-worker/venv/bin"

# Database
Environment="DATABASE_URL=postgresql://user:password@localhost/database"

# Logging
Environment="LOG_LEVEL=DEBUG"
Environment="LOG_GLOBAL_FORMAT=%(asctime)s %(levelname)s %(message)s"
Environment="LOG_TX_PROCESSING_FILE=/var/log/katalyst-exchange-worker/txprocessing.log"
Environment="LOG_TX_PROCESSING_FORMAT=%(asctime)s %(levelname)s %(message)s"
Environment="LOG_DATA_LOADING_FILE=/var/log/katalyst-exchange-worker/dataloading.log"
Environment="LOG_DATA_LOADING_FORMAT=%(asctime)s %(levelname)s %(message)s"

# Ethereum
Environment="ETHEREUM_WALLET_ADDRESS="
Environment="ETHERSCAN_API_KEY="
Environment="ETHERSCAN_URL_PATTERN=https://api-rinkeby.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset=1000&sort=desc&apikey={api_key}"
Environment="ETHEREUM_NODE_URL=http://127.0.0.1:8545"

# Waves
Environment="WAVES_WALLET_ADDRESS="
Environment="WAVES_WALLET_PRIVATE_KEY="
Environment="WAVESNODES_URL_PATTERN=https://testnode3.wavesnodes.com/transactions/address/{address}/limit/1000"
Environment="WAVES_NODE_URL=http://127.0.0.1:6869"
Environment="WAVES_NODE_CHAIN=testnet"

ExecStart=/opt/katalyst-exchange-worker/venv/bin/python workers.py
KillMode=process

[Install]
WantedBy=multi-user.target
```

Main worker timer

```ini
[Unit]
Description=Timer for Katalyst exchange worker

After=network.target

[Timer]
Unit=katalyst-exchange-worker.service
OnBootSec=1min
OnUnitActiveSec=1min

[Install]
WantedBy=multi-user.target
```

Management panel

```
[Unit]
Description=Katalyst exchange worker management panel

After=network.target

[Service]
User=user
Group=group

WorkingDirectory=/opt/katalyst-exchange-worker

# Virtualenv
Environment="PATH=/opt/katalyst-exchange-worker/venv/bin"

# Database
Environment="DATABASE_URL=postgresql://user:password@localhost/database"

ExecStart=/opt/katalyst-exchange-worker/venv/bin/gunicorn --bind 0.0.0.0:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```
