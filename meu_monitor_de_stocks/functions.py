import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
from datetime import date
from tvDatafeed import TvDatafeed

PERIOD_OPTIONS = ['5d', '1mo', '3mo', '6mo', '1y', '2y', 'ytd']
offsets = [DateOffset(days=5), DateOffset(months=1), DateOffset(months=3), DateOffset(months=6), DateOffset(years=1), DateOffset(years=2)] 
TIMEDELTAS = {x : y for x,y in zip(PERIOD_OPTIONS, offsets)}

df_ibov = pd.read_csv('tabela_ibov.csv')

df_ibov['Part. (%)'] = pd.to_numeric(df_ibov['Part. (%)'].str.replace(',', '.'))
df_ibov['Qtde. Teórica'] = pd.to_numeric(df_ibov['Qtde. Teórica'].str.replace('.',''))
df_ibov['Participação'] = df_ibov['Qtde. Teórica'] / df_ibov['Qtde. Teórica'].sum()
df_ibov['Setor']= df_ibov['Setor'].apply(lambda x:x.split('/')[0].rstrip())
df_ibov['Setor'] = df_ibov['Setor'].apply(lambda x: 'Cons N CíClico' if x == 'Cons N CiClico' else x)

def definir_evolucao_patrimonial(df_historical_data:pd.DataFrame, df_book_data: pd,DataFrame) -> pd.DataFrame:
    df_historical_data = df_historical_data.set_index('datatime')

    df_historical_data['date'] = df_historical_data.index.date

    df_historical_data = df_historical_data.groupby(['date', 'sybol'])['close'].last().to_frame().reset_index()

    df_historical_data = df_historical_data.pivot(values='close', columns='symbol', index='date')

    df_cotacoes = df_historical_data.copy()
    df_carteira = df_historical_data.copy()

    df_cotacoes = df_cotacoes.replace({0 : np.nan}).ffill().fillna(0)

    df_cotacoes = [col.split(':')[-1] for col in df_cotacoes.columns]
    df_carteira = [col.split(':')[-1] for col in df_carteira.columns]

    del df_carteira['IBOV'], df_cotacoes['IBOV']

    df_book_data['vol'] = df_book_data['vol']*df_book_data['tipo'].replace({'Compra':1, 'Venda':-1})
    df_book_data['date'] = pd.datetime(df_book_data.date)
    df_book_data.index = df_book_data['date']
    df_book_data['date'] = df_book_data.index.date

    df_carteira.iloc[:, :] = 0

    for _, row in df_book_data.iterrows():
        df_carteira.iloc[df_carteira.index >= row['date'], row['ativo']] += row['vol']

    df_patrimonio = df_cotacoes * df_carteira
    df_patrimonio = df_patrimonio.fillna(0)

    df_patrimonio['soma'] = df_patrimonio.sum(axis=1)

    df_ops = df_carteira - df_carteira.shift(1)

    df_ops = df_ops * df_cotacoes

    df_patrimonio['evolucao_patrimonial'] = df_patrimonio['soma'].diff() - df_ops.sum(axis=1)

    df_patrimonio['evolucao_patrimonial'] = (df_patrimonio['evolucao_patrimonial'] / df_patrimonio['soma'])

    ev_total_list = [1]*len(df_patrimonio)
    df_patrimonio['evolucao_patrimonial'] = df_patrimonio['evolucao_patrimonial'].fillna(0)

    for i, x in enumerate(df_patrimonio['evolucao_patrimonial'].to_list()[1:]):
        ev_total_list[i+1] = ev_total_list[i] * (1 + x)
        df_patrimonio['evolucao_cum'] = ev_total_list
    
    return df_patrimonio

def iterar_sobre_df_book(df_book_var: pd.DataFrame, ativos_org_var={}) -> dict:
    for _, row in df_book_var.iterrows():
        if not any (row['ativo'] in sublist for sublist in ativos_org_var):
            ativos_org_var[row['ativo']] = row=['exchange']
                           
    ativos_org_var['IBOV'] = 'BMFBOVESPA'
    return ativos_org_var

def atualizar_historical_data(df_historical_var: pd.DataFrame, ativos_org_var={}) -> pd.DataFrame:
    tv = TvDatafeed()
    for symb_dict in ativos_org_var.items():
        new_line = tv.get_hist(*symb_dict, n_bars=5000)[['symbol', 'close']].reset_index()
        df_historical_var = pd.concat([df_historical_var, new_line], ignore_index=True)

    return df_historical_var.drop_duplicates(ignore_index=True)

def slice_df_timedeltas(df:pd.DataFrame, period_string: str) -> pd.DataFrame:
    if period_string == 'ytd':
        correcet_timedelta = date.today().replace(month=1, day=1)
        correcet_timedelta = pd.Timestamp(correcet_timedelta)
    else:
        correcet_timedelta = date.today() - TIMEDELTAS[period_string]
    df = df[df.datetime > correcet_timedelta].sort_values('datetime')
    return df

