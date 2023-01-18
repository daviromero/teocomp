from teocomp.nfa import NFA
from graphviz import Digraph
from time import sleep
import ipywidgets as widgets
from IPython.display import clear_output
import pandas as pd
from IPython.display import display
from teocomp.bcolors import bcolors

class NFA_BB: # Non-Deterministic Finete Automata with Epsilon Transition with Building-Blocks
 
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
        if not t[1] in Sigma.union({''}):
          b = False
          ERROR.append(f"Na transição delta({t}), {t[1]} não está em Sigma")
        if not isinstance(delta[t],set) or not delta[t].issubset(Q):
          b = False
          ERROR.append(f"Na transição delta({t})={delta[t]}, {delta[t]} não é subconjunto de Q")
      return b, ERROR


    def __init__(self, Q={}, Sigma={}, q0=None, delta={}, F=set(), NFAs={}, input_jff=None,keep_traces=True):
        # if input_jff != None:          
        #   Q,Sigma,Gamma,delta,q0,F = MTNDMF.jffToMT(input_jff)

        b, ERROR = NFA_BB.valida(Q,Sigma,q0,delta,F)
        if not b: 
          print(f"{bcolors.FAIL}Os seguintes erros foram encontrados:\n")
          print(',\n'.join(ERROR))

        self.label= 'self'
        self.states = Q
        self.alphabet = Sigma
        self.transition = delta
        self.startState = q0
        self.acceptStates = F
        self.nfa_parent = None
        self.NFAs = NFAs
        for nfa in NFAs.keys():
          NFAs[nfa].label = nfa
          NFAs[nfa].nfa_parent = self
        self.NFAs = self.get_NFAs()
        b, ERROR = NFA_BB.valida(Q,Sigma,q0,delta,F)
        final_nfa_bb = set(self.NFAs.keys()).intersection(self.acceptStates)
        if final_nfa_bb!=set():
          if b: 
            print(f"{bcolors.FAIL}Os seguintes erros foram encontrados:\n")
          if len(final_nfa_bb)==1:
            print(f"{bcolors.FAIL}{', '.join(list(final_nfa_bb))} é um NFA_BB e não pode ser estado de aceitação deste NFA_BB.")
          else:
            print(f"{bcolors.FAIL}{', '.join(list(final_nfa_bb))} são NFA_BBs e não podem ser estados de aceitação deste NFA_BB.")

        self.keep_traces = keep_traces
        self.word = ''
        self.trace = []
        self.set_trace = []
        self.history_traces = []
        self.epsilon_closure = None
        self.set_epsilon_closure()

    def get_NFAs(self):
      nfas = {}
      for nfa in self.NFAs.keys():
        nfas[nfa] = self.NFAs[nfa]
        nfa_nfas = self.NFAs[nfa].get_NFAs()
        for nfa_aux in nfa_nfas.keys():
          nfas[nfa_aux] = nfa_nfas[nfa_aux]
      return nfas

    def get_nfa_parent_labels(self,nfa):
      result = {nfa.label}
      while nfa.nfa_parent!=None:
        result.add(nfa.nfa_parent.label)
        nfa = nfa.nfa_parent
      return result

    def get_nfa_labels(self, NS):
      result = set() 
      for nfa,s in NS:
        result = result.union(self.get_nfa_parent_labels(nfa))
      return list(result)

    def set_epsilon_closure(self):
      self.epsilon_closure = {}
      for s in self.states:
        result = {(self,s)}
        b = True
        while b:
          b = False
          new_set = set()
          for q in result:
            if (q,'') in self.transition:
              for s_q in self.transition[q,'']:
                if not s_q in result:
                  new_set.add((self,s_q))
                  b = True
          result = result.union(new_set)
        for nfa in self.NFAs.keys():
          if (self,nfa) in result:
            result.remove((self,nfa))
            result = result.union(self.NFAs[nfa].epsilon_closure[self.NFAs[nfa].startState])
        self.epsilon_closure[s] = result

    def id_to_str(self, id):
      return (f'{id[1]}, {self.word[id[2]:]}, {id[0].label}')

    def deduction(self, id):
      if id==None:
        return [] 

      result = []
      nfa, s, pos = id
      if pos>=len(self.word):
        return [] 
      a = self.word[pos]

      if (s,a) in nfa.transition and len(nfa.transition[s,a])>0:
        transition_closure = set()
        for r in nfa.transition[s,a]:
          transition_closure = transition_closure.union(nfa.epsilon_closure[r])
        for n,r_s in  transition_closure:
          if r_s in self.NFAs.keys():
            result.append((n,self.NFAs[r_s].startState,pos+1)) #talvez fazer o closure
          else:
            result.append((n,r_s,pos+1))
      elif s in nfa.acceptStates and nfa.nfa_parent!=None:
        if (nfa.label,a) in nfa.nfa_parent.transition:        
          transition_closure = set()
          for r in nfa.nfa_parent.transition[nfa.label,a]:
            transition_closure = transition_closure.union(nfa.nfa_parent.epsilon_closure[r])
          for n,r_s in  transition_closure:
            if r_s in nfa.nfa_parent.NFAs.keys():
              result.append((n,nfa.nfa_parent.NFAs[r_s].startState,pos+1)) 
            else:
              result.append((n,r_s,pos+1))
      return result

    def get_initial_ids(self):
      history_traces = []
      for n,r_s in self.epsilon_closure[self.startState]:
        history_traces.append((n,r_s,0))
      return history_traces

    def trace_accept(self, trace):
      return trace[-1][0]==self and trace[-1][1] in self.acceptStates and trace[-1][2]==len(self.word)

    def accept(self,word):
      self.word = word
      self.trace = []
      self.history_traces = []
      traces = [self.get_initial_ids()]
      if self.keep_traces:
        self.history_traces = traces
        self.set_trace = [(set([(t[-1][0],t[-1][1]) for t in traces]), 0)]
      for pos in range(len(word)):
        updated_traces = []
        has_new_deduction = False
        for trace in traces:
          id = trace[-1]
          if id[2]==pos:
            l_ids = self.deduction(id)
            if len(l_ids)>0:
              for n_id in l_ids:
                updated_traces.append(trace+[n_id])
                has_new_deduction = True
            else:
              updated_traces.append(trace)
          else:
            updated_traces.append(trace)
        if not has_new_deduction:
          break
        traces = updated_traces
        if self.keep_traces:
          self.history_traces = traces
          self.set_trace.append((set([(t[-1][0],t[-1][1]) for t in traces if t[-1][2]==pos+1]),pos+1))
      for trace in traces:
        if self.trace_accept(trace):
          return True
      return False

    def aceita(self,word):
      return self.accept(word)

    def nfa_state_to_str(self,S):
      return '{'+','.join(sorted([f'{nfa.label}:{s}' for nfa,s in S ]))+'}'

    def trace_to_str(self):
      result = []
      for (S, pos) in self.set_trace:
        if pos <len(self.word):
          result.append(self.nfa_state_to_str(S) +' '+self.word[pos])
        else:
          result.append(self.nfa_state_to_str(S))
      return ' '.join(result)


    def deduction_to_trace(self,deduction):
      return [({(nfa,q)},pos) for nfa, q,pos in deduction]

    def get_deduction(self, accept=True):
      for trace in self.history_traces:
        if (trace[-1][1] in self.acceptStates and trace[-1][2]==len(self.word)) == accept:
          return trace
      return self.get_initial_ids[0]

    def trace_to_deduction(self,trace):
      return '   '+'\n|- '.join([self.id_to_str(id) for id in trace])

    def traces_to_deduction(self):
      result = []
      for t in self.history_traces:
        result.append('   '+'\n|- '.join([self.id_to_str(id) for id in t]))
      return result

    def traces_to_deduction_print(self):
      print('\n\n'.join(self.traces_to_deduction()))

    def trace_visualizar(self,highlight=[], nfa_name = '', size='8,5'):             
        return self.trace_display(highlight=highlight, nfa_name = nfa_name, size=size)

    def trace_display(self,highlight=[], nfa_name = '', size='8,5'):             
        f = Digraph('finite automata '+nfa_name, filename='nfa.gv')
        f.attr(rankdir='LR')
        if size!=None:
          f.attr(size=size)
 
        f.attr('node', shape='point')
        f.node('')
 
        for index, (NS, pos) in enumerate(self.set_trace):
          shapeType = 'circle'
          for n in [s for nfa, s in NS]:
            if n in self.acceptStates:
              shapeType = 'doublecircle'
              break
          f.node(str(index),shape=shapeType,label=self.nfa_state_to_str(NS))
          # a_label = self.word[pos] if pos<len(self.word) else ''
          if index==0:
            f.edge('',str(index))
          else:
            f.edge(str(index-1),str(index),label=self.word[pos-1])
        return f

    def resultados_visualizar(self, casos_testes):
      self.display_results(cases_test=casos_testes)

    def display_results(self, cases_test):
      df = pd.DataFrame.from_dict(cases_test,orient='index',
                       columns=['Esperado'])
      lResult = []
      for palavra in casos_testes.keys():
        lResult.append(self.aceita(palavra))
      df['Resultado'] =lResult
      df.reset_index(inplace=True)
      df.rename(columns={'index':'Palavra'},inplace=True)
      acertos = df['Esperado'][df['Esperado']==df['Resultado']].count()
      casos = len(lResult)
      display('Acertou {:.2f}% ({} de {})'.format(acertos/casos*100, acertos, casos))
      display(df)

    def visualizar(self,highlight=[],highlightNonDeterministic=False, label = ''):             
      return self.display(highlight=highlight,highlightNonDeterministic=highlightNonDeterministic, label = label)

    def display(self,highlight=[],highlightNonDeterministic=False, label = ''):             
        f = Digraph('finite automata '+label, filename='nfa.gv')
        f.attr(rankdir='LR', size='8,5')
 
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
          for r in self.transition[(s,a)]:         
            if (s,r) in label:        
              label[s,r] += ', '+a
            else:
              label[s,r] = a       

        nonDeterministic = {}
        if highlightNonDeterministic:
          for key in self.transition:
            if len(self.transition[key])>1:
              for value in self.transition[key]:    
                nonDeterministic[key[0],value] = True

        for (q,r) in label:
          if highlightNonDeterministic and (q,r) in nonDeterministic:
            f.edge(str(q),str(r),label=label[q,r],color="blue")#,fontcolor="blue")      
          else:
            f.edge(str(q),str(r),label=label[q,r])         

        return f


    def display_word(self,id):
        s = Digraph('word'+self.word, filename='word.gv', node_attr={'shape': 'record','width':'0.1'})
        NS, pos = id

        s.node('',shape='point')
        fields = ['<f{}>{}'.format(i,a) for i,a in enumerate(self.word+' ')]
        s.node('word', "|".join(fields))
        s.edges([('', 'word:f{}'.format(pos))])

        return s      


    def begin_display(self, id=None, pausa = 0.8, show_other_NFAs= True):
        if id==None: id = self.set_trace[0]
        NS, pos = id
        # Inicializa os displays
        d_word = display(self.display_word(id),display_id=True)
        d_NFA = display(self.visualizar(highlight=[s for nfa, s in NS if nfa==self]),display_id=True)
        d_NFAs = None
        if(show_other_NFAs):
          d_NFAs = {}
          nfas = self.get_NFAs()
          for nfa in nfas.items():
            d_NFAs[nfa[0]] = display(nfa[1].visualizar(highlight=[s for nfa_aux, s in NS if nfa==nfa_aux]),display_id=True)
        sleep(pausa)
        return d_word, d_NFA, d_NFAs

    def display_id(self, id, d_word, d_NFA, d_NFAs, pausa = 0.8, pausa_entre_ids = 0, show_other_NFAs= True):
      NS, pos = id

      if(pausa_entre_ids>0):
        d_NFA.update(self.visualizar(highlight=[]))
        if(show_other_NFAs):
          for nfa in self.NFAs.items():
            d_NFAs[nfa[0]].update(nfa[1].visualizar(highlight=[]))
        sleep(pausa_entre_ids)

      d_word.update(self.display_word(id))
      highlight_states = self.get_nfa_labels(NS)
      if(show_other_NFAs):
        for nfa in self.NFAs.items():
          nfa_highlight = [s for nfa_aux, s in NS if nfa[1]==nfa_aux]
          d_NFAs[nfa[0]].update(nfa[1].visualizar(highlight=nfa_highlight+highlight_states))
          if(len(nfa_highlight)>0):
            highlight_states.append(nfa[0])
      d_NFA.update(self.visualizar(highlight=[s for nfa, s in NS if nfa==self]+highlight_states))

      sleep(pausa)

    def simular(self, input_string='', pausa = 0.8, show_other_NFAs=True):
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
          value=input_string,
          placeholder='Digite a entrada',
          description='Entrada:',
          disabled=False,
          layout= layout
      )
      only_trace = widgets.Checkbox(
          value=True,
          description_tooltip='Marque se você deseja visualizar um trace apenas',
          description='Trace único',
          disabled=False,
      )
      output = widgets.Output()
      wButtons = widgets.HBox([only_trace,step,run,speed])
      wInputBox= widgets.HBox([input, reset])
      allButtons = widgets.VBox([wInputBox,wButtons])
      display(allButtons,output)
      self.d_NFA = None
      self.d_NFAs = None
      self.d_word = None
      self.step_simulation = 0

      def on_button_step_clicked(_):
        run.disabled = True
        speed.disabled = True
        input.disabled = True
        step.disabled = True
        only_trace.disabled = True
  
        if self.d_NFA == None:
          # Inicializa o NFA
          self.keep_traces = True          
          self.result = self.accept(input.value)
          # Inicializa os displays
          self.d_word, self.d_NFA, self.d_NFAs = self.begin_display(self.set_trace[0], show_other_NFAs=show_other_NFAs)
          self.step_simulation = 0
          if only_trace.value:
            if self.result:
              self.set_trace = self.deduction_to_trace(self.get_deduction())
            else:
              self.set_trace = self.deduction_to_trace(self.get_deduction(accept=False))
        self.display_id(self.set_trace[self.step_simulation], self.d_word, self.d_NFA, self.d_NFAs, pausa = pausa, pausa_entre_ids = 0.1, show_other_NFAs=show_other_NFAs)        
        if(self.step_simulation==len(self.set_trace)-1):
          with output:
            if self.result: print(f"{bcolors.OKBLUE}A palavra {input.value} foi aceita.\n")
            else: print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por nenhuma computação.\n")
        self.step_simulation += 1
        if(self.step_simulation==len(self.set_trace)):          
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
        only_trace.disabled = True

        if self.d_NFA == None:
          # Inicializa a MT
          self.keep_traces = True          
          self.result = self.accept(input.value)
          if only_trace.value:
            if self.result:
              self.set_trace = self.deduction_to_trace(self.get_deduction())
            else:
              self.set_trace = self.deduction_to_trace(self.get_deduction(accept=False))
          # Inicializa os displays
          self.d_word, self.d_NFA, self.d_NFAs = self.begin_display(self.set_trace[0], show_other_NFAs=show_other_NFAs)
          self.step_simulation = 0
        while self.step_simulation<len(self.set_trace):
          self.display_id(self.set_trace[self.step_simulation], self.d_word, self.d_NFA, self.d_NFAs, pausa = pausa, pausa_entre_ids = 0.1, show_other_NFAs=show_other_NFAs)
          self.step_simulation += 1
        with output:
          if self.result: print(f"{bcolors.OKBLUE}A palavra {input.value} foi aceita.\n")
          else: print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por nenhuma computação.\n")
        reset.disabled = False

      run.on_click(on_button_run_clicked)

      def clear(_):
        speed.value =0.8
        speed.disabled = False
        reset.disabled = False
        step.disabled = False
        run.disabled = False
        input.disabled = False
        only_trace.disabled = False
        only_trace.value = True
        input.value = input_string
        clear_output()
        display(allButtons,output)
        self.d_NFA = None
        self.d_NFAs = None
        self.d_word = None
        output.clear_output()

      reset.on_click(clear)

    def states_to_str(self, states):
       return '{' + ', '.join(sorted(list(states)))+'}'

    def get_states_nfa(self, S):
      result = set()
      for s in S:
        if s in self.NFAs.keys():
          result.add(f'{s}_{self.NFAs[s].startState}')
        else:
          result.add(s)
      return result

    def to_NFA(self):
      Q = self.states.difference(self.NFAs.keys())
      Sigma = self.alphabet
      for nfa in self.NFAs.keys():
        Sigma = Sigma.union(self.NFAs[nfa].alphabet)
      q0 = self.startState
      F = self.acceptStates
      delta = {}
      nfas = {}
      for nfa in self.NFAs.keys():
        if(self.NFAs[nfa].nfa_parent==self):
          nfas[nfa] = self.NFAs[nfa].to_NFA()
      for (s,a) in self.transition:
        if s in nfas.keys():
          S = self.get_states_nfa(self.transition[s,a])
          Q = Q.union(S)
          for f_s in nfas[s].acceptStates:
            f_s = f'{s}_{f_s}'
            Q.add(f_s)
            delta[f_s, a] = S
        else:
          S = self.get_states_nfa(self.transition[s,a])
          Q = Q.union(S)
          delta[s, a] = S
      for nfa in nfas.keys():
        Q = Q.union(set([nfa+'_'+r for r in nfas[nfa].states]))
        for (s,a) in nfas[nfa].transition:
          delta[nfa+'_'+s,a] = set([nfa+'_'+r for r in nfas[nfa].transition[s,a]])
      return NFA(Q,Sigma,q0,delta,F)
