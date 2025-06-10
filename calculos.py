# calculos.py

from datetime import datetime
import csv
import math


def calcular_tasa_anualizada(futuros, precios_futuros, precios_spot, guardar_csv=False, nombre_csv="tasas_anualizadas.csv"):
    """
    Calcula la tasa anualizada para cada futuro usando el precio spot del activo subyacente
    y la fecha de vencimiento.
    Imprime la tasa anualizada para cada contrato futuro.
    """
    # Crea un diccionario para acceso rápido a precios futuros por símbolo
    futuros_dict = {item['Símbolo']: float(
        item['Precio Actual']) for item in precios_futuros}

    # Crea un diccionario para acceso rápido a precios spot por moneda base
    spot_dict = {item['MonedaBase']: float(
        item['Precio Actual']) for item in precios_spot}

    resultados = []
    fecha_actual = datetime.utcnow().strftime('%Y-%m-%d')
    print("\nTasas anualizadas para cada futuro:")
    print("-" * 50)
    for futuro in futuros:
        simbolo_futuro = futuro['Símbolo']
        fecha_venc = futuro['Fecha de Vencimiento']
        precio_futuro = futuros_dict.get(simbolo_futuro)

        # --- LÓGICA MODIFICADA PARA EXTRAER MONEDA BASE (la última que corregimos) ---
        moneda_base = ""
        if '_' in simbolo_futuro:
            partes = simbolo_futuro.split('_')
            temp_base_divisa = partes[0].upper()
            if temp_base_divisa.endswith("USDT"):
                moneda_base = temp_base_divisa.replace("USDT", "")
            elif temp_base_divisa.endswith("USD"):
                moneda_base = temp_base_divisa.replace("USD", "")
            elif temp_base_divisa.endswith("USDC"):
                moneda_base = temp_base_divisa.replace("USDC", "")
            else:
                moneda_base = temp_base_divisa
        elif '-' in simbolo_futuro:
            moneda_base = simbolo_futuro.split('-')[0].upper()
        else:
            print(
                f"Advertencia: Formato de símbolo de futuro inesperado para {simbolo_futuro}. No se pudo determinar la moneda base.")
            print("-" * 50)
            continue
        moneda_base = moneda_base.strip().upper()
        # --- FIN LÓGICA MODIFICADA ---

        precio_spot = spot_dict.get(moneda_base)

        if precio_futuro is None or precio_spot is None:
            print(
                f"No se encontró precio spot o futuro para {simbolo_futuro} (base: {moneda_base})")
            print("-" * 50)
            continue
        # Calcula los días al vencimiento
        vencimiento = datetime.strptime(fecha_venc, '%Y-%m-%d %H:%M:%S UTC')
        hoy = datetime.utcnow()
        dias = (vencimiento - hoy).days + (vencimiento - hoy).seconds / 86400
        if dias <= 0:
            print(f"El contrato {simbolo_futuro} ya venció o vence hoy.")
            print("-" * 50)
            continue
        # Calcula la tasa anualizada
        tasa = ((precio_futuro / precio_spot) - 1) * (365 / dias) * 100
        print(f"Símbolo: {simbolo_futuro}")
        print(f"  Moneda base: {moneda_base}")
        print(f"  Precio Futuro: {precio_futuro}")
        print(f"  Precio Spot: {precio_spot}")
        print(f"  Días al vencimiento: {dias:.2f}")
        print(
            f"  Fecha de vencimiento: {vencimiento.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"  Tasa anualizada: {tasa:.2f}%")
        if tasa > 20:
            print("  ⚠️  ¡Tasa anualizada mayor al 20%! ⚠️")
        print("-" * 50)
        resultados.append({
            "Fecha consulta": fecha_actual,
            "Símbolo": simbolo_futuro,
            "Moneda base": moneda_base,
            "Precio Futuro": precio_futuro,
            "Precio Spot": precio_spot,
            "Días al vencimiento": math.ceil(dias),
            "Fecha de vencimiento": vencimiento.strftime('%Y-%m-%d %H:%M:%S UTC'),
            "Tasa anualizada": f"{round(tasa, 2)}%"
        })
    if guardar_csv and resultados:
        with open(nombre_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
            writer.writeheader()
            writer.writerows(resultados)
        print(f"\nResultados guardados en {nombre_csv}\n")

# Puedes agregar más funciones de cálculo aquí en el futuro
# def otra_funcion_de_calculo(...):
#     pass
