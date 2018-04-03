# Katalyst exchange

## Configuration

Service

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

# Configuration

# Database
Environment="DATABASE_URL=postgresql://user:password@localhost/database"

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

Timer

```ini
[Unit]
Description=Timer for Katalyst exchange worker

[Timer]
Unit=katalyst-exchange-worker.service
OnBootSec=1min
OnUnitActiveSec=1min

[Install]
WantedBy=multi-user.target
```