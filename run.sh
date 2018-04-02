#!/usr/bin/env bash

export DATABASE_URL=sqlite:////home/nikita/Code/aoza/katalyst-exchange-worker/db.sqlite
#export DATABASE_URL=postgresql://katalyst:1234@localhost/katalyst

#python test.py
python workers.py