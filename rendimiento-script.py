# %%
import pandas as pd
import numpy as np


# def calc_efficiency(file):
#     df = pd.read_csv(f'data-8M/{file}.csv', parse_dates=['snapped_at'])
#     df = df.sort_values('snapped_at')
#     prices = df['price']
#     print(f"prices {prices}")
#
#     return prices.pct_change().dropna()


def calc_efficiency():
    df = pd.read_excel('precios_semanales.xlsx')
    efficiencies = {}

    for column in df.columns[1:]:
        prices = df[column]
        print(f"prices {prices}")
        efficiencies[column] = prices.pct_change().dropna()

    return pd.DataFrame(efficiencies)


def improve_portfolio(R_target, R, Sigma, N):
    A = np.zeros((N + 2, N + 2))
    A[:N, :N] = 2 * Sigma
    A[:N, N] = -R
    A[:N, N + 1] = -np.ones(N)
    A[N, :N] = R.T
    A[N + 1, :N] = np.ones(N)

    b = np.zeros(N + 2)
    b[N] = R_target
    b[N + 1] = 1.0

    try:
        sol = np.linalg.solve(A, b)
        X = sol[:N]
    except np.linalg.LinAlgError:
        return None, None, None

    # Proyectar pesos negativos a cero
    X = np.maximum(X, 0)
    if np.sum(X) > 1e-10:  # Evitar división por cero
        X = X / np.sum(X)
    else:
        return None, None, None

    # Calcular rendimiento y riesgo
    rendimiento = np.dot(X, R)
    riesgo = np.sqrt(np.dot(X, np.dot(Sigma, X)))

    return X, rendimiento, riesgo


if __name__ == '__main__':
    # files = ['btc-usd-max', 'apt-usd-max', 'bnb-usd-max', 'eth-usd-max',
    #          'sol-usd-max', 'sui-usd-max', 'wld-usd-max', 'xrp-usd-max',
    #          '1mbabydoge-usd-max']
    # files = ['btc-usd-max']

    r = calc_efficiency()
    # r = pd.DataFrame()
    # for file in files:
    #     print(f'Processing {file}...')
    #     efficiency = calc_efficiency_2(file)
    #     r[file.split('-')[0]] = efficiency
    #     print(f'Finished processing {file}.\n')
    #

    r = r.dropna()
    er = r.mean()
    cov_matrix = r.cov().values

    R_min = er.min()
    R_max = er.max()
    R_targets = np.linspace(R_min, R_max, 50)
    riesgos_manual = []
    rendimientos_manual = []
    pesos_manual = []

    for R_target in R_targets:
        X, rendimiento, riesgo = improve_portfolio(R_target, er, cov_matrix, len(er))
        if X is not None and not np.any(np.isnan(X)):
            rendimientos_manual.append(rendimiento)
            riesgos_manual.append(riesgo)
            pesos_manual.append(X)

    er.to_csv('expected_returns.csv')
    pd.DataFrame(cov_matrix, index=er.index, columns=er.index).to_csv('cov_matrix.csv')

    # Print results
    for i, R_target in enumerate(R_targets):
        print(f'R_target: {R_target:.4f}, Rendimiento: {rendimientos_manual[i]:.4f}, Riesgo: {riesgos_manual[i]:.4f}')
        print(f'Pesos: {pesos_manual[i]}')
