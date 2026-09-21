def calcular_custo_por_kg(custo_total, peso_inicial, peso_final):
    ganho_de_peso = peso_final - peso_inicial

    if ganho_de_peso <= 0:
        return 0

    return custo_total / ganho_de_peso