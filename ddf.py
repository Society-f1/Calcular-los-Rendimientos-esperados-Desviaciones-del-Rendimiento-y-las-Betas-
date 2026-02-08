from flask import Flask, render_template
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

def calcular_analisis():
    tickers = ['AAPL', 'JPM', 'KO', 'XOM', 'AMZN', '^GSPC']
    
    # Descargamos datos (con auto_adjust para evitar errores de nombres de columnas)
    try:
        data = yf.download(tickers, period="5y", interval="1mo", auto_adjust=True)
        
        # Manejo de estructura de columnas de yfinance
        if 'Close' in data.columns:
            df_close = data['Close']
        else:
            df_close = data
            
        returns = df_close.pct_change().dropna()
        
        if '^GSPC' not in returns.columns:
            return None, "No se pudo obtener el índice S&P 500"

        # Cálculos
        exp_returns = returns.mean() * 12
        volatility = returns.std() * np.sqrt(12)
        market_var = returns['^GSPC'].var()

        resultados = []
        for stock in tickers:
            beta = returns[stock].cov(returns['^GSPC']) / market_var
            resultados.append({
                "ticker": stock,
                "retorno": f"{exp_returns[stock]:.2%}",
                "volatilidad": f"{volatility[stock]:.2%}",
                "beta": round(beta, 4),
                "clase": "table-primary" if stock == '^GSPC' else ""
            })
            
        return resultados, None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    datos, error = calcular_analisis()
    return render_template('index.html', datos=datos, error=error)

if __name__ == '__main__':
    app.run(debug=True)