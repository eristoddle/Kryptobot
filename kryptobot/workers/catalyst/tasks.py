from catalyst import run_algorithm
# from catalyst.utils.run_algo import _run
from catalyst.exchange.exchange_bundle import ExchangeBundle
import importlib
import pandas as pd
from celery import chain
from .celery import app
from ..base_task import BaseTask


@app.on_after_configure.connect
def load_open_strategies(sender, **kwargs):
    return 'load_open_strategies not implemented yet'


@app.task(base=BaseTask)
def schedule_catalyst_strategy(params):
    params.pop('strategy_id', None)
    params.pop('portfolio_id', None)
    params.pop('config', None)
    params.pop('type', None)
    ingest = params.pop('ingest', None)
    strategy = params.pop('strategy', None)
    mod = importlib.import_module('kryptobot.strategies.catalyst.' + strategy)
    params['start'] = pd.to_datetime(params['start'], utc=True)
    params['end'] = pd.to_datetime(params['end'], utc=True)
    params['handle_data'] = mod.handle_data
    params['initialize'] = mod.initialize
    # params['analyze'] = mod.analyze
    try:
        run_algorithm(**params)
    except:
        ingest['data_frequency'] = params['data_frequency']
        ingest['include_symbols'] = ingest['purchase_currency'] + '_' + params['base_currency']
        ingest['exchange_name'] = params['exchange_name']
        ingest.pop('purchase_currency', None)
        chain(schedule_catalyst_ingest(**ingest) | run_algorithm(**params))()
    # _run(
    #     initialize=None,
    #     handle_data=None,
    #     before_trading_start=None,
    #     analyze=None,
    #     algofile=algofile,
    #     algotext=algotext,
    #     defines=define,
    #     data_frequency=None,
    #     capital_base=capital_base,
    #     data=None,
    #     bundle=None,
    #     bundle_timestamp=None,
    #     start=start,
    #     end=end,
    #     output=output,
    #     print_algo=print_algo,
    #     local_namespace=local_namespace,
    #     environ=os.environ,
    #     live=True,
    #     exchange=exchange_name,
    #     algo_namespace=algo_namespace,
    #     quote_currency=quote_currency,
    #     live_graph=live_graph,
    #     analyze_live=None,
    #     simulate_orders=simulate_orders,
    #     auth_aliases=auth_aliases,
    #     stats_output=None,
    # )


@app.task(base=BaseTask)
def schedule_catalyst_ingest(exchange_name, include_symbols, data_frequency):
    exchange_bundle = ExchangeBundle(exchange_name)
    exchange_bundle.ingest(
        data_frequency=data_frequency,
        include_symbols=include_symbols,
        # exclude_symbols=params['exclude_symbols'],
        # start=start,
        # end=end,
        # show_progress=params['show_progress'],
        # show_breakdown=params['show_breakdown'],
        # show_report=params['show_report'],
        # csv=params['csv']
    )
