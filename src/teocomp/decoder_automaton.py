import ruamel.yaml
from teocomp.dfa import DFA
from teocomp.nfa_e import NFA_E
from teocomp.nfa import NFA


def decode_dfa(input_dfa: str):
  data_dfa = input_dfa.replace('=',':').replace('{','[').replace('}',']').replace('(','[').replace(')',']')
  yaml = ruamel.yaml.YAML(typ='safe')
  data = yaml.load(data_dfa)
  Q = set([str(s) for s in data['Q']])
  Sigma = set([str(s) for s in data['Sigma']])
  q0 = data['q0']
  F = set([str(s) for s in data['F']])
  delta = {}
  for t in data['delta']:
    delta[str(t[0]),str(t[1])] = str(t[2])
  return DFA(Q,Sigma,q0,delta,F)


def decode_nfa(input_nfa_e: str, is_nfa_epsilon=True):
  data_nfa_e = input_nfa_e.replace('=',':').replace('{','[').replace('}',']').replace('set()','[]').replace('(','[').replace(')',']')
  yaml = ruamel.yaml.YAML(typ='safe')
  data = yaml.load(data_nfa_e)
  Q = set([str(s) for s in data['Q']])
  Sigma = set([str(s) for s in data['Sigma']])
  q0 = data['q0']
  F = set([str(s) for s in data['F']])
  delta = {}
  for t in data['delta']:
    delta[str(t[0]),str(t[1])] = set([str(s) for s in t[2]])
  if(is_nfa_epsilon):
    return NFA_E(Q,Sigma,q0,delta,F)
  else:
    return NFA(Q,Sigma,q0,delta,F)
