def calcular(a, b, operador):
    if operador == "+":
        return a + b
    if operador == "-":
        return a - b
    if operador == "*":
        return a * b
    if operador == "/":
        if b == 0:
            raise ValueError("Nao e possivel dividir por zero.")
        return a / b
    raise ValueError("Operador invalido.")


def processar_calculo(data):
    a = float(data["a"])
    b = float(data["b"])
    operador = data["operator"]
    resultado = calcular(a, b, operador)
    return f"Resultado: {a} {operador} {b} = {resultado}"
