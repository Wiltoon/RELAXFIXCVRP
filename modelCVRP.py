import pandas as pd
import io
import matplotlib.pyplot as plt
from docplex.mp.model import Model
from docplex.mp.relax_linear import LinearRelaxer

import numpy as np

from docplex.mp.model import Model

from constraints import * 
from instance import EntradasImportantes

def createModel(inputs):
    model = Model('CVRP')
    A, N, V = createIndex(model, inputs)
    Q = inputs.Q
    x,u = createVariables(model, inputs, A, N, Q)
    createObjectiveFunction(model, inputs, x, A)
    q = {i: inputs.cargapedidos[i] for i in N}
    print(q)
    createConstraints(model, x, u, q, A, N, V, Q)
    return model, A, N, V, x, u, q, Q

def solve(mdl, tempo):
    mdl.parameters.timelimit = tempo
    return mdl.solve(log_output=True)
    # opt = SolverFactory(solver)
    # return opt.solve(model)
    
def createIndex(model, inputs):
    N = [i for i in range(1, inputs.n)]
    V = [0] + N
    A = [(i,j) for i in V for j in V if i != j]
    return A, N, V
    # model.I = pyo.RangeSet(inputs.n)
    # model.J = pyo.RangeSet(inputs.n)
    # model.H = pyo.RangeSet(inputs.n)
    # model.Vlin = pyo.RangeSet((inputs.n - 1))
    # model.M = pyo.RangeSet(inputs.num_veiculos)

def createParams(model, inputs):
    model.c = pyo.Param(model.M, model.I, model.J, initialize = lambda model, k, i, j: inputs.custo_k[k-1][i-1][j-1])
    model.Q = pyo.Param(model.M, initialize = lambda model, k : inputs.Q[k-1]) 
    model.q = pyo.Param(model.I, initialize = lambda model, i : inputs.cargapedidos[i-1])   
    

def createVariables(mdl, inputs, A, N, Q):
    x = mdl.binary_var_dict(A, name='x')
    u = mdl.continuous_var_dict(N, ub=Q, name='u')
    return x,u
    # model.z = pyo.Var(model.M, within = pyo.Binary)
    # model.x = pyo.Var(model.M, model.I, model.J, within= pyo.Binary)
    # model.y = pyo.Var(model.I, model.J, within=pyo.NonNegativeIntegers, bounds=(0,inputs.capacidade_dos_veiculos))

def createObjectiveFunction(model, entrada, x, A):
    c = {(i, j): np.hypot(entrada.pedidos[i].x-entrada.pedidos[j].x, entrada.pedidos[i].y-entrada.pedidos[j].y) for i, j in A}
    model.minimize(model.sum(c[i,j]*x[i,j] for i,j in A))

def createConstraints(mdl, x, u, q, A, N, V, Q):
    mdl.add_constraints(mdl.sum(x[i, j] for j in V if j != i) == 1 for i in N)
    mdl.add_constraints(mdl.sum(x[i, j] for i in V if i != j) == 1 for j in N)
    mdl.add_indicator_constraints(
        mdl.indicator_constraint(x[i, j], u[i]+q[j] == u[j]) for i, j in A if i != 0 and j != 0)
    mdl.add_constraints(u[i] >= q[i] for i in N)


def printResults(solution, model, entrada, A, x):
    # print('Valor objetivo =', model.obj())
    solution.solve_status
    active_arcs = [a for a in A if x[a].solution_value > 0.9]
    plt.figure(figsize=(15,15))
    plt.scatter(entrada.deposit.x, entrada.deposit.y, marker='s', color='r')
    plt.scatter(entrada.coordenadas_x_pedidos, entrada.coordenadas_y_pedidos)
    for i, j in active_arcs:
        plt.plot([entrada.coordenadas_x_pedidos[i], entrada.coordenadas_x_pedidos[j]], [entrada.coordenadas_y_pedidos[i], entrada.coordenadas_y_pedidos[j]], c='g', alpha=0.3)
    plt.show()
    # model.pprint()
    # for k in model.M:
    #     for i in model.I:
    #         for j in model.J:
    #             if model.x[k,i,j].value == 1:
    #                 print(k,i,j, '----', model.x[k,i,j].value)
    # print('Valor objetivo =', model.obj())
    # for k in range(entrada.num_veiculos):
    #     rotaX = []
    #     rotaY = []
    #     for i in range(entrada.n):
    #         for j in range(entrada.n):
    #             if model.x[k,i,j] == True:
    #                 rotaX.append(entrada.pedidos[i].x)
    #                 rotaY.append(entrada.pedidos[i].y)
    #                 rotaX.append(entrada.pedidos[j].x)
    #                 rotaY.append(entrada.pedidos[j].y)
    #     plt.plot(rotaX,rotaY)
def alterVariablesFor(mdl, variables, type_wish):
    relaxed_model = mdl.copy()
    mdl_class = mdl.__class__
    relax_model_name = 'rlx_'+mdl.name
    relaxed_model = mdl_class(name=relax_model_name)
    # transfer variable containers
    ctn_map = {}
    for ctn in mdl.iter_var_containers():
        copied_ctn = ctn.copy_relaxed(relaxed_model)
        ctn_map[ctn] = copied_ctn
    # transfer variables    
    
    var_mapping = {}
    for v in mdl.iter_variables():
        if v.name in variables:
            rx_lb = v.lb
            copied_var = relaxed_model._var(type_wish, rx_lb, v.ub, v.name)
            var_ctn = v.container
            if var_ctn:
                copied_ctn = ctn_map.get(var_ctn)
                assert copied_ctn is not None
                copied_var.container = copied_ctn
            var_mapping[v] = copied_var
        else:
            copied_var = relaxed_model._var(v._vartype, v.lb, v.ub, v.name)
            var_ctn = v.container
            if var_ctn:
                copied_ctn = ctn_map.get(var_ctn)
                assert copied_ctn is not None
                copied_var.container = copied_ctn
            var_mapping[v] = copied_var
            
    # transfer all non-logical cts
    for ct in mdl.iter_constraints():
        if not ct.is_generated():
            if ct.is_logical():
                process_unrelaxable(ct, 'logical')
            try:
                copied_ct = ct.relaxed_copy(relaxed_model, var_mapping)
                relaxed_model.add(copied_ct)
            except DocplexLinearRelaxationError as xe:
                process_unrelaxable(xe.object, xe.cause)
            except KeyError as ke:
                info('failed to relax constraint: {0}'.format(ct))
                process_unrelaxable(ct, 'key')
    # clone objective
    relaxed_model.objective_sense = mdl.objective_sense
    try:
        relaxed_model.objective_expr = mdl.objective_expr.relaxed_copy(relaxed_model, var_mapping)
    except DocplexLinearRelaxationError as xe:
        process_unrelaxable(urx_=xe.object, reason=xe.cause)
    except KeyError:
        process_unrelaxable(urx_=mdl.objective_expr, reason='objective')
    if mdl.context:
        relaxed_model.context = mdl.context.copy()
    return relaxed_model

   
def executePrinter(modelo, tempo_execution, A, dados, x):
    result = solve(
        mdl=modelo,
        tempo=tempo_execution
    )
    printResults(
        solution = result, 
        model = modelo, 
        entrada = dados,
        A = A,
        x = x
    )

def createExecutePrinter(namefile,num_veiculos,capacidade,n,tempo_execution):
    dados = EntradasImportantes(
        nomearquivo=namefile, 
        num_veiculos=num_veiculos, 
        capacidade_dos_veiculos=capacidade, 
        num_pontos=n
    )
    model, A, N, V, x, u, q, Q = createModel(
        inputs = dados
    )
    result = solve(
        mdl=model,
        tempo=tempo_execution
    )
    printResults(
        solution = result, 
        model = model, 
        entrada = dados,
        A = A,
        x = x
    )
    return model, result, dados, A, x