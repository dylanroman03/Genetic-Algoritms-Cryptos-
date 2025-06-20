import pandas as pd


def read_csv(file):
    df = pd.read_csv(f'data/{file}.csv', parse_dates=['snapped_at'])
    df = df.sort_values('snapped_at')

    df['year'] = df['snapped_at'].dt.isocalendar().year
    df['week'] = df['snapped_at'].dt.isocalendar().week

    ultimo = df['snapped_at'].max()
    print(f'Último valor de snapped_at: {ultimo}')
    eight_months = ultimo - pd.DateOffset(months=8)
    print(f'Fecha hace 8 meses: {eight_months}')
    df = df[df['snapped_at'] >= eight_months]

    # Tomar el primer registro de cada semana (año, semana)
    df_semanal = df.groupby(['year', 'week'], as_index=False).first()

    # Opcional: ordenar por fecha
    df_semanal = df_semanal.sort_values('snapped_at')

    # Guarda el resultado
    df_semanal.to_csv(f'data-8M/{file}.csv', index=False)

    print(df_semanal[['snapped_at', 'price']])


if __name__ == '__main__':
    files = ['apt-usd-max', 'bnb-usd-max', 'btc-usd-max', 'eth-usd-max',
             'sol-usd-max', 'sui-usd-max', 'wld-usd-max', 'xrp-usd-max',
             '1mbabydoge-usd-max']

    for file in files:
        print(f'Processing {file}...')
        read_csv(file)
        print(f'Finished processing {file}.\n')
