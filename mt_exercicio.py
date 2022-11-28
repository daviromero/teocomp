from random import randrange
import pandas as pd
from mt_ndmf import MTNDMF, S_BLK
import ipywidgets as widgets
from IPython.display import display
from bcolors import bcolors
from mt_encoder import Encoder_MT
from random import randrange

class Exercicio_MT:

  @staticmethod    
  def gerar(num_states=5, num_extra_transition=2):
    q0 = 'q1'
    F = {'q2'}
    lQ = ['q'+str(i+1) for i in range(num_states)]
    Q = set(lQ)
    lQ_aux = lQ.copy()
    lQ_aux.remove('q2')
    blank=S_BLK #=' ' 
    Sigma = {'0','1'}
    Gamma = {'0','1',S_BLK}
    lGamma = list(Gamma)
    lMove = ['R','L','S']
    delta = {}
    delta['q1',lGamma[randrange(0,3)]] = {('q3',lGamma[randrange(0,3)],lMove[randrange(0,3)])}
    delta['q'+str(num_states),lGamma[randrange(0,3)]] = {('q2',lGamma[randrange(0,3)],lMove[randrange(0,3)])}
    for i in range(3,num_states):
      delta['q'+str(i),lGamma[randrange(0,3)]] = {('q'+str(i+1),lGamma[randrange(0,3)],lMove[randrange(0,3)])}
    while num_extra_transition>0:
      s_origem = lQ_aux[randrange(0,num_states-1)]
      s_destino = lQ[randrange(0,num_states)]
      t_origem = lGamma[randrange(0,3)]
      t_destino = lGamma[randrange(0,3)]
      move = lMove[randrange(0,3)]
      if (s_origem,t_origem) in delta:
        if (s_destino,t_destino,move) in delta[s_origem,t_origem]:
          continue
        else:
          delta[s_origem,t_origem].add((s_destino,t_destino,move))
          num_extra_transition = num_extra_transition-1
      else:
        delta[s_origem,t_origem] = {(s_destino,t_destino,move)}
        num_extra_transition= num_extra_transition-1
    return MTNDMF(Q,Sigma,Gamma,delta,q0,blank,F)

  @staticmethod    
  def gerar_tapes(M, size=3):
    tapes = []
    s = M.startState
    for t in M.transition.keys():
      if t[0] == s: 
        tapes = [t[i+1] for i in range(M.ntapes)]
    ta_size = len(M.tapeAlphabet)
    l_alphabet = list(M.tapeAlphabet)
    for i in range(1,size):
      tapes = [tapes[i]+str(l_alphabet[randrange(0,ta_size)]) for i in range(M.ntapes)]
    return tapes

  @staticmethod    
  def gerar_2(num_states=5, num_extra_transition=2):
    q0 = 'q1'
    F = {'q2'}
    lQ = ['q'+str(i+1) for i in range(num_states)]
    Q = set(lQ)
    lQ_aux = lQ.copy()
    lQ_aux.remove('q2')
    blank=S_BLK #=' ' 
    Sigma = {'0','1'}
    Gamma = {'0','1',S_BLK}
    lGamma = list(Gamma)
    lMove = ['R','L','S']
    delta = {}
    delta['q1',lGamma[randrange(0,3)]] = {('q3',lGamma[randrange(0,3)],lMove[0])}
    delta['q'+str(num_states),lGamma[randrange(0,3)]] = {('q2',lGamma[randrange(0,3)],lMove[randrange(0,3)])}
    for i in range(3,num_states):
      delta['q'+str(i),lGamma[randrange(0,3)]] = {('q'+str(i+1),lGamma[randrange(0,3)],lMove[randrange(0,3)])}
    while num_extra_transition>0:
      s_origem = lQ_aux[randrange(0,num_states-1)]
      s_destino = lQ[randrange(0,num_states)]
      t_origem = lGamma[randrange(0,3)]
      t_destino = lGamma[randrange(0,3)]
      move = lMove[randrange(0,3)]
      if (s_origem,t_origem) in delta:
        if (s_destino,t_destino,move) in delta[s_origem,t_origem]:
          continue
        else:
          delta[s_origem,t_origem].add((s_destino,t_destino,move))
          num_extra_transition = num_extra_transition-1
      else:
        delta[s_origem,t_origem] = {(s_destino,t_destino,move)}
        num_extra_transition= num_extra_transition-1
    return MTNDMF(Q,Sigma,Gamma,delta,q0,blank,F)

  @staticmethod    
  def encode(input_string='',num_states=4, num_extra_transition=2):
      layout = widgets.Layout(width='50%')
      run = widgets.Button(description="Verificar")
      input = widgets.Text(
          value=input_string,
          placeholder='Digite o código em binário da MT acima:',
          description='MT (binário):',
          layout=layout
          )
      M = Exercicio_MT.gerar(num_states, num_extra_transition)
      encoder = Encoder_MT(M)
      outputMT = widgets.Output()
      output = widgets.Output()
      
      with outputMT:
        display(M.visualizar())

      display(outputMT, input, run,output)

      def on_button_run_clicked(_):
        output.clear_output()
        with output:
          if (encoder.equals(input.value)):
            print(f"\n{bcolors.OKBLUE}Parabéns, você acertou a códificação!")
          else:
            print(f"\n{bcolors.FAIL}Infelizmente, você errou a códificação! Tente novamente!")
      run.on_click(on_button_run_clicked)

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
  def encode_string(size=4):
      layout = widgets.Layout(width='300px')
      run = widgets.Button(description="Verificar")
      s = Exercicio_MT.gerar_string(size)
      input = widgets.Text(
          value='',
          placeholder=f'Digite a codificação de {s}',
          description=f'',
          layout=layout
          )
      #print(f"Codifique a palavra {s} em um número, usando a função T:")
      output = widgets.Output()
      wInputBox= widgets.HBox([input,run])

      display(wInputBox,output)

      def on_button_run_clicked(_):
        output.clear_output()
        with output:
          if (str(Exercicio_MT.T(s))==(input.value)):
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
  def diagonal(size=4):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value='',
        placeholder=f'Digite os elementos da diagonal da matriz',
        description=f'',
        layout=layout
        )
    output = widgets.Output()
    A, R = Exercicio_MT.gerar_matriz(size)
    Exercicio_MT.visualiza_matriz(A,R)
    wInputBox= widgets.HBox([input,run])
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        if (Exercicio_MT.get_diagonal(A,R)== input.value.split(' '))or (Exercicio_MT.get_diagonal(A,R)== [] and input.value.split(' ')==''):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou a diagonal!")
          Exercicio_MT.visualiza_diagonalizacao(A, R)
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a diagonal! Tente novamente!")
    run.on_click(on_button_run_clicked)



  @staticmethod    
  def mt_universal(M, input_strings=None):
    if input_strings==None:
      input_strings = Exercicio_MT.gerar_tapes(M)
    M.iniciar(input_string_tapes=input_strings)
    encoder = Encoder_MT(M,delimiter_color=False)
    input_MT_word = input_strings[0]

    wOutputMT1 = widgets.Output()
    wOutputMTU1 = widgets.Output()
    wOutputMT2 = widgets.Output()
    wOutputMTU2 = widgets.Output()

    wInputs_1 = [widgets.Text(placeholder=f'Prefixo da Fita {i+1}') for i in range(3)]
    wInputs_2 = [widgets.Text(placeholder=f'Sufixo da Fita {i+1}') for i in range(3)]
    wStates = widgets.Dropdown(description="Estado:",options=sorted(list(['Controle'])),value='Controle', disabled= True,style= {'description_width': '0px'})      
    wText = widgets.HTML(value="<h3>Defina a Descrição Instantânea Inicial da Máquina de Turing Universal de M</h3>")
    output1 = widgets.Output()



    with wOutputMT1:
      display(widgets.HTML(value="<h3>Considere a descrição instântanea inicial da MT M</h3>"))
      M.display()
    with wOutputMTU1:
        wAll = widgets.HBox([widgets.VBox(wInputs_1),wStates,widgets.VBox(wInputs_2)])
        display(wText,wAll,output1)


    wInputs_1_B = [widgets.Text(placeholder=f'Prefixo da Fita {i+1}') for i in range(3)]
    wInputs_2_B = [widgets.Text(placeholder=f'Sufixo da Fita {i+1}') for i in range(3)]
    wStates_B = widgets.Dropdown(description="Estado:",options=sorted(list(['Controle'])),value='Controle', disabled= True,style= {'description_width': '0px'})      
    wText_B = widgets.HTML(value="<h3>Defina a Descrição Instantânea da Máquina de Turing Universal de M ao lado</h3>")
    output2 = widgets.Output()


    with wOutputMT2:
      display(widgets.HTML(value="<h3>Considere a computação em um passo da MT M:</h3>"))
      M.step()
      M.display()

    with wOutputMTU2:
        wAll_B = widgets.HBox([widgets.VBox(wInputs_1_B),wStates,widgets.VBox(wInputs_2_B)])
        display(wText_B, wAll_B)


    wOutput1 = widgets.HBox([wOutputMT1, wOutputMTU1])
    wOutput2 = widgets.HBox([wOutputMT2, wOutputMTU2])
    display(wOutput1, wOutput2)