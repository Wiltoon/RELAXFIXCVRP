from instance import EntradasImportantes
from modelCVRP import *

def main():
    dados = EntradasImportantes(
        nomearquivo='c101.csv', 
        num_veiculos=10, 
        capacidade_dos_veiculos=200, 
        num_pontos=25
    )
    modelo = createModel(
        inputs=dados
    )
    result = solve(
        mdl=modelo
    )
    printResults(
        solution = result, 
        model = modelo, 
        entrada = dados
    )

if __name__ == '__main__':
    main()