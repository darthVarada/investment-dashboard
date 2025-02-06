from dash import dcc
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import pandas as pd

# poetry run python d:/pc/estudos/azimov/meu_monitor_de_stocks/index.py

from components import header, fixed_row, wallet, home
from functions import *
from app import app

ativo_org = {}
try:
    df_book = pd.read_csv('book_data.csv', index_col=0)
    ativo_org = iterar_sobre_df_book(df_book)
except:
    df_book = pd.DataFrame(columns=['date', 'preco', 'tipo', 'ativo', 'exchange', 'vol', 'valor_total'])

try:
    df_historical_data = pd.read_csv('historical_data.csv', index_col=0)

except:
    df_historical_data = pd.DataFrame(columns=['datetime', 'symbol', 'close'])

df_historical_data = atualizar_historical_data(df_historical_data, ativo_org)

df_historical_data = df_historical_data.to_dict()
df_book = df_book.to_dict()


app.layout = dbc.Container([
    dcc.Location(id="url"),
    dcc.Store(id='book_data_store', data=df_book, storage_type='memory'),
    dcc.Store(id='historical_data_store', data=df_historical_data, storage_type='memory'),
    dcc.Store(id='layout_data', data=[], storage_type='memory'),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    header.layout
                ], className= 'header_layout'),
            ]),
            dbc.Row([
                dbc.Col([
                    fixed_row.layout
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    
                ], id="page-content"),
            ]),
        ])
    ])
], fluid=True)


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def render_page_content(pathname):
    if pathname == '/home' or pathname == '/':
        return home.layout
    if pathname == '/wallet':
        return wallet.layout


@app.callback(
    Output('historical_data_store', 'data'),
    Input('book_data_store', 'data'),
    State('historical_data_store', 'data')
)
def atualizar_databases(book_data, historical_data):
    df_book = pd.DataFrame(book_data)
    df_historical = pd.DataFrame(historical_data)

    ativos = iterar_sobre_df_book(df_book)

    df_historical = atualizar_historical_data(df_historical, ativos)

    df_historical.to_csv('historical_data.csv')
    
    return df_historical.to_dict()

if __name__ == '__main__':
    app.run_server(debug=True)