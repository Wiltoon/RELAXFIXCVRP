import pandas as pd
from delivery import Pedido
from scipy.spatial import distance_matrix

class EntradasImportantes:
    def __init__(self, nomearquivo, num_veiculos, capacidade_dos_veiculos, num_pontos):
        self.nomearquivo = nomearquivo
        self.num_veiculos = num_veiculos
        self.capacidade_dos_veiculos = capacidade_dos_veiculos
        self.n = num_pontos
        self.df = pd.read_csv(nomearquivo)
        self.deposit = Pedido(
            0,
            self.df['XCOORD.'][0],
            self.df['YCOORD.'][0],
            0)
        self.coordenadas_x_pedidos = self.df['XCOORD.'][0:101]
        self.coordenadas_y_pedidos = self.df['YCOORD.'][0:101]
        self.pedidos = []
        self.coordenadas = []
        self.cargapedidos = []
        self.number = []
        for i in range(self.n):
            pedido = Pedido(
                self.df['CUSTOMER CUST NO.'][i], 
                self.df['XCOORD.'][i], 
                self.df['YCOORD.'][i], 
                self.df[' DEMAND'][i]
            )
            self.pedidos.append(pedido)
        for i in range(self.n):
            self.coordenadas.append([self.pedidos[i].x,self.pedidos[i].y])
            self.number.append(self.pedidos[i].num)
            self.cargapedidos.append(self.pedidos[i].cargapedido)
        novaTabela = pd.DataFrame(self.coordenadas, columns=['xcoord', 'ycoord'], index=self.number)
        matriz_distancia = pd.DataFrame(
            distance_matrix(novaTabela.values, novaTabela.values), 
            index=novaTabela.index, 
            columns=novaTabela.index
            )
        self.Q = capacidade_dos_veiculos
        self.custo_k = matriz_distancia
        # for i in range(num_veiculos):
        #     self.Q.append(capacidade_dos_veiculos)
            # self.custo_k.append(matriz_distancia)
