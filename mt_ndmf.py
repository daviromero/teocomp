import xmltodict
from graphviz import Digraph
from time import sleep
import ipywidgets as widgets
from IPython.display import clear_output
from IPython.display import display
import pandas as pd
from bcolors import bcolors

S_EPSILON = '\u03B5' # ε
S_BLK = ' '
S_BLK_U = '\u2294' # ⊔
S_BLK_BOX = '\u2610' # ☐
S_LEFT_ANGLE_BRACKET = '\u2329' # 〈
S_RIGHT_ANGLE_BRACKET = '\u232a' # 〉

class MTNDMF: # Máquina de Turing Não-Determinística Multi-fita

    default = {'blank':' ','right':'R','left':'L','stationary':'S','separador':';','separador_tape':'|'}

    @staticmethod
    def valida(Q={}, Sigma={}, Gamma={}, delta={}, q0=0, blank_as=S_BLK,  F=set()):
      b = True
      ERROR = []
      if not blank_as in Gamma:
        b = False
        ERROR.append(f"{blank_as} não está em Gamma")
      if blank_as in Sigma:
        b = False
        ERROR.append(f"{blank_as} está em Sigma")
      if not q0 in Q:
        b = False
        ERROR.append(f"{q0} não está em Q")
      if not F.issubset(Q):
        b = False
        ERROR.append(f"{F} não é subconjunto de Q")
      if not Sigma.issubset(Gamma):
        b = False
        ERROR.append(f"Sigma não é subconjunto de Gamma")
      ntapes = max([len(t)-1 for t in delta])
      for d in delta.keys():
        q = d[0]
        if not q in Q:
          b = False
          ERROR.append(f"Na transição delta({d}), {q} não está em Q")
        for i in range(1,ntapes+1):
          if not d[i] in Gamma:
            b = False
            ERROR.append(f"Na transição delta({d}), {d[i]} não está em Gamma")
        for t in delta[d]:
          q = t[0]
          if not q in Q:
            b = False
            ERROR.append(f"Na transição delta({d})={t}, {q} não está em Q")
          for i in range(1,ntapes+1):
            if not t[i] in Gamma:
              b = False
              ERROR.append(f"Na transição delta({d})={t}, {t[i]} não está em Gamma")
          for i in range(ntapes+1,2*ntapes+1):
            if not t[i] in {'S','L','R'}:
              b = False
              ERROR.append(f"Na transição delta({d})={t}, {t[i]} não é um movimento válido")
      return b, ERROR

    @staticmethod
    def jffToMT(input_jff):
          """ Convert a jff input as a Multi Tape Non-Deterministic Turing Machine.

          :param: jff input;
          :return: *(dict)* representing a Multi Tape Turing Machine.
          """
          xmlFile = xmltodict.parse(input_jff)
          
          Q = set()
          Sigma = set()
          Gamma = set()
          Gamma.add(S_BLK)
          delta = {}
          F = set()
          q0 = None

          states_aux = {}

          for s in xmlFile['structure']['automaton']['state']:
            states_aux[s["@id"]] = s["@name"]
            Q.add(s["@name"])
            if 'initial' in s:
              q0 = s["@name"]
            if 'final' in s:
              F.add(s["@name"])
          if 'tapes' in xmlFile['structure']:
            nTapes = int(xmlFile['structure']['tapes'])
          else:
            nTapes = 1
          for t in xmlFile['structure']['automaton']['transition']:
            sFrom = states_aux[t["from"]]
            sTo = states_aux[t["to"]]
            listFrom = [sFrom]
            listTo = [sTo] 
          
            for i in range(nTapes):
              sRead = t["read"][i]["#text"] if "#text" in t["read"][i] else S_BLK
              sWrite = t["write"][i]["#text"] if "#text" in t["write"][i] else S_BLK
              listFrom.append(sRead)
              listTo.append(sWrite)
              if sRead != S_BLK: Sigma.add(sRead)
              if sWrite != S_BLK: Sigma.add(sWrite)
              Gamma.add(sRead)
              Gamma.add(sWrite)
            for i in range(nTapes):
              sMove = t["move"][i]["#text"] if "#text" in t["move"][i] else S_BLK
              listTo.append(sMove)
            if tuple(listFrom) in delta: delta[tuple(listFrom)].add(tuple(listTo))
            else: delta[tuple(listFrom)] = {tuple(listTo)}
          return Q, Sigma, Gamma, delta, q0, F

    def __init__(self, Q={}, Sigma={}, Gamma={}, delta={}, q0=0, blank_as=S_BLK,  F=set(), MTs={}, input_jff=None):
        if input_jff != None:          
          Q,Sigma,Gamma,delta,q0,F = MTNDMF.jffToMT(input_jff)

        b, ERROR = MTNDMF.valida(Q,Sigma,Gamma,delta,q0,blank_as,F)
        if not b: 
          print(f"{bcolors.FAIL}Os seguintes erros foram encontrados:\n")
          print(',\n'.join(ERROR))

        self.states = Q
        self.inputAlphabet = Sigma
        self.tapeAlphabet = Gamma
        self.transition = delta
        self.startState = q0
        self.acceptStates = F
        self.traces = []
        self.MTs = MTs
        self.blank_sym = blank_as#self.default['blank']
        self.left_sym = self.default['left']
        self.right_sym = self.default['right']

        self.keep_traces = True
        self.show_steps = False
        self.ntapes = max([len(t)-1 for t in self.transition])
 
        self.iniciar()

 
    def defaults():
        return __class__.default['blank'], __class__.default['right'], __class__.default['left']
 
    def config(self, blank_sym=None, right_sym=None, left_sym=None, keep_traces=None):
        if blank_sym != None: self.blank_sym = blank_sym 
        if left_sym != None: self.left_sym = left_sym
        if right_sym != None: self.right_sym = right_sym
        if keep_traces != None: self.keep_traces = keep_traces
 
  
    def hasNext(self):
        return self.traces and (not self.acceptTraces())
    
    def acceptTraces(self):
        return [t for t in self.traces if t[-1][0] in self.acceptStates and t[-1][3]==self]
        
    def getQ0(self):
      return self.startState

    def getTransition(self):
      return self.transition
      
    def getTraces(self):
      return self.traces

    def getNameMT(self, M):
      for name, MTNDMF in self.MTs.items():  # retorna o nome da MT
        if MTNDMF == M: return name
      return ''

        # Uma descrição instântanea é formada por:
        #     - estado
        #     - lista de posições (cabeças das fitas)
        #     - lista do conteúdos das fitas 
        #     - Máquina de Turing
        # Inicializa a lista de Trace com um único trace, contendo a ID inicial
        # Uma lista de Traces, na qual cada trace é formada por uma lista de descrições instântaneas (histórico).
    def iniciar(self, input_string_tapes='', head_tapes=None, start_state=None):
        if start_state != None: self.startState = start_state
        if head_tapes==None:
          head_tapes = [0]*(self.ntapes)
        if type(input_string_tapes) is list:
            input_string_tapes = [list(input_string) for input_string in input_string_tapes]
        else: 
          input_list = list(input_string_tapes) if input_string_tapes else [self.blank_sym]
          input_list = input_list + [self.blank_sym]*(1-len(input_list))
          input_string_tapes = [input_list] + [[self.blank_sym]]*(self.ntapes-1)
        self.startId = (self.startState, head_tapes, input_string_tapes, self)
        self.traces = [ [self.startId] ]         

    def aceita(self, input_string_tapes=None, head_tapes=None, start_state=None, max_steps=1000,show_steps=False):
        self.iniciar(input_string_tapes=input_string_tapes, head_tapes=head_tapes, start_state=start_state)
        if (show_steps):
          self.print_snapshot()
        return self.executar(show_steps=show_steps,max_steps=max_steps)

    def executar(self, max_steps=1000,show_steps=False):   
        while (self.hasNext()): 
          if max_steps == 0: 
            return "Timeout"
          self.step()
          max_steps -= 1
          if (show_steps): 
            self.print_snapshot()
        return self.resultado()
 
    def resultado(self):
        return True if self.acceptTraces() else (False if (not self.traces) else None)

    def step(self):
      updated_traces = []
      for trace in self.traces:
        q, head, tape, M = trace[-1]
        if q in self.MTs:
          M = self.MTs[q]
          if (self.keep_traces):
            updated_traces.append(trace+[(M.startState,head,tape,M)])    
          else:
            updated_traces.append([(M.startState,head,tape,M)])        
        else:
          args = (q,) + tuple([tape[i][h] for i,h in enumerate(head)])            
          if (args in M.getTransition()):
            for values in M.getTransition()[args]:
              h = head[:]
              t = [t[:] for t in tape[:]]
              r = values[0]
              b = values[1:self.ntapes+1]
              m = values[self.ntapes+1:]
              for i in range(self.ntapes):
                t[i][h[i]] = b[i]
                h[i] += 1 if m[i] == self.right_sym else -1 if m[i] == self.left_sym else 0
                if h[i] < 0:
                  h[i] = 0
                  t[i]= [self.blank_sym] +t[i]
                h[i] = 0 if h[i] < 0 else h[i]
                t[i] += [self.blank_sym] if h[i] == len(t[i]) else []
              if (self.keep_traces):
                updated_traces.append(trace+[(r,h,t,M)])    
              else:
                updated_traces.append([(r,h,t,M)])            
          else:
            # Se a máquina não é essa e ela pára e a atual máquina tem q executar a sua transição.
            if M!= self:
              stateName  = self.getNameMT(M)
              args = (stateName,) + tuple([tape[i][h] for i,h in enumerate(head)])
              if (args in self.getTransition()):
                for values in self.getTransition()[args]:
                  h = head[:]
                  t = [t[:] for t in tape[:]]
                  r = values[0]
                  b = values[1:self.ntapes+1]
                  m = values[self.ntapes+1:]
                  for i in range(self.ntapes):
                    t[i][h[i]] = b[i]
                    h[i] += 1 if m[i] == self.right_sym else -1 if m[i] == self.left_sym else 0
                    if h[i] < 0:
                      h[i] = 0
                      t[i]= [self.blank_sym] +t[i]
                    h[i] = 0 if h[i] < 0 else h[i]
                    t[i] += [self.blank_sym] if h[i] == len(t[i]) else []
                  if (self.keep_traces):
                    updated_traces.append(trace+[(r,h,t,self)])    
                  else:
                    updated_traces.append([(r,h,t,self)])
      self.traces = updated_traces         

    def display_resultados(self, casos_testes, max_steps=1000):
      df = pd.DataFrame.from_dict(casos_testes,orient='index',
                       columns=['Esperado'])
      lResult = []
      for palavra in casos_testes.keys():
        lResult.append(self.aceita(palavra,max_steps=max_steps))
      df['Resultado'] =lResult
      df.reset_index(inplace=True)
      df.rename(columns={'index':'Palavra'},inplace=True)
      acertos = df['Esperado'][df['Esperado']==df['Resultado']].count()
      casos = len(lResult)
      print('Acertou {:.2f}% ({} de {})'.format(acertos/casos*100, acertos, casos))
      display(df)

    def print_snapshot(self):
      ntraces = 1
      sTraces = []
      for key in self.snapshot().keys():
        if(key[0]>ntraces):
          ntraces = key[0]
      for n in range(ntraces):
        sIds = ''
        if(self.ntapes>1):
          sIds = '['#S_LEFT_ANGLE_BRACKET             
        for i in range(self.ntapes):
          if(i>0): sIds+=', '
          if (n,i) in self.snapshot():
            sIds += self.snapshot()[n,i]
        if(self.ntapes>1): sIds += ']'#S_RIGHT_ANGLE_BRACKET 
        if sIds!='': sTraces.append(sIds) 
      if sTraces != []:
        print(', '.join(sTraces))

    def snapshot_id_tape(self, id, tape_i):
      q, head, tape, M = id
      if M!= self: 
        return f"{self.getNameMT(M)+':'+''.join(tape[tape_i][:head[tape_i]])}{bcolors.OKBLUE}{q}{bcolors.ENDC}{''.join(tape[tape_i][head[tape_i]:])}"
      if self.MTs == {}:
        return f"{''.join(tape[tape_i][:head[tape_i]])}{bcolors.OKBLUE}{q}{bcolors.ENDC}{''.join(tape[tape_i][head[tape_i]:])}"
      else:
        return f"{'self:'+''.join(tape[tape_i][:head[tape_i]])}{bcolors.OKBLUE}{q}{bcolors.ENDC}{''.join(tape[tape_i][head[tape_i]:])}"

    def snapshot(self):
        snap = {}
        for n, trace in enumerate(self.traces):
          for i in range(self.ntapes):
            snap[(n,i)] = self.snapshot_id_tape(trace[-1],i)
        return snap

    def snapshot_all(self, size=10):
      l = []
      for i in range(self.ntapes):
        l.append(self.graphic_snapshot(size=size, tape_i=i))
      return l

    def graphic_snapshot_all(self, size=10):
      l = self.snapshot_all()
      for i in l:
        display(i)

    def display(self,blank_as=S_BLK_BOX,highlight=[],highlightNonDeterministic=False, turing_name = '', tape_size=10):
      display(self.visualizar(blank_as=blank_as,highlight=highlight, highlightNonDeterministic=highlightNonDeterministic, turing_name = turing_name))
      self.graphic_snapshot_all(size=tape_size)

    def graphic_snapshot(self,id=None, size=10, tape_i=0):
        s = Digraph('tape '+str(tape_i+1), filename='tm_snapshot.gv',
                    node_attr={'shape': 'record','width':'0.1'})
        if id==None:
          id = self.traces[0][-1]
        q, head, tape, M = id
        
        if M != self:
          s.node('state', '<f0>{}:{}'.format(self.getNameMT(M),q))
        else:
          s.node('state', '<f0>{}'.format(q))
        h = head[tape_i]
        t = ['...']+ [self.blank_sym]+tape[tape_i] + [self.blank_sym]*(size-1-len(tape[tape_i])) + ['...']
        fields = ['<f{}>{}'.format(i,a) for i,a in enumerate(t)]
        s.node('tape', "|".join(fields))
        s.edges([('state:f0', 'tape:f{}'.format(head[tape_i]+2))])

        return s      

    def visualizar(self,blank_as=S_BLK_BOX,highlight=[],highlightNonDeterministic=False, turing_name = ''):             
        f = Digraph('turing machine '+turing_name, filename='tm.gv')
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
        for key in self.transition:
          for value in self.transition[key]:    
            q,r = key[0],value[0]
            nlabel = ''
            for i in range(self.ntapes):
              if(i>0): nlabel += '{}'.format(self.default['separador_tape'])
              nlabel += '{}{}{},{}'.format(str(key[i+1]),str(self.default['separador']),str(value[i+1]),str(value[self.ntapes+i+1]))
            nlabel = nlabel if blank_as == None else nlabel.replace(self.blank_sym,blank_as)
            label[q,r] = label[q,r]+'\n'+nlabel if (q,r) in label else nlabel

        nonDeterministic = {}
        if highlightNonDeterministic:
          for key in self.transition:
            if len(self.transition[key])>1:
              for value in self.transition[key]:    
                nonDeterministic[key[0],value[0]] = True

        for (q,r) in label:
          if highlightNonDeterministic and (q,r) in nonDeterministic:
            f.edge(str(q),str(r),label=label[q,r],color="blue")#,fontcolor="blue")      
          else:
            f.edge(str(q),str(r),label=label[q,r])      

        return f

    def inicializar_vizualizacao(self, id=None, blank_as=S_BLK_BOX, tamanho_fita = 10, pausa = 0.8, show_other_MTs= True):
        if id==None: id = self.startId
        q, head, tape, M = id
        # Inicializa os displays
        d_MT = display(self.visualizar(highlight=[],blank_as=blank_as),display_id=True)
        d_MTs = {}
        if(show_other_MTs):
          for mt in self.MTs.items():
            d_MTs[mt[0]] = display(mt[1].visualizar(highlight=[],blank_as=blank_as),display_id=True)
        d_Tapes = []
        for i in range(self.ntapes):
          d_Tapes.append(display(self.graphic_snapshot(id,size=tamanho_fita, tape_i=i),display_id=True))

        if M== self:
          d_MT.update(self.visualizar(highlight=[q],blank_as=blank_as))
        else:
          if(show_other_MTs):
            d_MTs[self.getNameMT(M)].update(M.visualizar(highlight=[q],blank_as=blank_as))
        sleep(pausa)
        return d_MT, d_MTs, d_Tapes

    def visualizar_id(self, id, d_MT, d_MTs, d_Tapes, blank_as=S_BLK_BOX, tamanho_fita = 10, pausa = 0.8, pausa_entre_ids = 0, show_other_MTs= True):
      q, head, tape, M = id

      if(pausa_entre_ids>0):
        if (M==self):
          d_MT.update(self.visualizar(highlight=[],blank_as=blank_as))
        if(show_other_MTs):
          for mt in self.MTs.items():
            d_MTs[mt[0]].update(mt[1].visualizar(highlight=[],blank_as=blank_as))
        sleep(pausa_entre_ids)

      for i in range(self.ntapes):
        d_Tapes[i].update(self.graphic_snapshot(id,size=tamanho_fita, tape_i=i))
      if M== self:
        d_MT.update(self.visualizar(highlight=[q],blank_as=blank_as))
        if(show_other_MTs):
          for mt in self.MTs.items():
            d_MTs[mt[0]].update(mt[1].visualizar(highlight=[],blank_as=blank_as))
      else:
        if(show_other_MTs):
          d_MTs[self.getNameMT(M)].update(M.visualizar(highlight=[q],blank_as=blank_as))
      sleep(pausa)

    def visualizar_computacao(self, input_string_tapes='', head_tapes=None, start_state=None, max_steps=1000, blank_as=S_BLK_BOX,tamanho_fita = 10, pausa = 0.8, show_other_MTs= True):
      self.keep_traces = True
      aceita = self.aceita(input_string_tapes=input_string_tapes,  start_state=start_state, head_tapes=head_tapes, show_steps=False, max_steps=max_steps)

      if type(input_string_tapes) is list:
        input_string = input_string_tapes[0]#''.join(input_string_tapes[0])
      else:
        input_string = input_string_tapes

      if aceita == True:
        print(f"{bcolors.OKBLUE}A palavra {input_string} foi aceita pela seguinte computação:\n")
        # Exibe o trace aceito mais à esquerda
        trace = self.acceptTraces()[0]
        # Inicializa os displays
        d_MT, d_MTs, d_Tapes = None, None, None
        for id in trace:
          if d_MT==None:
            d_MT, d_MTs, d_Tapes = self.inicializar_vizualizacao(id, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, show_other_MTs=show_other_MTs)
          else:          
            self.visualizar_id(id, d_MT, d_MTs, d_Tapes, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, pausa_entre_ids = 0.02,show_other_MTs=show_other_MTs)
      else:
        if aceita == "Timeout": print(f"{bcolors.FAIL}A palavra {input_string} não foi aceita em {max_steps} passos. Veja um exemplo:")
        else: print(f"{bcolors.FAIL}A palavra {input_string} não foi aceita por nenhuma computação. Veja um exemplo:")
        # Inicializa a MT
        self.iniciar(input_string_tapes=input_string_tapes,  start_state=start_state, head_tapes=head_tapes)
        id_inicial = self.startId#self.traces[0][0]
        # Inicializa os displays
        d_MT, d_MTs, d_Tapes = self.inicializar_vizualizacao(id_inicial, blank_as=blank_as, tamanho_fita = tamanho_fita, show_other_MTs=show_other_MTs)
        # Exibe o trace mais à esquerda
        #Visualiza a Id Inicial
        self.visualizar_id(id_inicial, d_MT, d_MTs, d_Tapes, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, show_other_MTs=show_other_MTs)
        # Inicia a computação
        while (self.hasNext()): 
          if max_steps == 0: 
#            print(f"{bcolors.FAIL}A palavra {input_string} não foi aceita em {max_steps} passos.")
            return False
          self.step()
          max_steps -= 1
          if not self.traces: break
          self.traces = [self.traces[0]]
          id = self.traces[0][-1]
          self.visualizar_id(id, d_MT, d_MTs, d_Tapes, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, pausa_entre_ids = 0.02, show_other_MTs=show_other_MTs)


    def simular(self, input_string='', max_steps=200, blank_as=S_BLK_BOX,tamanho_fita = 10, pausa = 0.8, show_other_MTs=True):
      layout = widgets.Layout(width='750px')
      w_max_steps = widgets.IntSlider(
          description="Max. Passos.",
          value=max_steps,
          min=10,
          step=10,
          max=1000,
          description_tooltip='Defina o número máximo de passos executados pela máquina de turing.',
          disabled=False,
          continuous_update=False,
          orientation='horizontal',
          readout=True
      )
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
      output = widgets.Output()
      wButtons = widgets.HBox([step,run,speed,w_max_steps])
      wInputBox= widgets.HBox([input, reset])
      allButtons = widgets.VBox([wInputBox,wButtons])
      display(allButtons,output)
      self.d_MT = None
      self.d_MTs = None
      self.d_Tapes = None

      def on_button_step_clicked(_):
        run.disabled = True
        speed.disabled = True
        input.disabled = True
        step.disabled = True
        w_max_steps.disabled = True
  
        if self.d_MT == None:
          # Inicializa a MT
          self.iniciar(input.value)
          #self.id_inicial = self.startId#self.traces[0][0]
          # Inicializa os displays
          self.d_MT, self.d_MTs, self.d_Tapes = self.inicializar_vizualizacao(self.startId, blank_as=blank_as, tamanho_fita = tamanho_fita, show_other_MTs=show_other_MTs)
          #Visualiza a Id Inicial
          self.visualizar_id(self.startId, self.d_MT, self.d_MTs, self.d_Tapes, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, pausa_entre_ids = 0, show_other_MTs=show_other_MTs)
        elif self.hasNext():
          self.step()
          if self.traces:
            self.traces = [self.traces[0]]
            id = self.traces[0][-1]
            self.visualizar_id(id, self.d_MT, self.d_MTs, self.d_Tapes, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, pausa_entre_ids = 0, show_other_MTs=show_other_MTs)
            if self.resultado(): 
              with output:
                print(f"{bcolors.OKBLUE}A palavra {input.value} foi aceita.\n")
              step.disabled = True
              return
          else:
            if self.resultado(): 
              with output:
                print(f"A palavra {input.value} foi aceita.\n")
            else:
              with output:
                self.keep_traces = True
                aceita = self.aceita(input.value,show_steps=False)
                if aceita==True: print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por esta computação.\n{bcolors.OKGREEN}Todavia, há uma computação que reconhece essa palavra. Clique no botão Simular para visualizar uma computação que reconhece essa palavra.")
                elif aceita == "Timeout": print(f"{bcolors.FAIL}A palavra {input_string} não foi aceita em {w_max_steps.value} passos.")
                else: print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por nenhuma computação.\n")
            step.disabled = True
            return
        else:
          if not self.resultado():
            with output:
              print(f"{bcolors.FAIL}A palavra {input.value} não foi aceita por nenhuma computação.\n")
            step.disabled = True
            return
        step.disabled = False

      step.on_click(on_button_step_clicked)

      def on_button_run_clicked(_):
        reset.disabled = True
        step.disabled = True
        run.disabled = True
        input.disabled = True
        speed.disabled = True
        w_max_steps.disabled = True
        self.visualizar_computacao(input.value, pausa = speed.value,max_steps=w_max_steps.value, show_other_MTs=show_other_MTs)
        reset.disabled = False

      run.on_click(on_button_run_clicked)

      def clear(_):
        speed.value =0.8
        speed.disabled = False
        reset.disabled = False
        step.disabled = False
        run.disabled = False
        input.disabled = False
        w_max_steps.disabled = False
        w_max_steps.value = max_steps
        input.value = input_string
        clear_output()
        display(allButtons,output)
        self.d_MT = None
        self.d_MTs = None
        self.d_Tapes = None
        output.clear_output()

      reset.on_click(clear)



    def simular_set_start_id(self, input_string='', max_steps=200, blank_as=S_BLK_BOX,tamanho_fita = 10, pausa = 0.8, show_other_MTs=True):
      layout = widgets.Layout(width='850px')
      w_max_steps = widgets.IntSlider(
          description="Max. Passos.",
          value=max_steps,
          min=10,
          step=10,
          max=1000,
          description_tooltip='Defina o número máximo de passos executados pela máquina de turing.',
          disabled=False,
          continuous_update=False,
          orientation='horizontal',
          readout=True
      )
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
      wInputs_1 = [widgets.Text(placeholder=f'Prefixo da Fita {i+1}') for i in range(self.ntapes)]
      wInputs_2 = [widgets.Text(placeholder=f'Sufixo da Fita {i+1}') for i in range(self.ntapes)]
      if type(input_string) is list:
        wInputs_2 = [widgets.Text(value=input_string[i], placeholder=f'Sufixo da Fita {i+1}') for i in range(self.ntapes)]
      else:
        wInputs_2 = [widgets.Text(placeholder=f'Sufixo da Fita {i+1}') for i in range(self.ntapes)]
        wInputs_2[0].value=input_string
      wStates = widgets.Dropdown(description="Estado:",options=sorted(list(self.states)),value=self.startState,style= {'description_width': '0px'})      
      wText = widgets.HTML(value="Defina a Descrição Instantânea Inicial da Máquina de Turing")
      wAll = widgets.HBox([widgets.VBox(wInputs_1),wStates,widgets.VBox(wInputs_2)])

      output = widgets.Output()
      wButtons = widgets.HBox([reset,step,run,speed,w_max_steps])
      display(wText,wAll,wButtons,output)
      self.d_MT = None
      self.d_MTs = None
      self.d_Tapes = None
      palavra = ''

      def get_input_id():
        state = wStates.value
        lTapes = []
        lPos = []
        for i in range(self.ntapes):
          pre_tape_i = wInputs_1[i].value
          suf_tape_i = wInputs_2[i].value if wInputs_2[i].value else ' '
          tape_i = (pre_tape_i+suf_tape_i)
          lTapes.append(tape_i) 
          pos_i = len(pre_tape_i)
          lPos.append(pos_i)
        return state, lPos, lTapes


      def on_button_step_clicked(_):
        run.disabled = True
        speed.disabled = True
        wStates.disabled = True
        for i in range(self.ntapes):
          wInputs_1[i].disabled = True
          wInputs_2[i].disabled = True
        step.disabled = True
        w_max_steps.disabled = True
        
        start_state, head_tapes, input_string_tapes = get_input_id()
        if input_string_tapes is list:
          palavra = input_string_tapes[0]
        else:
          palavra = input_string_tapes

        if self.d_MT == None:
          # Inicializa a MT
          self.iniciar(start_state=start_state, head_tapes=head_tapes, input_string_tapes=input_string_tapes)
          # Inicializa os displays
          self.d_MT, self.d_MTs, self.d_Tapes = self.inicializar_vizualizacao(self.startId, blank_as=blank_as, tamanho_fita = tamanho_fita, show_other_MTs=show_other_MTs)
          #Visualiza a Id Inicial
          self.visualizar_id(self.startId, self.d_MT, self.d_MTs, self.d_Tapes, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, pausa_entre_ids = 0, show_other_MTs=show_other_MTs)
        elif self.hasNext():
          self.step()
          if self.traces:
            self.traces = [self.traces[0]]
            id = self.traces[0][-1]
            self.visualizar_id(id, self.d_MT, self.d_MTs, self.d_Tapes, blank_as=blank_as, tamanho_fita = tamanho_fita, pausa = pausa, pausa_entre_ids = 0, show_other_MTs=show_other_MTs)
            if self.resultado(): 
              with output:
                print(f"{bcolors.OKBLUE}A palavra {palavra} foi aceita.\n")
              step.disabled = True
              return
          else:
            if self.resultado(): 
              with output:
                print(f"A palavra {palavra} foi aceita.\n")
            else:
              with output:
                self.keep_traces = True
                aceita = self.aceita(start_state=start_state, head_tapes=head_tapes, input_string_tapes=input_string_tapes,show_steps=False)
                if aceita==True: print(f"{bcolors.FAIL}A palavra {palavra} não foi aceita por esta computação.\n{bcolors.OKGREEN}Todavia, há uma computação que reconhece essa palavra. Clique no botão Simular para visualizar uma computação que reconhece essa palavra.")
                elif aceita == "Timeout": print(f"{bcolors.FAIL}A palavra {palavra} não foi aceita em {w_max_steps.value} passos.")
                else: print(f"{bcolors.FAIL}A palavra {palavra} não foi aceita por nenhuma computação.\n")
            step.disabled = True
            return
        else:
          if not self.resultado():
            with output:
              print(f"{bcolors.FAIL}A palavra {palavra} não foi aceita por nenhuma computação.\n")
            step.disabled = True
            return
        step.disabled = False

      step.on_click(on_button_step_clicked)

      def on_button_run_clicked(_):
        reset.disabled = True
        step.disabled = True
        run.disabled = True
        wStates.disabled = True
        for i in range(self.ntapes):
          wInputs_1[i].disabled = True
          wInputs_2[i].disabled = True
        speed.disabled = True
        w_max_steps.disabled = True
        start_state, head_tapes, input_string_tapes = get_input_id()
        self.visualizar_computacao(start_state=start_state, head_tapes=head_tapes, input_string_tapes=input_string_tapes, pausa = speed.value,max_steps=w_max_steps.value, show_other_MTs=show_other_MTs)
        reset.disabled = False

      run.on_click(on_button_run_clicked)

      def clear(_):
        speed.value =0.8
        speed.disabled = False
        reset.disabled = False
        step.disabled = False
        wStates.disabled = False
        for i in range(self.ntapes):
          wInputs_1[i].disabled = False
          wInputs_2[i].disabled = False
        run.disabled = False
        w_max_steps.disabled = False
        w_max_steps.value = max_steps
        clear_output()
        display(wText,wAll,wButtons,output)
        self.d_MT = None
        self.d_MTs = None
        self.d_Tapes = None
        output.clear_output()

      reset.on_click(clear)
      