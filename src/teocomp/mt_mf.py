from teocomp.mt_ndmf import MTNDMF, S_BLK
import xmltodict


class MTMF(MTNDMF):
    @staticmethod
    def jffToMT(input_jff):
          """ Convert a jff input as a Multi Tape Turing Machine.

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
              sMove = t["move"][i]["#text"] if "#text" in t["move"][i] else ' '
              listTo.append(sMove)
            delta[tuple(listFrom)] = tuple(listTo)

          return Q,Sigma,Gamma,delta,q0,F


    def __init__(self, Q=[], Sigma=[], Gamma=[], delta={}, q0=0,blank_as=S_BLK,  F=set(),input_jff=None):
        if input_jff != None:          
          Q,Sigma,Gamma,delta,q0,F = MTMF.jffToMT(input_jff)

        super().__init__(Q,Sigma,Gamma,{x:{delta[x]} for x in delta},q0,blank_as,F)
