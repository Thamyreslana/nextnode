"""
NextNode - Tabela de frete (SIMULADA)

O primeiro dígito do CEP indica a região do Brasil. Os valores e prazos
abaixo são fictícios, apenas para o projeto de estudo. Uma loja real
consultaria a API dos Correios ou de uma transportadora.
"""

FREE_SHIPPING_FROM = 500.00  # frete econômico grátis a partir deste subtotal

SHIPPING_REGIONS = {
    0: {"name": "Grande São Paulo",          "price": 19.90, "days": 2},
    1: {"name": "Interior de SP",            "price": 24.90, "days": 3},
    2: {"name": "RJ e ES",                   "price": 29.90, "days": 4},
    3: {"name": "Minas Gerais",              "price": 29.90, "days": 4},
    4: {"name": "BA e SE",                   "price": 44.90, "days": 7},
    5: {"name": "PE, AL, PB e RN",           "price": 49.90, "days": 8},
    6: {"name": "Norte, CE, PI e MA",        "price": 64.90, "days": 10},
    7: {"name": "Centro-Oeste, TO e RO",     "price": 39.90, "days": 6},
    8: {"name": "PR e SC",                   "price": 29.90, "days": 4},
    9: {"name": "Rio Grande do Sul",         "price": 34.90, "days": 5},
}
