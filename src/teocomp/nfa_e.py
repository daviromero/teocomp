from teocomp.dfa import DFA
from graphviz import Digraph
from time import sleep
import ipywidgets as widgets
from IPython.display import clear_output
import pandas as pd
from IPython.display import display
from teocomp.bcolors import bcolors

class NFA_E: # Non-Deterministic Finete Automata with Epsilon Transitions
 
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


    def __init__(self, Q={}, Sigma={}, q0=None, delta={}, F=set(), input_jff=None,keep_traces=True):
        # if input_jff != None:          
        #   Q,Sigma,Gamma,delta,q0,F = MTNDMF.jffToMT(input_jff)

        b, ERROR = NFA_E.valida(Q,Sigma,q0,delta,F)
        if not b: 
          print(f"{bcolors.FAIL}Os seguintes erros foram encontrados:\n")
          print(',\n'.join(ERROR))
        self.label= 'self'
        self.states = Q
        self.alphabet = Sigma
        self.transition = delta
        self.startState = q0
        self.acceptStates = F
        self.keep_traces = keep_traces
        self.word = ''
        self.trace = []
        self.history_traces = []
        self.epsilon_closure = None
        self.set_epsilon_closure()

    def set_epsilon_closure(self):
      self.epsilon_closure = {}
      for s in self.states:
        result = {s}
        b = True
        while b:
          b = False
          new_set = set()
          for q in result:
            if (q,'') in self.transition:
              for s_q in self.transition[q,'']:
                if not s_q in result:
                  new_set.add(s_q)
                  b = True
          result = result.union(new_set)
        self.epsilon_closure[s] = result
      

    def id_to_str(self, id):
      return (f'{id[0]}, {self.word[id[1]:]}')

    def delta(self, s, input):
      if input=='' or input==[]:
        r_s = self.epsilon_closure[s]
        return r_s
      else:
        states_delta_bar = self.delta(s,input[:-1])
        result = set()
        for s_delta_bar in states_delta_bar:
          if (s_delta_bar,input[-1]) in self.transition:
            set_r = self.transition[s_delta_bar,input[-1]]
            result = result.union(set_r)
        new_result = set()
        for r in result:
          new_result = new_result.union(self.epsilon_closure[r])
        return new_result

    def deduction(self, id):
      if id==None:
        return [] 

      result = []
      s, pos = id
      if pos>=len(self.word):
        return [] 
      a = self.word[pos]

      if (s,a) in self.transition:
        transition_closure = set()
        for r in self.transition[s,a]:
          transition_closure = transition_closure.union(self.epsilon_closure[r])
        for r in  transition_closure:
          result.append((r,pos+1))
      return result

    def get_initial_ids(self):
      history_traces = []
      for r in self.epsilon_closure[self.startState]:
        history_traces.append([(r,0)])
      return history_traces

    def trace_accept(self, trace):
      return trace[-1][0] in self.acceptStates and trace[-1][1]==len(self.word)

    def len_states(self):
      return len(self.states)

    def len_transition(self):
      total = 0
      for (s,a) in self.transition:
        total += len(self.transition[s,a])
      return total

    def accept(self,word):
      self.word= word
      self.trace = []
      self.history_traces = []
      traces = self.get_initial_ids()
      if self.keep_traces:
        self.history_traces = traces
        self.trace = [(self.epsilon_closure[self.startState], 0)]
      for pos in range(len(word)):
        updated_traces = []
        has_new_deduction = False
        for trace in traces:
          id = trace[-1]
          if id[1]==pos:
            l_ids = self.deduction(id)
            if len(l_ids)>0:
              for n_id in l_ids:
                updated_traces.append(trace+[n_id])
                has_new_deduction = True
            else:
              updated_traces.append(trace)
          else:
            updated_traces.append(trace)
        traces = updated_traces
        if self.keep_traces:
          self.history_traces = traces
          new_set = set([t[-1][0] for t in traces if t[-1][1]==pos+1])
          if len(new_set)>0:
            self.trace.append((new_set,pos+1))
        if not has_new_deduction:
          break
      for trace in traces:
        if self.trace_accept(trace):
          return True
      return False

    def aceita(self,word):
      return self.accept(word)

    def states_to_str(self, states):
       return '{' + ', '.join(sorted(list(states)))+'}'

    def determinization(self):
        """ Returns a DFA that reads the same language of the input NFA.

        Let A be an NFA, then there exists a DFA :math:`A_d` such
        that :math:`L(A_d) = L(A)`. Intuitively, :math:`A_d`
        collapses all possible runs of A on a given input word into
        one run over a larger state set.
        :math:`A_d` is defined as:

        :math:`A_d = (Σ, Q_d , s_0 , ρ_d , F_d )`

        where:

        • :math:`Q_d` which is a subset of `2^S` , i.e., the state set of :math:`A_d` , consists
          of all sets of states S in A;
        • :math:`s_0 = S^0` , i.e., the single initial state of
          :math:`A_d` is the set :math:`S_0` of initial states of A;
        • :math:`F_d = \{Q | Q ∩ F ≠ ∅\}`, i.e., the collection of
          sets of states that intersect F nontrivially;
        • :math:`ρ_d(Q, a) = \{s' | (s,a, s' ) ∈ ρ\ for\ some\ s ∈ Q\}`.

        :param nfa: input NFA.
        :return: *dfa* representing a DFA
        """
        Q = set()
        Sigma = self.alphabet.copy()
        q0 = 'q0'
        delta = {}
        F = set()


        initial_states = self.epsilon_closure[self.startState]
        if len(initial_states) > 0:
            q0= self.states_to_str(initial_states)
            Q.add(q0)

        sets_states = list()
        sets_queue = list()
        sets_queue.append(initial_states)
        sets_states.append(initial_states)
        if len(sets_states[0].intersection(self.acceptStates)) > 0:
            F.add(self.states_to_str(sets_states[0]))

        while sets_queue:
            current_set = sets_queue.pop(0)
            for a in self.alphabet:
                next_set = set()
                for state in current_set:
                    if (state, a) in self.transition:
                        for next_state in self.transition[state, a]:
                            next_set.add(next_state)
                if len(next_set) == 0:
                    continue
                new_next_set = set()
                for s in next_set:
                    new_next_set.update(self.epsilon_closure[s])
                next_set = new_next_set
                s_next_set = self.states_to_str(next_set)
                s_current_set = self.states_to_str(current_set)
                if next_set not in sets_states:
                    sets_states.append(next_set)
                    sets_queue.append(next_set)
                    s_next_set = self.states_to_str(next_set)
                    Q.add(s_next_set)
                    if next_set.intersection(self.acceptStates):
                        F.add(s_next_set)

                delta[s_current_set, a] = s_next_set

        return DFA(Q,Sigma,q0,delta,F)


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

    def traces_to_deduction(self):
      result = []
      for t in self.history_traces:
        result.append('   '+'\n|- '.join([self.id_to_str(id) for id in t]))
      return result

    def deduction_to_trace(self,deduction):
      return [({q},pos) for q,pos in deduction]

    def get_deduction(self, accept=True):
      for trace in self.history_traces:
        if (trace[-1][0] in self.acceptStates and trace[-1][1]==len(self.word)) == accept:
          return trace
      return self.get_initial_ids[0]

    def traces_to_deduction_print(self):
      print('\n\n'.join(self.traces_to_deduction()))

    def trace_visualizar(self,highlight=[], nfa_name = '', size=None):  
        return self.trace_display(highlight=highlight, nfa_name = nfa_name,size=size)

    def trace_display(self,highlight=[], nfa_name = '', size=None):
        f = Digraph('finite automata '+nfa_name, filename='nfa.gv')
        f.attr(rankdir='LR')
        if size!=None:
          f.attr(size=size)
 
        f.attr('node', shape='point')
        f.node('')
 
        for index, (set_n, pos) in enumerate(self.trace):
          shapeType = 'circle'
          for n in sorted(list(set_n)):
            if n in self.acceptStates:
              shapeType = 'doublecircle'
              break
          f.node(str(index),shape=shapeType,label=self.states_to_str(set_n))
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
      for palavra in cases_test.keys():
        lResult.append(self.aceita(palavra))
      df['Resultado'] =lResult
      df.reset_index(inplace=True)
      df.rename(columns={'index':'Palavra'},inplace=True)
      acertos = df['Esperado'][df['Esperado']==df['Resultado']].count()
      casos = len(lResult)
      display('Acertou {:.2f}% ({} de {})'.format(acertos/casos*100, acertos, casos))
      display(df)

    def tabela(self):
      self.table()

    def table(self):
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
      for a in sorted(list(self.alphabet)+['']):
        l = []
        for s in sorted_states:
          if (s,a) in self.transition.keys():
            l.append('{'+', '.join([s for s in sorted(list(self.transition[s,a]))])+'}')
          else:
            l.append('∅')
        if a=='':
          d_tabela["𝜖"] = l
        else:
          d_tabela[a] = l
      df = pd.DataFrame(d_tabela)
      display(df.style.hide_index()) 


    def visualizar(self,highlight=[],highlightNonDeterministic=False, label = '', size=None):  
      return self.display(highlight=highlight,highlightNonDeterministic=highlightNonDeterministic, label = label, size=size)

    def display(self,highlight=[],highlightNonDeterministic=False, label = '', size=None): 
        f = Digraph('finite automata '+label, filename='nfa.gv')
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
        s = Digraph('word'+self.word, filename='word.gv',
                    node_attr={'shape': 'record','width':'0.1'})
        q, pos = id

        s.node('',shape='point')
        fields = ['<f{}>{}'.format(i,a) for i,a in enumerate(self.word+' ')]
        s.node('word', "|".join(fields))
        s.edges([('', 'word:f{}'.format(pos))])

        return s      


    def begin_display(self, id=None, pausa = 0.8, size=None):
        if id==None: id = self.trace[0]
        # Inicializa os displays
        d_word = display(self.display_word(id),display_id=True)
        d_NFA = display(self.visualizar(highlight=list(id[0]),size=size),display_id=True)
        return d_word, d_NFA

    def display_id(self, id, d_word, d_NFA, pausa = 0.8, pausa_entre_ids = 0, size=None):
      if(pausa_entre_ids>0):
        d_NFA.update(self.visualizar(highlight=[],size=size))
        sleep(pausa_entre_ids)

      d_word.update(self.display_word(id))
      d_NFA.update(self.visualizar(highlight=list(id[0]),size=size))
      sleep(pausa)

    def simular(self, word='', pausa = 0.8, size=None):
      self.simulate(word=word, pausa = 0.8, size=size)
    def simulate(self, word='', pausa = 0.8, size=None):
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
          if only_trace.value:
            if self.result:
              self.trace = self.deduction_to_trace(self.get_deduction())
            else:
              self.trace = self.deduction_to_trace(self.get_deduction(accept=False))
          # Inicializa os displays
          self.d_word, self.d_NFA = self.begin_display(self.trace[0], size=size)
          self.step_simulation = 0
        else:
          self.step_simulation += 1
          self.display_id(self.trace[self.step_simulation], self.d_word, self.d_NFA, pausa = pausa, pausa_entre_ids = 0.1, size=size)
        if(self.step_simulation==len(self.trace)-1):
          with output:
            if self.result: print(f"{bcolors.OKBLUE}A palavra {input.value} foi aceita.\n")
            else: print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por nenhuma computação. Veja um exemplo:\n")
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
        only_trace.disabled = True
        if self.d_NFA == None:
          # Inicializa a MT
          self.keep_traces = True          
          self.result = self.accept(input.value)
          if only_trace.value:
            if self.result:
              self.trace = self.deduction_to_trace(self.get_deduction())
            else:
              self.trace = self.deduction_to_trace(self.get_deduction(accept=False))
          # Inicializa os displays
          self.d_word, self.d_NFA = self.begin_display(self.trace[0], size=size)
          self.step_simulation = 0
        while self.step_simulation<len(self.trace):
          self.display_id(self.trace[self.step_simulation], self.d_word, self.d_NFA, pausa = pausa, pausa_entre_ids = 0.1, size=size)
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
        only_trace.disabled = False
        only_trace.value = True
        input.value = word
        clear_output()
        display(allButtons,output)
        self.d_NFA = None
        self.d_word = None
        output.clear_output()

      reset.on_click(clear)

