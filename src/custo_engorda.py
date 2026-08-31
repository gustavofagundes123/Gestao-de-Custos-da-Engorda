def calcular_custo_por_kg(custo_total, peso_inicial, peso_final):
    ganho_de_peso = peso_final - peso_inicial

    if ganho_de_peso <= 0:
        return 0

    return custo_total / ganho_de_peso


custo_total = 1500.00
peso_inicial = 300.00
peso_final = 450.00

custo_por_kg = calcular_custo_por_kg(
    custo_total,
    peso_inicial,
    peso_final
)

print(f"Custo por kg produzido: R$ {custo_por_kg:.2f}")