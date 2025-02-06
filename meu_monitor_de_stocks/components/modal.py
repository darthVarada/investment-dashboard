from dash import dcc, Input, Output, State, no_update, callback_context
import dash_bootstrap_components as dbc
from datetime import date

from app import *

layout = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Cadastro de Ativos"), class_name='modal_header'),
    dbc.ModalBody([
       dbc.Row([
           dbc.Col([
               dbc.Input(id="nome_ativo", placeholder="Nome", type='text')
           ]),
           dbc.Col([
               dbc.Input(id="preco_ativo", placeholder="preço (R$)", type='number', min=0, step=0.01)
           ]),
       ]),
       dbc.Row([
           dbc.Col([
               "Data:   ",
               dcc.DatePickerSingle(
                id='data_ativo',
                className='dbc',
                min_date_allowed=date(2005, 12, 31),
                max_date_allowed=date.today(),
                initial_visible_month=date.today(),
                date=date.today()
               ),
           ], xs=6, md=6),
           dbc.Col([
               dbc.Input(id="quantidade_ativo", placeholder="Quantidade", type='number', min=0, step=1),
           ], xs=6, md=6)
       ],style={'margin-top' : '1rem'}),
       dbc.Row([
           dbc.Col([
               dbc.RadioItems(id="compra_venda_radio", options=[{"label": "Compra", "value": 'Compra'}, {"label": "Venda", "value": 'Venda'}], value='Compra', labelCheckedClassName="text-success", inputCheckedClassName="border border-success bg-success"),
           ], style={'margin-top' : '1rem'})
       ]),
    ], class_name='modal_body'),
    dbc.ModalFooter([
        dbc.Row([
            dbc.Col([
                dbc.Button("Salvar", id="submit_cadastro"),
            ])
        ])
    ], class_name='modal_footer')    
], id="modal", size="lg", is_open=False, centered=True)


@app.callback(
    Output("submit_cadastro", "children"),
    Input("submit_cadastro", "n_clicks"),
    Input("add_button", "n_clicks"),
)
def cadastra_ativo(n, n2):
    trigg_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if trigg_id == 'submit_cadastro':
        return[dbc.Spinner(size="sm"), " Processando registro"]
    elif trigg_id == 'add_button':
        return "Salvar"
    else:
        return no_update