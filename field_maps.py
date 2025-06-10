from validadores import validador_binance, validador_okx

# Revisar las respuestas de las APIs para completar  los campos demanera correcta
# Importar los validadores específicos para cada exchange


# Binance
binance_fields = {
    "root": "symbols",
    "type": "contractType",
    "symbol": "symbol",
    "pair": "pair",
    "alias": "contractType",
    "expTime": "deliveryDate",
    "validar": validador_binance,
    "precios_root": None,  # La respuesta de precios es una lista
    "precios_symbol": "symbol",
    "precios_price": "price",
    "spot_root": None,     # Binance spot también es una lista directa
    "spot_symbol": "symbol",
    "spot_price": "price"
}

# OKX
okx_fields = {
    "root": "data",  # Los símbolos de instrumentos están en 'data'
    "type": "instType",
    "symbol": "instId",
    "pair": "instFamily",  # OKX usa instFamily para el par (ej: BTC-USD)
    "alias": "alias",
    "expTime": "expTime",
    "validar": validador_okx,
    "precios_root": "data",  # La respuesta de precios de futuros está en 'data'
    "precios_symbol": "instId",
    "precios_price": "last",
    "spot_root": "data",     # La respuesta de precios spot está en 'data'
    "spot_symbol": "instId",
    "spot_price": "last"
}
