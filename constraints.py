def funcao_objetivo(model):
  return (
      sum(model.c[k,i,j] * model.x[k,i,j] for k in model.M for i in model.I for j in model.J)
  )
  
def restricaoVisitarTodos(model, j, k):
    p = j+1
    return (
        sum(model.x[k,i,p] for i in model.I if i!=p) == model.z[k]
    )

def restricaoDeFluxoParaRotaDeVeiculo(model, h, k):
    p = h+1
    return (
        sum(model.x[k,i,p] for i in model.I if i != p) - sum(model.x[k,p,j] for j in model.J if j != p) == 0
    )

def restricaoDeveSairDoDeposito(model, k):
    return (
        sum(model.x[k,1,j+1] for j in model.Vlin) == model.z[k]
    )

def restricaoDeveRetornarAoDeposito(model, k):
    return (
        sum(model.x[k,i+1,1] for i in model.Vlin) == model.z[k]
    )

def restricaoFluxoDeCapacidade(model, j):
    p = j+1
    return (
        sum(model.y[i,p] for i in model.I) - sum(model.y[p,h] for h in model.J) == model.q[p]
    )

def restricaoLimiteInferior(model, i, j, k):
    if i != j:
        return (
            (model.q[j] * model.x[k,i,j]) <= model.y[i,j]
        )
    else: # :?
        return (
            model.y[i,j] >= 0
        )

def restricaoLimiteSuperior(model, i, j, k):
    if i != j:
        return (
            model.y[i,j] <= (model.Q[k] - model.q[i]) * model.x[k,i,j]
        )
    else:
        return model.x[k,i,j] == 0 # i = j entao nao deve existir caminho