from flask import Flask, render_template
import yfinance as yf  # La herramienta para descargar datos reales de la bolsa
import pandas as pd    # Para manejar tablas de datos (DataFrames)
import numpy as np     # Para realizar cálculos matemáticos avanzados
#Descargamos las librerias de python
app = Flask(__name__)
 # PUNTO 1: Definimos las 5 acciones (AAPL, JPM, KO, XOM, AMZN) y el índice (^GSPC es el S&P 500)
def calcular_analisis():
    tickers = ['AAPL', 'JPM', 'KO', 'XOM', 'AMZN', '^GSPC']
    #Los datos son descargados de Yahoo finance
    # Descargamos datos (con auto_adjust para evitar errores de nombres de columnas)
    try:
        # PUNTO 2: Descargamos datos mensuales (interval="1mo") de los últimos 5 años (period="5y")
        # auto_adjust=True trae los precios ajustados por dividendos y splits
        data = yf.download(tickers, period="5y", interval="1mo", auto_adjust=True)
        
        # Manejo de estructura de columnas de yfinance
        # Filtramos para quedarnos solo con el precio de cierre ("Close")
        if 'Close' in data.columns:
            df_close = data['Close']
        else:
            df_close = data
             # Calculamos los rendimientos porcentuales: (Precio actual / Precio anterior) - 1
        # dropna() elimina la primera fila que queda vacía porque no tiene un mes anterior para comparar
        returns = df_close.pct_change().dropna()
        
        if '^GSPC' not in returns.columns:
            return None, "No se pudo obtener el índice S&P 500"

        # Cálculos
        # RENDIMIENTO ESPERADO:
        # Calculamos el promedio de los rendimientos mensuales y multiplicamos por 12 
        # para anualizar el resultado
        exp_returns = returns.mean() * 12
        # DESVIACIÓN (VOLATILIDAD):
        # Calculamos la desviación estándar de los rendimientos mensuales.
        # Se multiplica por la raíz cuadrada de 12 para anualizar la volatilidad.
        volatility = returns.std() * np.sqrt(12)
        # Calculamos la varianza del mercado (S&P 500) necesaria para la fórmula de la Beta
        market_var = returns['^GSPC'].var()

        resultados = []
        for stock in tickers:
             # FÓRMULA DE BETA: Covarianza(Acción, Mercado) / Varianza(Mercado)
            beta = returns[stock].cov(returns['^GSPC']) / market_var
            # Guardamos los resultados formateados para enviarlos a la página web
            resultados.append({
                "ticker": stock,
                "retorno": f"{exp_returns[stock]:.2%}", # Formato porcentaje (ej: 15.50%)
                "volatilidad": f"{volatility[stock]:.2%}",
                "beta": round(beta, 4), # Redondeamos a 4 decimales
                "clase": "table-primary" if stock == '^GSPC' else ""
            })
            
        return resultados, None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    # Llamamos a la función de cálculos
    datos, error = calcular_analisis()
    # --- CÓDIGO PARA MOSTRAR EN CONSOLA ---
    if datos:
        print("\n" + "="*60)
        print(f"{'TICKER':<10} | {'RETORNO':<12} | {'VOLATILIDAD':<12} | {'BETA':<8}")
        print("-" * 60)
        for fila in datos:
            print(f"{fila['ticker']:<10} | {fila['retorno']:<12} | {fila['volatilidad']:<12} | {fila['beta']:<8}")
        print("="*60 + "\n")
    # Enviamos los resultados al archivo 'index.html' para que el usuario los vea
    return render_template('index.html', datos=datos, error=error)
 # Arranca la aplicación en modo prueba
if __name__ == '__main__':
    app.run(debug=True)