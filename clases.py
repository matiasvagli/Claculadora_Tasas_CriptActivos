# clases.py
# Clase Exchange para manejar la conexión a las APIs
# Todas las Apis usadas son publicas leer la documentación de cada exchange para más detalles

import requests
from datetime import datetime


class Exchange:
    def __init__(self, name, url_vencimientos, url_spot, url_futuros, field_map):
        self.name = name
        self.url_vencimientos = url_vencimientos
        self.url_spot = url_spot
        self.url_futuros = url_futuros
        self.field_map = field_map
        self.pares_disponibles = set()  # Almacena los pares base 
        
    def get_symbols(self):
        print(f"Conectando a {self.name} Obteniendo símbolos de futuros")

        try:
            response = requests.get(self.url_vencimientos)
            response.raise_for_status()
            data = response.json()

            found_futures = []
            pares_base = set()
            print("Conexión exitosa. Recolectando datos de futuros...")
            symbols_data = data.get(self.field_map.get("root", ""), [])
            if not symbols_data and self.field_map.get("root"):
                symbols_data = data

            for symbol_info in symbols_data:
                inst_type = symbol_info.get(self.field_map["type"])
                symbol = symbol_info.get(self.field_map["symbol"])
                pair = symbol_info.get(self.field_map["pair"])
                alias = symbol_info.get(self.field_map.get("alias", ""), "")
                exp_time = symbol_info.get(self.field_map.get("expTime", ""))

                if self.field_map["validar"](inst_type, alias, exp_time):
                    try:
                        fecha = datetime.fromtimestamp(int(exp_time) / 1000)
                    except (ValueError, TypeError):
                        fecha = "Fecha inválida"

                    found_futures.append({
                        "Símbolo": symbol,
                        "Par": pair,
                        "Tipo de Contrato": alias,
                        "Fecha de Vencimiento": fecha.strftime('%Y-%m-%d %H:%M:%S UTC') if isinstance(fecha, datetime) else fecha
                    })
                    # Guardar el par base (ej: BTC de BTC-USDT, ETH de ETH-USDT)
                    if pair:
                        if '-' in pair:
                            base_currency = pair.split('-')[0].upper()
                            pares_base.add(base_currency)
                        elif pair.endswith("USDT") or pair.endswith("USD"):
                            base_currency = pair.replace(
                                "USDT", "").replace("USD", "").upper()
                            pares_base.add(base_currency)

            self.pares_disponibles = pares_base
            # print(f"Pares base disponibles en {self.name}: {self.pares_disponibles}") # Para depuración

            print("Contratos encontrados:")
            print("-" * 60)
            """ for f in found_futures:
                print(f"   Símbolo: {f['Símbolo']}")
                print(f"   Par: {f['Par']}")
                print(f"   Tipo de Contrato: {f['Tipo de Contrato']}")
                print(f"   Fecha de Vencimiento: {f['Fecha de Vencimiento']}")
                print("-" * 80) """

            return found_futures

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con la API de {self.name}: {e}")
            return []
        except Exception as e:
            print(f"Error en {self.name} al obtener símbolos: {e}")
            return []

    def get_futuros(self, found_futures):
        print(
            f"Intentando conectar a la API de {self.name} para obtener precios de futuros")

        try:
            response = requests.get(self.url_futuros)
            response.raise_for_status()
            data = response.json()

            print("Conexión exitosa. Analizando datos de futuros...")

            print("Recolenctando precios de futuros...")
            print("-" * 60)

            precios_futuros = []

            precios_root = self.field_map.get("precios_root")
            precios_data = data.get(precios_root, []) if precios_root else data

            precios_symbol = self.field_map.get("precios_symbol", "symbol")
            precios_price = self.field_map.get("precios_price", "price")

            precios_dict = {}
            for item in precios_data:
                symbol = item.get(precios_symbol)
                price = item.get(precios_price)
                if symbol and price:
                    precios_dict[symbol] = price

            for futuro in found_futures:
                simbolo = futuro['Símbolo']
                if simbolo in precios_dict:
                    precios_futuros.append({
                        "Símbolo": simbolo,
                        "Precio Actual": precios_dict[simbolo]
                    })

            if precios_futuros:
                print("Precios de futuros encontrados:")
                print("-" * 60)
                for precio in precios_futuros:
                    """ print(f"   Símbolo: {precio['Símbolo']}")
                    print(f"   Precio Actual: {precio['Precio Actual']}")
                    print("-" * 50) """
            else:
                print("No se encontraron precios para los futuros especificados.")
            return precios_futuros
        except requests.exceptions.RequestException as e:
            print(
                f"Error al conectar con la API de {self.name} para futuros: {e}")
            return []
        except Exception as e:
            print(
                f"Ocurrió un error inesperado al obtener precios de futuros: {e}")
            return []

    def get_spot(self):
        """
        Obtiene los precios spot actuales solo de los pares seleccionados contra USDT o USD.
        Devuelve una lista de diccionarios con los precios encontrados.
        """
        print(f"Conectando a {self.name} para precios spot")

        print("Coneccion exitosa. Recolenctando datos de precios spot...")

        # Función auxiliar para normalizar los símbolos para comparación

        def normaliza_par_spot(par):
            if not par:
                return ""
            # Esto convierte BTCUSDT, BTC-USDT, BTC_USDT a BTCUSDT
            # y BTCUSD, BTC-USD a BTCUSD
            par = par.upper()
            if par.endswith("USDT"):
                return par.replace("-", "").replace("_", "")
            elif par.endswith("USD"):
                return par.replace("-", "").replace("_", "")
            return par

        try:
            response = requests.get(self.url_spot)
            response.raise_for_status()
            data = response.json()

            precios_root = self.field_map.get("spot_root")
            precios_data = data.get(precios_root, []) if precios_root else data

            precios_symbol = self.field_map.get("spot_symbol", "symbol")
            precios_price = self.field_map.get("spot_price", "price")

            pares_base_interes = self.pares_disponibles

            precios_spot = []
            for item in precios_data:
                if not isinstance(item, dict):
                    continue
                symbol = item.get(precios_symbol)
                price = item.get(precios_price)

                if symbol and price:
                    # Normalizar el símbolo spot para la comparación
                    symbol_norm = normaliza_par_spot(symbol)

                    # Verificar si el símbolo spot normalizado corresponde a un par base de interés
                    for base in pares_base_interes:
                        expected_usdt = normaliza_par_spot(base + "USDT")
                        expected_usd = normaliza_par_spot(
                            base + "USD")  # Para OKX que usa USD

                        if symbol_norm == expected_usdt or symbol_norm == expected_usd:
                            precios_spot.append({
                                "Símbolo": symbol,  # Mantener el símbolo original de la API
                                "SímboloNormalizado": symbol_norm,  # Símbolo normalizado para búsqueda
                                "Precio Actual": price,
                                "MonedaBase": base  # Agregar la moneda base para facilitar el mapeo
                            })
                            break  # Encontramos una coincidencia, pasamos al siguiente item

            if precios_spot:
                print("Precios  spot OK (solo pares de los futuros):")
                print("-" * 60)
                print("-" * 60)

                """ for precio in precios_spot:
                    print(f"   Símbolo: {precio['Símbolo']}")
                    print(f"   Precio Actual: {precio['Precio Actual']}")
                    print("-" * 50) """
            else:
                print("No se encontraron precios spot para los pares de futuros.")
            return precios_spot
        except requests.exceptions.RequestException as e:
            print(
                f"Error al conectar con la API de {self.name} para spot: {e}")
            return []
        except Exception as e:
            print(f"Ocurrió un error inesperado al obtener precios spot: {e}")
            return []
