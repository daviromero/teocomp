from pcpm import PCPM

class Encoder_LU_to_PCPM:
  def __init__(self, mtndmf, word, delimiter='#'):
    self.MT = mtndmf
    self.word = word
    self.delimiter = delimiter

  def encode(self):
    Gamma = self.MT.tapeAlphabet.copy()
    Gamma.remove(self.MT.blank_sym)
    #Appends the initial ID
    l = [(self.delimiter, f'{self.delimiter}{self.MT.startState}{self.word}{self.delimiter}')]
    #Appends the tape symbols and the delimiter
    l += [(x,x) for x in Gamma]+[(self.delimiter,self.delimiter)]
    #Appends the transition correspondences
    for (s_origem,t_origem) in self.MT.transition.keys():
      destino = self.MT.transition[s_origem,t_origem]
      for (s_destino, t_destino, move) in destino: 
        #print('(',s_origem,t_origem,') : (',s_destino, t_destino, move,')')
        if(move=='R'):
          if(t_origem!=self.MT.blank_sym):
            l += [(f'{s_origem}{t_origem}',f'{t_destino}{s_destino}')]
          else:
            l += [(f'{s_origem}{self.delimiter}',f'{t_destino}{s_destino}{self.delimiter}')]
        elif(move=='L'):
          if(t_origem!=self.MT.blank_sym):
            l += [(f'{Z}{s_origem}{t_origem}',f'{s_destino}{Z}{t_destino}') for Z in Gamma]
          else:
            l += [(f'{Z}{s_origem}{self.delimiter}',f'{s_destino}{Z}{t_destino}{self.delimiter}') for Z in Gamma]
        elif(move=='S'):
          if(t_origem!=self.MT.blank_sym):
            l += [(f'{s_origem}{t_origem}',f'{s_destino}{t_destino}')]
          else:
            l += [(f'{s_origem}{self.delimiter}',f'{s_destino}{t_destino}{self.delimiter}')]
    #Appends the correspondece for the accept states
    for s in self.MT.acceptStates:
      for a in Gamma:
        l.append((f'{a}{s}',s))
        for b in Gamma:
          l.append((f'{a}{s}{b}',s))
        l.append((f'{s}{a}',s))
    #Appends the final correspondence
    for s in self.MT.acceptStates:
      l+= [(f'{s}{self.delimiter}{self.delimiter}',f'{self.delimiter}')]
    return PCPM(l)

