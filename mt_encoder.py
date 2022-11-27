from mt_ndmf import MTNDMF, S_BLK
from bcolors import bcolors

class Encoder_MT():    
  def __init__(self, MTNDMF,delimiter_color=True):
    self.startState = MTNDMF.startState
    self.states = MTNDMF.states
    self.blank_sym = MTNDMF.blank_sym
    self.tapeAlphabet = MTNDMF.tapeAlphabet
    self.transition = MTNDMF.transition    
    self.ntapes = MTNDMF.ntapes
    self.acceptStates = MTNDMF.acceptStates

    self.delimiter_color = delimiter_color
    self.setDelimiter_1(self.delimiter_color)
    self.setDelimiter_2(self.delimiter_color)

    self.encodeMoves()
    self.encodeStates()
    self.encodeAlphabet()
    self.encodeTransition()

  def setDelimiter_1(self,delimiter_color=True):
    self.delimiter_1 = f'{bcolors.OKBLUE}1{bcolors.ENDC}' if delimiter_color else '1'
    
  def setDelimiter_2(self,delimiter_color=True):
    self.delimiter_2 = f'{bcolors.CYELLOW}11{bcolors.ENDC}' if delimiter_color else '11'

  def encodeMoves(self,L_encode='0',R_encode='00',S_encode='000'):
    self.move_encode = {}
    self.move_encode['L'] = L_encode
    self.move_encode['R'] = R_encode
    self.move_encode['S'] = S_encode

  # Faz a codificação dos estados em 0s. O 0 será sempre o estado inicial.
  def encodeStates(self,begin_with_startState = True):
    self.states_encode = {}
    lStates = list(self.states)
    lStates.sort()
    if begin_with_startState:
      lStates.remove(self.startState)
      s = list(self.acceptStates)[0]
      lStates.remove(s)
      lStates = [self.startState,s]+lStates
    for i in range(len(lStates)):
      self.states_encode[lStates[i]]='0'*(i+1)

  def encodeAlphabet(self,end_with_blank_sym=True):
    # Faz a codificação dos símbolos do alfabeto Gamma em 0s. O símbolo branco será sempre o 0^{size(Gamma)}.
    lTapeAlphabet = list(self.tapeAlphabet)
    lTapeAlphabet.sort()
    if end_with_blank_sym:
      lTapeAlphabet.remove(self.blank_sym)
      lTapeAlphabet = lTapeAlphabet+[self.blank_sym]
    self.tapeAlphabet_encode = {}
    for i in range(len(lTapeAlphabet)):
      self.tapeAlphabet_encode[lTapeAlphabet[i]]='0'*(i+1)

  def encodeTransition(self):
    # Faz a codificação dos símbolos do alfabeto Gamma em 0s. O símbolo branco será sempre o 0^{size(Gamma)}.
    self.transition_encode = []
    for t in self.transition.keys():
      s_t = self.states_encode[t[0]]
      for i in range(self.ntapes):
        s_t += self.delimiter_1+self.tapeAlphabet_encode[t[i+1]]
      for dt in self.transition[t]:
        s_t_aux = str(s_t) + self.delimiter_1 + self.states_encode[dt[0]] 
        moves_encode = ''
        for i in range(self.ntapes):
          s_t_aux += self.delimiter_1+ self.tapeAlphabet_encode[dt[i+1]]
          moves_encode += self.delimiter_1+self.move_encode[dt[self.ntapes+i+1]]
        self.transition_encode.append(s_t_aux+moves_encode)

  def isTransition(self,s_transition):
    if self.delimiter_color: s_transition = s_transition.replace('1',self.delimiter_1) 
    return s_transition in self.transition_encode

  def equals(self, encoded_MT):
    l_transitions = encoded_MT.split('11')
    if self.delimiter_color: l_transitions = [x.replace('1',self.delimiter_1) for x in l_transitions]    
    return set(self.transition_encode) == set(l_transitions)

  @staticmethod
  def decode(encoded_MT,blank_sym=S_BLK):
    l_transitions = encoded_MT.split('11')
    l_transitions.sort()
    ntapes =  (len(l_transitions[0].split('1'))-2)//3
    Q = set()
    Sigma = set()
    Gamma = set()
    delta = {}
    F = {'q2'}
    q0 = 'q1'
    max_symbol = -1 # variável usada para encontrar o "maior" símbolo que será substituído pelo branco
    for t in l_transitions:
      l_t = t.split('1')
      l_key = []
      l_tape =[]
      l_move =[]
      q = 'q'+str(len(l_t[0]))
      r = 'q'+str(len(l_t[ntapes+1]))
      Q.add(q)
      Q.add(r)
      l_key.append(q)
      for i in range(ntapes):
        s_tape_i = len(l_t[i+1])-1
        if s_tape_i > max_symbol:
          max_symbol = s_tape_i 
        Gamma.add(str(s_tape_i))
        l_key.append(str(s_tape_i))
        s_tape_write_i = len(l_t[ntapes+i+2])-1
        if s_tape_write_i > max_symbol:
          max_symbol = s_tape_write_i
        Gamma.add(str(s_tape_write_i))        
        l_tape.append(str(s_tape_write_i))
        s_move_i = len(l_t[2*ntapes+i+2])
        s_move_i = 'L' if s_move_i == 1 else 'R' if s_move_i == 2 else 'S'
        l_move.append(s_move_i)
      if tuple(l_key) in delta: 
        delta[tuple(l_key)].add(tuple([r]+l_tape+l_move))
      else: 
        delta[tuple(l_key)] = {tuple([r]+l_tape+l_move)} 
    #Se a máquina não tem o branco 000, adiciona-o.
    if max_symbol < 2:
      Gamma.add(blank_sym)
    else:
      # Troca na função delta o último símbolo pelo branco.
      Gamma.remove(str(max_symbol))
      Sigma = Gamma.copy()
      Gamma.add(blank_sym)
      s_max_symbol = str(max_symbol)
      delta_aux = {}
      for t in delta.keys():
        hasBlank = False
        new_key = t
        if(s_max_symbol in t[1:ntapes+1]):
          l_key = [t[0]]
          for i in range(ntapes):
            if(t[i+1]==s_max_symbol): l_key.append(blank_sym)
            else: l_key.append(t[i+1])
          l_key+= t[1+ntapes:]
          new_key = tuple(l_key)
          hasBlank = True
        new_dt = set()
        for dt in delta[t]:
          if(s_max_symbol in dt[1:ntapes+1]):
            l_dt = [dt[0]]
            for i in range(ntapes):
              if(dt[i+1]==s_max_symbol): l_dt.append(blank_sym)
              else: l_dt.append(dt[i+1])
            l_dt+= dt[ntapes+1:]
            new_dt.add(tuple(l_dt))
            hasBlank = True
          else:
            new_dt.add(dt)
        if hasBlank: delta_aux[new_key] = new_dt
        else: delta_aux[t] = delta[t]
      delta = delta_aux
    return MTNDMF(Q,Sigma,Gamma,delta,q0,blank_sym,F)