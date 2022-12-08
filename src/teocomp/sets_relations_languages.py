from graphviz import Digraph
import ipywidgets as widgets
from IPython.display import display, Markdown
from random import randrange
import pandas as pd
from teocomp.bcolors import bcolors

# Define um novo conjunto a partir de um conjunto A obedecendo a propriedade P.
def conjunto(A,P):
  B = set()
  for a in A:
    if(P(a)):
      B.add(a)
  return B

# Para visualizar uma relação
from graphviz import Digraph
def visualiza(A1, A2, R, labelSet1="A1", labelSet2="A2"):
	g = Digraph()
	g.attr(rankdir='LR')

	with g.subgraph(name='cluster_1') as c:
		c.attr(color='blue')
		c.node_attr.update(style='filled')
		c.attr(label=labelSet1)
		for a1 in A1:
			c.node(str(a1))

	with g.subgraph(name='cluster_2') as d:
		d.attr(color='blue')
		d.attr(label=labelSet2)
		d.node_attr.update(style='filled')
		for a2 in A2:
			d.node("d_"+str(a2),label=str(a2))
	for (a1,a2) in R:
		g.edge(str(a1),"d_"+str(a2))
	return g


def visualiza_auto_relacao(A, R, labelSet=""):
	g = Digraph()
	g.attr(rankdir='LR')

	with g.subgraph(name='cluster_1') as c:
		c.attr(color='blue')
		c.node_attr.update(style='filled')
		c.attr(label=labelSet)
		for a1 in A:
			c.node(str(a1))
	for (a1,a2) in R:
		g.edge(str(a1),str(a2))
	return g

# Em python, não podemos ter um conjunto de conjuntos. Portanto, essa função retorna uma lista de listas.
def powerset(fullset):
  listsub = list(fullset)
  subsets = []
  for i in range(2**len(listsub)):
    subset = []
    for k in range(len(listsub)):            
      if i & 1<<k:
        subset.append(listsub[k])
    subsets.append(subset)   
  return subsets       

def strPowerSet(X):
  subsets= powerset(X)
  r = "{"
  for i in range(len(subsets)):
    if i== len(subsets)-1: r+=str(set(subsets[i]))
    else: r+= str(set(subsets[i]))+", "
  return r+"}"
def printPowerSet(X):
  print(strPowerSet(X))

def unionSets(*args):
  R = set()
  for a in args:
    R = R.union(a)
  return R
def intersectionSets(*args):
  if (len(args)==0): return set()
  else:
    R = args[0]
    for i in range(1, len(args)):
      R = R.intersection(args[i])
    return R

def produtoCartesiano(A1, A2):
  R = set()
  for a1 in A1:
    for a2 in A2:
      R.add((a1,a2))
  return R

def produtoCartesiano_3(A1, A2, A3):
  R = set()
  for a1 in A1:
    for a2 in A2:
      for a3 in A3:
        R.add((a1,a2,a3))
  return R

def isConexa(A,R):
  for a in A:
    for b in A:
      if not ((a,b) in R or (b,a) in R or a==b): return False
  return True

def isReflexiva(A,R):
  for a in A:
    if (a,a) not in R: return False
  return True

def isSimetrica(A,R):
  for a in A:
    for b in A:
      if (a,b) in R:
        if (b,a) not in R: return False
  return True

def isAntiSimetrica(A,R):
  for a in A:
    for b in A:
      if (a,b) in R and (b,a) in R:
        if (a!=b): return False
  return True

def isTransitiva(A,R):
  for a in A:
    for b in A:
      for c in A:
        if (a,b) in R and (b,c) in R:
          if (a,c) not in R: return False
  return True

def isRelacao(A1,A2,R):
  for (a,b) in R:
    if not a in A1:
      return False
    if not b in A2:
      return False
  return True
  
def isFuncao(A1,A2,R):
  if not isRelacao(A1,A2,R): return False
  for a in A1:
    elemento_unico = None
    for b in A2:
      if (a,b) in R:
        if(elemento_unico ==None): elemento_unico = b
        else: return False
  return True

def isFuncaoTotal(A1,A2,R):
  if not isFuncao(A1,A2,R): return False
  for a in A1:
    elemento_unico = None
    for b in A2:
      if (a,b) in R:
        if(elemento_unico ==None): elemento_unico = b
        else: return False
    if(elemento_unico==None): return False
  return True

def isInjetora(A1,A2,R):
  if not isFuncao(A1,A2,R): return False
  for c in A2:
    elemento_a = None
    for (a,b) in R:
      if (b==c):
        if elemento_a == None: elemento_a = a
        elif elemento_a != a: return False
  return True
  
def isSobrejetora(A1,A2,R):
  if not isFuncao(A1,A2,R): return False
  for b in A2:
    result = False
    for a in A1:
      if (a,b) in R: 
        result = True
        break
    if not result: return False
  return True

def isBijetora(A1,A2,R):
  return isInjetora(A1,A2,R) and isSobrejetora(A1,A2,R)

def fechoTransitivo(A,R):
  S = R.copy()
  adicionou_elemento = True
  while adicionou_elemento:
    adicionou_elemento = False
    for a in A:
      for b in A:
        for c in A:
          if (a,b) in S and (b,c) in S:
            if (a,c) not in S: 
              S.add((a,c))
              adicionou_elemento = True
  return S

def fechoReflexivo(A,R):
  S = R.copy()
  for a in A:
    if (a,a) not in S: S.add((a,a))
  return S

sVazia = ''

# Retorna a o Sigma^k do alfabeto A
def sigma(A,k):
  R = set()
  if k==0: return {sVazia}
  else:
    S = sigma(A,k-1)
    for s in S:
      for a in A:
        R.add(s+str(a))
  return R

# Converte uma string em um número
def T(s):
  s = '1'+s
  z = len(s)
  r = 0
  for x in range (z):
    y = z-x-1
    r+= (2**y)*int(s[x])
  return r


import pandas as pd
# Visualiza a diagonalização de uma auto-relação. Note que D é diferente de todo R
def visualiza_diagonalizacao(A, R):
  l = []
  d ={}
  D = []
  D_s = ''
  A = sorted(list(A))
  for a in A:
    la = []
    R_s = ''
    for b in A:
      if (a,b) in R:
        la.append('x')
        if R_s == '': R_s = str(b)
        else: R_s += ', '+str(b)      
        if a==b: 
          D.append(' ') 
      else:
        if a==b: 
          D.append('x') 
          D_s = str(b) if D_s=='' else D_s+', '+str(b)
        la.append(' ')  
        
    la.append('R_'+str(a)+'={'+R_s+'}')
    d[a] = la
    l.append(la)
  D.append('D={'+D_s+'}')
  if 'D' in A: d['D'] = D  
  else: d[' D'] = D

  df = pd.DataFrame.from_dict(d, orient='index',columns=list(A)+['R'])
  display(df)


class Exercicio_Conjuntos:
  # Gera um conjunto de números inteiros de um dado tamanho
  @staticmethod    
  def gerar_conjunto(size=4, min_value =0, max_value =10):
    return set(sorted([randrange(min_value,max_value+1) for x in range(0, size)]))

  # Gera um conjunto de números inteiros a partir de uma string de inteiros separados por espaço
  @staticmethod   
  def parser_conjunto_inteiros(s):
    C_string = [x for x in s.strip().split(' ') if x!='']
    return set([ int(x.strip()) for x in C_string]) if C_string!=[''] else set()

  # Gera um conjunto de strings a partir de uma string de strings separadas por espaço
  @staticmethod   
  def parser_conjunto_strings(s):
    C_string = [x for x in s.strip().split(' ') if x!='']
    return set([ x.strip() for x in C_string]) if C_string!=[''] else set()

  # Gera uma lista de strings a partir de uma string de strings separadas por espaço
  @staticmethod   
  def parser_lista_strings(s):
    C_string = [x for x in s.strip().split(' ') if x!='']
    return [ int(x.strip()) if x.isdigit() else x.strip() for x in C_string] if C_string!=[''] else set()

  # Gera um conjunto de conjuntos de números inteiros a partir de uma string de conjuntos separados por ; e cada conjunto de inteiros separados por espaço
  @staticmethod   
  def parser_lista_conjuntos_inteiros(s):
    return [Exercicio_Conjuntos.parser_conjunto_inteiros(x) for x in s.strip().split(';')]

  # Gera um conjunto de conjuntos de strings a partir de uma string de conjuntos de strings separados por ; e cada conjunto de string separados por espaço
  @staticmethod   
  def parser_lista_conjuntos_strings(s):
    return [Exercicio_Conjuntos.parser_conjunto_strings(x) for x in s.strip().split(';')]
  # Gera uma conjunto de tuplas de strings a partir de uma string de tuplas de strings separados por ; e cada tupla de string separados por espaço
  @staticmethod   
  def parser_conjunto_tuplas_strings(s):
    tuplas = [tuple(Exercicio_Conjuntos.parser_lista_strings(x)) for x in s.strip().split(';')]
    return set(tuplas) if tuplas !=[()] else set() 


  # Converte uma string em um número
  @staticmethod    
  def T(s):
    s = '1'+s
    z = len(s)
    r = 0
    for x in range (z):
      y = z-x-1
      r+= (2**y)*int(s[x])
    return r

  @staticmethod
  def gerar_string(size=4):
    l= [str(randrange(0,2)) for i in range(size)]
    return ''.join(l)

  @staticmethod    
  def questao_encode_string(size=4):
      layout = widgets.Layout(width='300px')
      run = widgets.Button(description="Verificar")
      s = Exercicio_Conjuntos.gerar_string(size)
      input = widgets.Text(
          value='',
          placeholder=f'Digite a codificação de {s}',
          description=f'',
          layout=layout
          )
      display(Markdown(f"Codifique a palavra {s} em um número, usando a função T:"))
      #print(f"Codifique a palavra {s} em um número, usando a função T:")
      output = widgets.Output()
      wInputBox= widgets.HBox([input,run])

      display(wInputBox,output)
      #print(Exercicio_Conjuntos.T(s))

      def on_button_run_clicked(_):
        output.clear_output()
        with output:
          if (str(Exercicio_Conjuntos.T(s))==(input.value)):
            print(f"\n{bcolors.OKBLUE}Parabéns, você acertou a códificação de {s}!")
          else:
            print(f"\n{bcolors.FAIL}Infelizmente, você errou a códificação de {s}! Tente novamente!")
      run.on_click(on_button_run_clicked)

  @staticmethod    
  def gerar_matriz(size=5):
    A = [x for x in range(size)]
    R = set()
    for i in range(size):
      r_size = randrange(0,size+1)
      for j in range(r_size):
        R.add((j,randrange(0,size+1)))
    return set(A), R

  @staticmethod    
  def get_diagonal(A,R):
    l = []
    for i in range(len(A)):
      if not (i,i) in R:
        l.append(str(i))
    return l
  
  @staticmethod    
  def visualiza_matriz(A,R):
    # Visualiza a diagonalização de uma auto-relação. Note que D é diferente de todo R
    l = []
    d ={}
    A = sorted(list(A))
    for a in A:
      la = []
      R_s = ''
      for b in A:
        if (a,b) in R:
          la.append('x')
        else:
          la.append(' ')  
          
      d[a] = la
      l.append(la)

    df = pd.DataFrame.from_dict(d, orient='index',columns=list(A))
    display(df)

  @staticmethod    
  def visualiza_diagonalizacao(A, R):
    # Visualiza a diagonalização de uma auto-relação. Note que D é diferente de todo R
    l = []
    d ={}
    D = []
    D_s = ''
    A = sorted(list(A))
    for a in A:
      la = []
      R_s = ''
      for b in A:
        if (a,b) in R:
          la.append('x')
          if R_s == '': R_s = str(b)
          else: R_s += ', '+str(b)      
          if a==b: 
            D.append(' ') 
        else:
          if a==b: 
            D.append('x') 
            D_s = str(b) if D_s=='' else D_s+', '+str(b)
          la.append(' ')  
          
      la.append('R_'+str(a)+'={'+R_s+'}')
      d[a] = la
      l.append(la)
    D.append('D={'+D_s+'}')
    if 'D' in A: d['D'] = D  
    else: d[' D'] = D

    df = pd.DataFrame.from_dict(d, orient='index',columns=list(A)+['R'])
    display(df)

  @staticmethod    
  def questao_diagonal(size=4, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos da diagonal da matriz',
        description=f'',
        layout=layout
        )
    output = widgets.Output()
    A, R = Exercicio_Conjuntos.gerar_matriz(size)
    Exercicio_Conjuntos.visualiza_matriz(A,R)
    wInputBox= widgets.HBox([input,run])
    display(Markdown('Digite os elementos da diagonal da matriz'))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        if (Exercicio_Conjuntos.get_diagonal(A,R)== input.value.strip().split(' '))or (Exercicio_Conjuntos.get_diagonal(A,R)== [] and input.value.split(' ')==''):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou a diagonal!")
          Exercicio_Conjuntos.visualiza_diagonalizacao(A, R)
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a diagonal! Tente novamente!")
    run.on_click(on_button_run_clicked)


  @staticmethod    
  def questao_conjunto_propriedade(A, P, descripton_P, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto',
        layout=layout
        )
    output = widgets.Output()
    B = conjunto(A,P)

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto B abaixo:'))
    display(Markdown("B = { x | x $\in$"+f" {A} e x é {descripton_P}"+ " }"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_inteiros(input.value)
        if (B == C):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto!\nB = {B}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_conjunto_potencia(A, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto',
        layout=layout
        )
    output = widgets.Output()
    B = [set(x) for x in powerset(A)]

    wInputBox= widgets.HBox([input,run])
    display(Markdown(rf'Encontre o conjunto-potência de {A}'))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_lista_conjuntos_inteiros(input.value)
        result = True
        for a in B:
          if not a in C:
            result = False
            break
        for a in C:
          if not a in B:
            result = False
            break
        if (result):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto-potência!")
          display(Markdown(f'2^{A} = {strPowerSet(A)}'))
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto-potência! Tente novamente!")
    run.on_click(on_button_run_clicked)



  @staticmethod    
  def questao_conjunto_eh_subconjunto(A,B, proprio=False):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    cResult = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=None, 
      description='Resposta:',
      disabled=False
    )
    output = widgets.Output()

    wInputBox= widgets.HBox([cResult,run])
    if proprio:
      display(Markdown(f"{A} $\subset$ {B} ?"))
    else:
      display(Markdown(f"{A} $\subseteq$ {B} ?"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        if (cResult.value==None):
          display(Markdown('<font color="red">**Escolha uma das alternativas! Tente novamente!**</font>'))
        elif(proprio and A!=B and A.issubset(B) and cResult.value=='Sim'):
          display(Markdown('<font color="blue">**Parabéns, você acertou a questão.**</font>'))
        elif(proprio and (A==B or not A.issubset(B)) and cResult.value=='Não'):
          display(Markdown('<font color="blue">**Parabéns, você acertou a questão.**</font>'))
        elif((not proprio) and A.issubset(B) and cResult.value=='Sim'):
          display(Markdown('<font color="blue">**Parabéns, você acertou a questão.**</font>'))
        elif((not proprio) and (not A.issubset(B)) and cResult.value=='Não'):
          display(Markdown('<font color="blue">**Parabéns, você acertou a questão.**</font>'))
        else:
          display(Markdown('<font color="red">**Infelizmente, você errou a questão. Tente novamente!**</font>'))
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_conjunto_uniao_conjuntos(*args, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto abaixo:'))
    
    display(Markdown(' $\cup$ '.join([str(x) for x in args])))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_inteiros(input.value)
        if (unionSets(*tuple(args)) == C):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto união!\n{C}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto união! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_conjunto_uniao(A, B, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto abaixo:'))
    display(Markdown(f" {A} $\cup$ {B}"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_inteiros(input.value)
        if (A.union(B) == C):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto união!\n{C}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto união! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_conjunto_intersecao_conjuntos(*args, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto abaixo:'))
    
    display(Markdown(' $\cap$ '.join([str(x) for x in args])))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_inteiros(input.value)
        if (intersectionSets(*tuple(args)) == C):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto interseção!\n{C}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto interseção! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_conjunto_intersecao(A, B, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto abaixo:'))
    display(Markdown(f" {A} $\cap$ {B}"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_inteiros(input.value)
        if (A.intersection(B) == C):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto interseção!\n{C}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto interseção! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_conjunto_diferenca(A, B, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto abaixo:'))
    display(Markdown(f" {A} $-$ {B}"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_inteiros(input.value)
        if (A.difference(B) == C):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto diferença!\n{C}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto diferença! Tente novamente!")
    run.on_click(on_button_run_clicked)


  @staticmethod    
  def questao_conjunto_produto_cartesiano(A, B, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite as tuplas',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto abaixo:'))
    display(Markdown(f" {A} $\\times$ {B}"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_tuplas_strings(input.value)
        if (produtoCartesiano(A,B) == C):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o produto cartesiano!\n{C}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o produto cartesiano! Tente novamente!")
    run.on_click(on_button_run_clicked)


  @staticmethod    
  def questao_conjunto_produto_cartesiano_3(A, B,C, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite as tuplas',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Encontre o conjunto abaixo:'))
    display(Markdown(f" {A} $\\times$ {B}$\\times$ {C}"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        D = Exercicio_Conjuntos.parser_conjunto_tuplas_strings(input.value)
        if (produtoCartesiano_3(A,B,C) == D):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o produto cartesiano!\n{D}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o produto cartesiano! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_relacao(A, B, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite as tuplas',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Digite uma relação a partir dos conjuntos abaixo:'))
    display(Markdown(f"{A} e {B}"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        R = Exercicio_Conjuntos.parser_conjunto_tuplas_strings(input.value)
        C = produtoCartesiano(A,B)
        if (R.issubset(C)):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou uma relação!\n{R} é um subconjunto do produto cartesiano dos conjuntos acima.")
          display(visualiza(A, B, R))
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou uma relação! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_auto_relacao(A, R,default_conexa=None, default_reflexiva=None, default_simetrica=None, default_anti_simetrica=None, default_transitiva=None):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    cConexa = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_conexa,
      description='Conexa:', 
      disabled=False
    )
    cReflexiva = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_reflexiva, 
      description='Rerflexiva:',
      disabled=False
    )
    cSimetrica = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_simetrica, 
      description='Simétrica:',
      disabled=False
    )
    cAntiSimetrica = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_anti_simetrica, 
      description='Anti-simétrica:',
      disabled=False
    )
    cTransitiva = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_transitiva, 
      description='Transitiva:',
      disabled=False
    )

    output = widgets.Output()

    display(Markdown('Considere a auto-relação abaixo:'))
    display(visualiza_auto_relacao(A,R))
    display(Markdown('Responda se a auto-relação é:'))
    display(cConexa, cReflexiva, cSimetrica, cAntiSimetrica, cTransitiva,run,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        vConexa = isConexa(A,R)
        vReflexiva = isReflexiva(A,R)
        vSimetrica = isSimetrica(A,R)
        vAntiSimetrica = isAntiSimetrica(A,R)
        vTransitiva = isTransitiva(A,R)
        result = True
        if ((cConexa.value=='Sim')!=vConexa):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser conexa! Tente novamente!")
          result = False
        if ((cReflexiva.value=='Sim')!=vReflexiva):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser reflexiva! Tente novamente!")
          result = False
        if ((cSimetrica.value=='Sim')!=vSimetrica):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser simétrica! Tente novamente!")
          result = False
        if ((cAntiSimetrica.value=='Sim')!=vAntiSimetrica):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser anti-simétrica! Tente novamente!")
          result = False
        if ((cTransitiva.value=='Sim')!=vTransitiva):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser transitiva! Tente novamente!")
          result = False
        if result:
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou todas as propriedades da auto-relação!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_fecho_relacao(A, R, input_response='', reflexivo=True, transitivo=True):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite as tuplas',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown('Considere a auto-relação abaixo:'))
    display(visualiza_auto_relacao(A,R))

    texto = 'reflexivo e transitivo ' if reflexivo and transitivo else 'reflexivo ' if reflexivo else 'transitivo ' if transitivo else ''
    display(Markdown(f'Digite a relação que é o fecho {texto}da auto-relação é:'))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        R = Exercicio_Conjuntos.parser_conjunto_tuplas_strings(input.value)
        if reflexivo and transitivo:
          FECHO_R = fechoReflexivo(A,fechoTransitivo(A,R))
        elif reflexivo:
          FECHO_R = fechoReflexivo(A,R)
        elif transitivo:
          FECHO_R = fechoTransitivo(A,R)
        else:
          FECHO_R = R
        if (R==FECHO_R):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o fecho {texto}da auto-relação!\n{FECHO_R}")
          display(visualiza_auto_relacao(A,FECHO_R))
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou uma relação! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_eh_funcao(A,B, R,default_funcao=None, default_funcao_total=None):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    cFuncao = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_funcao,
      description='Função:', 
      disabled=False
    )
    cFuncaoTotal = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_funcao_total, 
      description='Função Total:',
      disabled=False
    )

    output = widgets.Output()

    display(Markdown('Considere a relação abaixo:'))
    display(visualiza(A,B,R))
    display(Markdown('Responda se a relação é:'))
    display(cFuncao, cFuncaoTotal,run,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        vFuncao = isFuncao(A,B,R)
        vFuncaoTotal = isFuncaoTotal(A,B,R)
        result = True
        if ((cFuncao.value=='Sim')!=vFuncao):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser função! Tente novamente!")
          result = False
        if ((cFuncaoTotal.value=='Sim')!=vFuncaoTotal):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser função total! Tente novamente!")
          result = False
        if result:
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou todas as propriedades de função!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def questao_eh_funcao_injetora_sobrejetora_bijetora(A,B, R,default_injetora=None, default_sobrejetora=None, default_bijetora=None):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    cInjetora = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_injetora,
      description='Injetora:', 
      disabled=False
    )
    cSobrejetora = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_sobrejetora, 
      description='Sobrejetora:',
      disabled=False
    )
    cBijetora = widgets.RadioButtons(
      options=['Sim', 'Não'],
      value=default_bijetora,
      description='Bijetora:', 
      disabled=False
    )

    output = widgets.Output()

    display(Markdown('Considere a relação abaixo:'))
    display(visualiza(A,B,R))
    display(Markdown('Responda se a relação é:'))
    display(cInjetora, cSobrejetora,cBijetora,run,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        vInjetora = isInjetora(A,B,R)
        vSobrejetora = isSobrejetora(A,B,R)
        vBijetora = isBijetora(A,B,R)
        result = True
        if ((cInjetora.value=='Sim')!=vInjetora):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser função injetora! Tente novamente!")
          result = False
        if ((cSobrejetora.value=='Sim')!=vSobrejetora):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser função sobrejetora! Tente novamente!")
          result = False
        if ((cBijetora.value=='Sim')!=vBijetora):
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a relação de ser função bijetora! Tente novamente!")
          result = False
        if result:
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou todas as propriedades de função!")
    run.on_click(on_button_run_clicked)


  @staticmethod    
  def questao_conjunto_sigma(A, k=3, input_response=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_response,
        placeholder=f'Digite os elementos do conjunto Sigma {k}',
        layout=layout
        )
    output = widgets.Output()

    wInputBox= widgets.HBox([input,run])
    display(Markdown(f'Encontre o conjunto Sigma {k} do alfabeto abaixo:'))
    display(Markdown(f"{A}"))
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        C = Exercicio_Conjuntos.parser_conjunto_strings(input.value)
        S = sigma(A,k)
        if (S == C or (k==0 and C==set())):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou o conjunto Sigma {k}!\n{S}")
          display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou o conjunto Sigma {k}! Tente novamente!")
    run.on_click(on_button_run_clicked)

