import math

import os
from flask import Flask, render_template_string, request, redirect
from sqlalchemy import desc

from katalyst_exchange import session
from katalyst_exchange.models import ExchangeTx, ExchangeRate, LastSeenTransaction

app = Flask(__name__)

TX_TEMPLATE = """
<!doctype html>
<html lang="en">
    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

        <title>Transactions</title>
        <style>
            body { font-size: 12px; font-family: monospace; }
        </style>
    </head>
    <body>
        <nav class="text-center mt-3 mb-3">
            <a href="/" class="btn btn-primary btn-sm disabled">Transactions</a>
            <a href="/exchange-rates" class="btn btn-primary btn-sm">Exchange Rates</a>
        </nav>
        
        <h4>Last seen txs</h4>
        <table class="table">
            <thead>
                <tr>
                    <th scope="col">Tx ID</th>
                    <th scope="col">Address</th>
                </tr>
            </thead>
            <tbody>
                {% for tx in last_txs %}
                    <tr>
                        <td>{{ tx.tx_id }}</td>
                        <td>{{ tx.address }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h4>Processed txs</h4>
        <div>
            Pages: 
            {% for p in range(pages_count) %}
                {% if loop.index == current_page %}{{ loop.index }}{% else %}<a href="/?p={{ loop.index }}">{{ loop.index }}</a>{% endif %}{% if loop.index < pages_count %}, {% endif %}
            {% endfor %}
        </div>
        <table class="table">
            <thead>
                <tr>
                    <th scope="col" rowspan="2">#</th>
                    <th scope="col" rowspan="2">Date</th>
                    <th scope="col" colspan="5">Income</th>
                    <th scope="col" colspan="4">Outcome</th>
                    <th scope="col" rowspan="2">Status</th>
                    <th scope="col" rowspan="2">Status data</th>
                </tr>
                <tr>
                    <th scope="col">Tx ID</th>
                    <th scope="col">Address</th>
                    <th scope="col">Amount</th>
                    <th scope="col">Platform</th>
                    <th scope="col">E/R</th>
                    
                    <th scope="col">Tx ID</th>
                    <th scope="col">Address</th>
                    <th scope="col">Amount</th>
                    <th scope="col">E/R</th>
                </tr>
            </thead>
            <tbody>
                {% for tx in txs %}
                    <tr>
                        <th scope="row">{{ tx.id }}</th>
                        
                        <td>{{ tx.created_at }}</td>
                        
                        <td>{{ tx.income_tx_id }}</td>
                        <td>{{ tx.income_address }}</td>
                        <td>{{ tx.income_amount }}</td>
                        <td>{{ tx.income_platform }}</td>
                        <td>{{ tx.income_exchange_rate }}</td>
                        
                        <td>{{ tx.outcome_tx_id }}</td>
                        <td>{{ tx.outcome_address }}</td>
                        <td>{{ tx.outcome_amount }}</td>
                        <td>{{ tx.outcome_exchange_rate }}</td>
                        
                        <td>{{ tx.status }}</td>
                        <td>{{ tx.status_data }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
        <div>
            Pages: 
            {% for p in range(pages_count) %}
                {% if loop.index == current_page %}{{ loop.index }}{% else %}<a href="/?p={{ loop.index }}">{{ loop.index }}</a>{% endif %}{% if loop.index < pages_count %}, {% endif %}
            {% endfor %}
        </div>
    </body>
</html>
"""


@app.route('/')
def txs():
    page = request.args.get('p', 1, int)
    txs_q = session.query(ExchangeTx).order_by(desc(ExchangeTx.id))
    last_txs = session.query(LastSeenTransaction).order_by(desc(LastSeenTransaction.id)).limit(5).all()
    txs_count = txs_q.count()
    return render_template_string(TX_TEMPLATE,
                                  txs=txs_q.offset((page - 1) * 20).limit(20).all(),
                                  txs_count=txs_count,
                                  pages_count=math.ceil(txs_count / 20),
                                  current_page=page,
                                  last_txs=last_txs)


RATES_TEMPLATE = """
<!doctype html>
<html lang="en">
    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

        <title>Transactions</title>
        <style>
            body { font-size: 12px; font-family: monospace; }
        </style>
    </head>
    <body>
        <nav class="text-center mt-3 mb-3">
            <a href="/" class="btn btn-primary btn-sm">Transactions</a>
            <a href="/exchange-rates" class="btn btn-primary btn-sm disabled">Exchange Rates</a>
        </nav>
        
        <form method="post" class="mt-3 mb-3">
            <select required name="platform">
                <option value="ethereum">Ethereum</option>
                <option value="waves">Waves</option>
            </select>
            <input type="number" step=".01" required name="value" placeholder="Value">
            <button type="submit" class="b1tn btn-primary">Set</button>
        </form>

        <table class="table">
            <thead>
                <tr>
                    <th scope="col">Platform</th>
                    <th scope="col">Value</th>
                    <th scope="col">Date</th>
                </tr>
            </thead>
            <tbody>
                {% for rate in rates %}
                    <tr>
                        <td>{{ rate.platform }}</td>
                        <td>{{ rate.value }}</td>
                        <td>{{ rate.created_at }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
        
    </body>
</html>
"""


@app.route('/exchange-rates', methods=['GET', 'POST'])
def rates():

    if request.method == 'POST':
        er = ExchangeRate(platform=request.form.get('platform'), value=float(request.form.get('value')))
        session.add(er)
        session.commit()

        return redirect('/exchange-rates')

    rates = session.query(ExchangeRate).order_by(desc(ExchangeRate.id)).all()
    return render_template_string(RATES_TEMPLATE, rates=rates)


if __name__ == "__main__":
    app.run()
