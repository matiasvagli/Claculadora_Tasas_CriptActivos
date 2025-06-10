# Agregar validadores para diferentes exchanges para filtrar los futuros que nos interesan
# Validadores para filtrar los futuros según las reglas de cada exchange


def validador_okx(inst_type, alias, exp_time):
    # OKX usa "instType" y "alias". Queremos FUTURES y que no sean "perpetual"
    return inst_type == "FUTURES" and alias.lower() != "perpetual" and exp_time


def validador_binance(inst_type, alias, exp_time):
    # Binance usa "contractType". Queremos que no sea "PERPETUAL" y que tenga fecha de vencimiento.
    return inst_type not in ["PERPETUAL", "PERPETUAL DELIVERING"] and exp_time
