from docplex.mp.model import Model
from instance import EntradasImportantes
from docplex.mp.relax_linear import LinearRelaxer
from modelCVRP import *

def modelRelaxFix(namefile,num_veiculos,capacidade,n,tempo_execution):
    dados = EntradasImportantes(
        nomearquivo=namefile, 
        num_veiculos=num_veiculos, 
        capacidade_dos_veiculos=capacidade, 
        num_pontos=n
    )
    model, A, N, V, x, u, q, Q = createModel(
        inputs = dados
    )
    model_relax = relaxAllX(model, N)
    result, x, A = solve_relax_fix_each_client(model_relax, N, x)
    printResults(
        solution = result, 
        model = model_relax, 
        entrada = dados,
        A = A,
        x = x
    )
    return model_relax, result, dados, A, x 


def relaxAllX(model:Model, N):
    variables = []
    for i in range(len(N)):
        for j in range(len(N)):
            variable = 'x_'+str(i)+'_'+str(j)
            variables.append(variable)
    return alterVariablesTo(model,variables,model.continuous_vartype)

def solve_relax_fix_each_client(mdl_relax: Model, N: int, x):
    visitados = []
    visitar = [0]
    t = 0
    while(len(visitados) <= len(N)):
        destinatarios = []
        variables = []
        # Selecionar o conjunto inteiro
        for d in range(len(visitar)):
            for j in range(len(N)):
                variable = 'x_'+str(visitar[d])+'_'+str(j)
                variables.append(variable)
        model = transformVariablesToBinary(mdl_relax, variables)
        # for ct in model.iter_variables():
        #     print("Aque -> " + ct)
        # print("NADA?")
        result = solve(model,10)
        # Fixar variaveis
        for check in range(len(visitar)):            
            for j in range(len(N)):
                if(j != visitar[check]):
                    if model.x[(visitar[check],j)].solution_value >= 0.9:
                        fix(model.x[(visitar[check],j)])
                        visitado = 0
                        for it in range(len(visitados)):
                            if visitados[it] == j:
                                visitado = 1
                        if visitado == 0:
                            destinatarios.append(j)
                    else:
                        fix(x[(visitar[check],j)])
        visitar = destinatarios.copy()
    return result

def transformVariablesToBinary(mdl: Model, variables):
    mdl_rlx = alterVariablesTo(mdl, variables, mdl.binary_vartype)
    return mdl_rlx

def fix(x):
    fixToValue(x,x.solution_value)

def fixToValue(x,value):
    fixer = value
    x.lb(fixer)
    x.ub(fixer)