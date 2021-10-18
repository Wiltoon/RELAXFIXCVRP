from RELAXFIXCVRP.modelCVRP import alterVariablesTo

from docplex.mp.model import Model

def solve_relax_fix_each_client(mdl_relax: Model, N):
    visitados = []
    visitar = [0]
    t = 0
    while(len(visitados) <= N):
        destinatarios = []
        variables = []
        # Selecionar o conjunto inteiro
        for d in range(len(visitar)):
            for j in range(N):
                variable = 'x_'+visitar[d]+'_'+j
                variables.append(variable)
        model = transformVariablesToBinary(mdl_relax, variables)
        result = model.solve(log_output=True)
        # Fixar variaveis
        for check in range(len(visitar)):            
            for j in range(N):
                if x[visitar[check]][j]:
                    x[visitar[check]][j].fix(1,1)
                    visitado = 0
                    for it in range(len(visitados)):
                        if visitados[it] == j:
                            visitado = 1
                    if visitado == 0:
                        destinatarios.append(j)
                else:
                    x[visitar[check]][j].fix(0,0)
        visitar = destinatarios.copy()

def transformVariablesToBinary(mdl: Model, variables):
    mdl_rlx = alterVariablesTo(mdl, variables, mdl.binary_vartype)
    return mdl_rlx