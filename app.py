# crear clases con el nombre de los exchanges colocando los campos necesarios
# Agregar variables a los metodos de la clase para que se puedan reutilizar
# Las tasas anualizadas se guardarán en un CSV
# En caso de no querer el CVS cambiar el booleano a  FALSE en guardar_csv
# app.py (versión refactorizada)

from clases import Exchange
from field_maps import okx_fields, binance_fields
from calculos import calcular_tasa_anualizada


def procesar_exchange(config):
    """
    Procesa un exchange completo: obtiene datos, calcula tasas y guarda el CSV.
    """
    nombre = config["nombre"]
    print(f"\n--- Procesando {nombre} ---")

    exchange = Exchange(
        nombre,
        config["url_vencimientos"],
        config["url_spot"],
        config["url_futuros"],
        config["fields"]
    )

    found_futures = exchange.get_symbols()
    if not found_futures:
        print(f"No se encontraron futuros para {nombre}. Saltando...")
        return

    futuros_precios = exchange.get_futuros(found_futures=found_futures)
    spot_precios = exchange.get_spot()

    calcular_tasa_anualizada(
        found_futures,
        futuros_precios,
        spot_precios,
        guardar_csv=True,
        nombre_csv=config["nombre_csv"]
    )


if __name__ == "__main__":
    exchanges_a_procesar = [
        {
            "nombre": "OKX",
            "url_vencimientos": "https://www.okx.com/api/v5/public/instruments?instType=FUTURES",
            "url_spot": "https://www.okx.com/api/v5/market/tickers?instType=SPOT",
            "url_futuros": "https://www.okx.com/api/v5/market/tickers?instType=FUTURES",
            "fields": okx_fields,
            "nombre_csv": "okx_tasas.csv"
        },
        {
            "nombre": "Binance",
            "url_vencimientos": "https://dapi.binance.com/dapi/v1/exchangeInfo",
            "url_spot": "https://api.binance.com/api/v3/ticker/price",
            "url_futuros": "https://dapi.binance.com/dapi/v1/ticker/price",
            "fields": binance_fields,
            "nombre_csv": "binance_tasas.csv"
        }
    ]

    for config in exchanges_a_procesar:
        procesar_exchange(config)

    print("\n--- Procesamiento finalizado ---")
