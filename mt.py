from mt_ndmf import MTNDMF, S_BLK
import xmltodict

class MT(MTNDMF):

    @staticmethod
    def jffToMT(input_jff):
          """ Convert a jff input as a Turing Machine.

          :param: jff input;
          :return: *(dict)* representing a Turing Machine.
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
          for t in xmlFile['structure']['automaton']['transition']:
            sFrom = states_aux[t["from"]]
            sTo = states_aux[t["to"]]
            sRead = t["read"] if t["read"]!=None else S_BLK
            sWrite = t["write"] if t["write"]!=None else S_BLK
            sMove = t["move"]
            delta[sFrom,sRead] = (sTo, sWrite,sMove)
            if sRead != S_BLK: Sigma.add(sRead)
            if sWrite != S_BLK: Sigma.add(sWrite)
            Gamma.add(sRead)
            Gamma.add(sWrite)
          return Q,Sigma,Gamma,delta,q0,F


    def __init__(self, Q=[], Sigma=[], Gamma=[], delta={}, q0=0, blank_as=S_BLK, F=set(), MTs={},input_jff=None):
        if input_jff != None:          
          Q,Sigma,Gamma,delta,q0,F = MT.jffToMT(input_jff)
        super().__init__(Q,Sigma,Gamma,{x:{delta[x]} for x in delta},q0,blank_as, F,MTs)
