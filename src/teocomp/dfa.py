from collections import deque
from graphviz import Digraph
from time import sleep
import ipywidgets as widgets
from IPython.display import clear_output
import pandas as pd
from IPython.display import display, Markdown
from teocomp.bcolors import bcolors


class DFA: # Deterministic Finete Automata
 
    @staticmethod
    def valida(Q={}, Sigma={}, q0=0, delta={}, F=set()):
      b = True
      ERROR = []
      if not q0 in Q:
        b = False
        ERROR.append(f"{q0} não está em Q")
      if not F.issubset(Q):
        b = False
        ERROR.append(f"{F} não é subconjunto de Q")
      for t in delta.keys():
        if(len(t)!=2):
          b = False
          ERROR.append(f"A transição delta({t}) tem mais de duas entradas")
        q = t[0]        
        if not q in Q:
          b = False
          ERROR.append(f"Na transição delta({t}), {q} não está em Q")
        if not t[1] in Sigma:
          b = False
          ERROR.append(f"Na transição delta({t}), {t[1]} não está em Sigma")
        if not delta[t] in Q:
          b = False
          ERROR.append(f"Na transição delta({t})={delta[t]}, {delta[t]} não está em Q")
      return b, ERROR


    def __init__(self, Q={}, Sigma={}, q0=None, delta={}, F=set(),input_jff=None):
        # if input_jff != None:          
        #   Q,Sigma,Gamma,delta,q0,F = MTNDMF.jffToMT(input_jff)

        b, ERROR = DFA.valida(Q,Sigma,q0,delta,F)
        if not b: 
          print(f"{bcolors.FAIL}Os seguintes erros foram encontrados:\n")
          print(',\n'.join(ERROR))

        self.states = Q
        self.alphabet = Sigma
        self.transition = delta
        self.startState = q0
        self.acceptStates = F
        # A dictionary for each state s returns transitions as the list of alphabets and the list of states
        self.s_t = self.get_state_transition() 
        self.word = ''
        self.trace = []

    def get_state_transition(self):
      s_t = {} # a subset of 2^Ax2^S 
      for s in self.states:
        s_t[s] = ([],[])
      for (s,a) in self.transition:
        s_t[s][0].append(a)
        s_t[s][1].append(self.transition[s,a])
      return s_t

    def min_aux(self, P, X):
        if(len(X)<2):
            return [X] 
        R = [ [X[0]] ]
        for i in range(len(X)-1):
            equal_equivalence = False
            for j in range(len(R)):
                equal_states = True
                alphabet = set(self.s_t[R[j][0]][0]).union(set(self.s_t[X[i+1]][0]))
                for a in alphabet:
                    dest1 = None
                    dest2 = None
                    if (R[j][0], a) in self.transition: dest1 = self.transition[R[j][0],a]
                    if (X[i+1],a) in self.transition: dest2 = self.transition[X[i+1],a]
                    equal_dest = True
                    if(dest1!=dest2):
                        equal_dest = False
                        for k in range(len(P)):
                            if(dest1 in P[k] and dest2 in P[k]):
                                equal_dest = True
                                break
                    if(equal_dest==False):
                        equal_states = False
                        break       
                if(equal_states):
                    R[j].append(X[i+1])
                    equal_equivalence = True
                    break
            if(equal_equivalence==False):
                R.append([X[i+1]])
        return R

    def minimization(self,show_partitions=False):
        self.remove_unreachable_states()
        P = []
        list_accepting_states = list(self.acceptStates)#.sort()
        list_non_accepting_states = list(self.states.difference(self.acceptStates))#.sort() 
        if len(list_non_accepting_states)>0:
            P.append(sorted(list_non_accepting_states))
        if len(list_accepting_states)>0:
            P.append(sorted(list_accepting_states))
        new_partition = True
        Q = []
        i=0
        if show_partitions:
          print(f'{i}-equivalence: {P}')
        while(new_partition):   
            Q = []
            new_partition = False
            for i in range(len(P)):
                R = self.min_aux(P, P[i])
                if len(R)>1: #Se o conjunto P[i] gerou um novo conjunto
                    new_partition = True
                for X in R:
                    Q.append(X)
            P = Q.copy()
            if show_partitions:
              print(f'{i}-equivalence: {P}')
            i+=1

        min_states = set()
        min_initial_state = None
        min_accepting_states = set()
        min_transitions = {}
        min_alphabet = self.alphabet.copy()
        N_S =[]
        for S in P:
            n_s = []
            for s in S: n_s.append(s)
            N_S.append(n_s) 
        P = N_S

        for S in P:
            state = str(S)
            min_states.add(state)
            if(self.startState in S):
                min_initial_state = state
            for final in list_accepting_states:
                if(final in S):
                    min_accepting_states.add(state)
                    break
            for a in self.alphabet:
                state_destination = None
                if((S[0],a) in self.transition ): state_destination = self.transition[(S[0],a)]
                if(state_destination!=None):
                    for D in P:
                        if(state_destination in D):
                            min_transitions[state,a] = str(D)
                            break
        
        return  DFA(Q=min_states, Sigma=min_alphabet, q0=min_initial_state, delta=min_transitions, F=min_accepting_states)

    def remove_unreachable_states(self):
      states = {self.startState}
      accepting_states = set()
      transitions = {}
      S = deque([self.startState])
      while(S):
        s = S.popleft()
        if(s in self.acceptStates):
          accepting_states.add(s)
        (lA,lS) = self.s_t[s]
        for i in range(len(lA)):
          transitions[s,lA[i]] = lS[i]
          if lS[i] not in states:
            states.add(lS[i])
            S.append(lS[i])            
      self.states = states
      self.transition = transitions
      self.acceptStates = accepting_states

    def rename(self, prefix_name='s'):
      states = set()
      initial_state = None
      accepting_states = set()
      transitions = {}
      i = 1
      tStates = {}
      for s in self.states:
          if(s == self.startState):
              new_state = '{}{}'.format(prefix_name,0)
              states.add(new_state)
              tStates[s] = new_state
              initial_state = new_state
              if (s in self.acceptStates):
                  accepting_states.add(new_state)
          else:
              new_state = '{}{}'.format(prefix_name,i)
              states.add(new_state)
              tStates[s] = new_state
              if (s in self.acceptStates):
                  accepting_states.add(new_state)
              i = i + 1
      for t in self.transition:
          transitions[tStates[t[0]], t[1]] = tStates[self.transition[t[0], t[1]]]
      self.states = states
      self.startState = initial_state
      self.acceptStates = accepting_states
      self.transition = transitions
      self.s_t = self.get_state_transition() 

    def id_to_str(self, id):
      return (f'{id[0]}, {self.word[id[1]:]}')

    def delta(self, s, input, show_steps=False):
      if input=='' or input==[]:
        if show_steps:
          display(Markdown(r'$\bar{\delta}_D('+s+f',\epsilon) = {s}$'))
        self.trace.append((s,0))
        return s
      else:
        s_delta_bar = self.delta(s,input[:-1],show_steps=show_steps)
        if (s_delta_bar,input[-1]) in self.transition.keys():
          d = self.transition[s_delta_bar,input[-1]]
          if show_steps:
            if len(input[1:])>0:
              s_aux = input[1:]  
            else:
              s_aux = '\epsilon'
            display(Markdown(r'$\bar{\delta}_D('+s+f',{input}) = \delta_D('+r'\bar{\delta}_D(' + f'{s},{s_aux}), {input[0]}) = \delta_D({s_delta_bar},{input[-1]}) = {d}$'))
          self.trace.append((d,self.trace[-1][1]+1))
          
          return d
        else:
          #self.traces.append((set(),input[-1]))
          return None
          
    def len_states(self):
      return len(self.states)

    def len_transition(self):
      return len( self.transition)

    def aceita(self,palavra):
      return self.accept(palavra)
    def accept(self,word):
      self.word = word
      self.trace = []
      return self.delta(self.startState,word) in self.acceptStates

    def exibir_resultados(self, casos_testes):
      self.display_results(cases=casos_testes)
    def display_results(self, cases):
      df = pd.DataFrame.from_dict(cases,orient='index',
                       columns=['Esperado'])
      lResult = []
      for palavra in cases.keys():
        lResult.append(self.aceita(palavra))
      df['Resultado'] =lResult
      df.reset_index(inplace=True)
      df.rename(columns={'index':'Palavra'},inplace=True)
      acertos = df['Esperado'][df['Esperado']==df['Resultado']].count()
      casos = len(lResult)
      display('Acertou {:.2f}% ({} de {})'.format(acertos/casos*100, acertos, casos))
      display(df)

    def trace_to_str(self):
      result = []
      for (s, pos) in self.trace:
        if pos <len(self.word):
          result.append(str(s)+' '+self.word[pos])
        else:
          result.append(str(s))
      return ' '.join(result)

    def trace_print(self):
      print(self.trace_to_str())

    def trace_to_deduction(self,trace):
      return '   '+'\n|- '.join([self.id_to_str(id) for id in trace])

    def trace_to_deduction_print(self):
      print('   '+'\n|- '.join([self.id_to_str(id) for id in self.trace]))

    def traces_to_deduction_print(self):
      print('\n'.join(self.traces_to_deduction()))

    def trace_visualizar(self,highlight=[], dfa_name = '', size='8,5'):             
        return self.trace_display(highlight=highlight, dfa_name = dfa_name, size=size)

    def trace_display(self,highlight=[], dfa_name = '', size='8,5'): 
        f = Digraph('finite automata '+dfa_name, filename='dfa.gv')
        f.attr(rankdir='LR')
        if size!=None:
          f.attr(size=size)
 
        f.attr('node', shape='point')
        f.node('')
 
        for index, (s, pos) in enumerate(self.trace):
          shapeType = 'circle'
          if s in self.acceptStates:
            shapeType = 'doublecircle'
          f.node(str(index),shape=shapeType,label=s)
          if index==0:
            f.edge('',str(index))
          else:
            f.edge(str(index-1),str(index),label=self.word[pos-1])
        return f

    def visualizar(self,highlight=[], label = '',size='8,5'):             
      return self.display(highlight=highlight,label = label, size=size)
      
    def display(self,highlight=[],label = '',size='8,5'):             
        f = Digraph('finite automata '+label, filename='dfa.gv')
        f.attr(rankdir='LR')
        if size!=None:
          f.attr(size=size)

        f.attr('node', shape='point')
        f.node('')
 
        for n in self.states:
          shapeType = 'circle'
          if n in self.acceptStates:
            shapeType = 'doublecircle'
          if n in highlight:
            f.node(str(n),color='gray',style='filled', shape=shapeType)
          else:
            f.node(str(n),shape=shapeType)
 
        f.edge('', str(self.startState))
 
        label = {} 
        for (s,a) in self.transition:  
          if (s,self.transition[(s,a)]) in label:        
            label[s,self.transition[(s,a)]] += ', '+a
          else:
            label[s,self.transition[(s,a)]] = a       

        for (q,r) in label:
          f.edge(str(q),str(r),label=label[q,r])      

        return f

    def table(self):
      self.tabela()

    def tabela(self):
      d_tabela = {}
      states = []
      sorted_states = sorted(list(self.states)) 
      for s in sorted_states:
        if s==self.startState and s in self.acceptStates:
          states.append('->*'+s)
        elif s==self.startState:
          states.append('->'+s)
        elif s in self.acceptStates:
          states.append('*'+s)
        else: 
          states.append(s)
      d_tabela['Estado'] = states
      for a in sorted(list(self.alphabet)):
        l = []
        for s in sorted_states:
          if (s,a) in self.transition.keys():
            l.append(self.transition[s,a])
          else:
            l.append('-')
        d_tabela[a] = l
      df = pd.DataFrame(d_tabela)
      display(df.style.hide_index()) 


    def display_word(self,id):
        s = Digraph('word'+self.word, filename='word.gv',
                    node_attr={'shape': 'record','width':'0.1'})
        q, pos = id

        s.node('',shape='point')
        fields = ['<f{}>{}'.format(i,a) for i,a in enumerate(self.word+' ')]
        s.node('word', "|".join(fields))
        s.edges([('', 'word:f{}'.format(pos))])

        return s      


    def begin_display(self, id=None, pausa = 0.8, size='8,5'):
        if id==None: id = self.trace[0]
        # Inicializa os displays
        d_word = display(self.display_word(id),display_id=True)
        d_DFA = display(self.visualizar(highlight=[id[0]], size= size),display_id=True)
        return d_word, d_DFA

    def display_id(self, id, d_word, d_DFA, pausa = 0.8, pausa_entre_ids = 0, size='8,5'):
      if(pausa_entre_ids>0):
        d_DFA.update(self.visualizar(highlight=[], size= size))
        sleep(pausa_entre_ids)

      d_word.update(self.display_word(id))
      d_DFA.update(self.visualizar(highlight=[id[0]], size= size))
      sleep(pausa)


    def simular(self, word='', pausa = 0.8, size='8,5'):
      self.simulate(word=word, pausa = pausa, size=size)
    def simulate(self, word='', pausa = 0.8, size='8,5'):
      layout = widgets.Layout(width='750px')
      speed = widgets.FloatSlider(
          value=0.8,
          min=0,
          max=3.0,
          step=0.1,
          description='Pausa:',
          description_tooltip='Defina a pausa (em segundos) de exibição entre as descrições instantâneas da simulação.',
          disabled=False,
          continuous_update=False,
          orientation='horizontal',
          readout=True,
          readout_format='.1f',
      )
      step = widgets.Button(description="Passo-a-Passo")
      run = widgets.Button(description="Simular")
      reset = widgets.Button(description="Limpar")
      input = widgets.Text(
          value=word,
          placeholder='Digite a entrada',
          description='Entrada:',
          disabled=False,
          layout= layout
      )
      output = widgets.Output()
      wButtons = widgets.HBox([step,run,speed])
      wInputBox= widgets.HBox([input, reset])
      allButtons = widgets.VBox([wInputBox,wButtons])
      display(allButtons,output)
      self.d_DFA = None
      self.d_word = None
      self.step_simulation = 0

      def on_button_step_clicked(_):
        run.disabled = True
        speed.disabled = True
        input.disabled = True
        step.disabled = True
  
        if self.d_DFA == None:
          # Inicializa o DFA
          self.keep_traces = True          
          self.result = self.accept(input.value)
          # Inicializa os displays
          self.d_word, self.d_DFA = self.begin_display(self.trace[0], size=size)
          self.step_simulation = 0
        else:
          self.step_simulation += 1
          self.display_id(self.trace[self.step_simulation], self.d_word, self.d_DFA, pausa = pausa, pausa_entre_ids = 0.1, size=size)
        if(self.step_simulation==len(self.trace)-1):
          with output:
            if self.result: print(f"{bcolors.OKBLUE}A palavra {input.value} foi aceita.\n")
            else: print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por nenhuma computação.\n")
        if(self.step_simulation==len(self.trace)-1):
          step.disabled = True
        else:  
          step.disabled = False

      step.on_click(on_button_step_clicked)

      def on_button_run_clicked(_):
        reset.disabled = True
        step.disabled = True
        run.disabled = True
        input.disabled = True
        speed.disabled = True
        if self.d_DFA == None:
          # Inicializa a MT
          self.keep_traces = True          
          self.result = self.accept(input.value)
          # Inicializa os displays
          self.d_word, self.d_DFA = self.begin_display(self.trace[0], size=size)
          self.step_simulation = 0
        while self.step_simulation<len(self.trace):
          self.display_id(self.trace[self.step_simulation], self.d_word, self.d_DFA, pausa = pausa, pausa_entre_ids = 0.1, size=size)
          self.step_simulation += 1
        with output:
          if self.result: print(f"{bcolors.OKBLUE}A palavra {input.value} foi aceita.\n")
          else: print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por nenhuma computação. Veja um exemplo:\n")
        reset.disabled = False

      run.on_click(on_button_run_clicked)

      def clear(_):
        speed.value =0.8
        speed.disabled = False
        reset.disabled = False
        step.disabled = False
        run.disabled = False
        input.disabled = False
        input.value = word
        clear_output()
        display(allButtons,output)
        self.d_DFA = None
        self.d_word = None
        output.clear_output()

      reset.on_click(clear)