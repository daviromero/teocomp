from teocomp.pcp import PCP

PCPM_1 = [('A','AB'), ('B','CA'), ('CA','A'),('ABC','C')]
PCPM_2 = [('A','AB'), ('CA','A'),('B','CA'), ('ABC','C')]
PCPM_3 = [('A','AB'), ('ABC','C'), ('B','CA'), ('CA','A')]
PCPM_4 = [('A','AB'), ('B','CA'), ('ABC','C'), ('CA','A')]
PCPM_5 = [('A','AB'), ('BC', 'CA'), ('AB', 'C'),('CA','A')]
PCPM_6 = [('A','AB'), ('AB', 'C'),('BC', 'CA'), ('CA','A')]
PCPM_7 = [('A','AB'), ('CA','A'), ('BC', 'CA'), ('AB', 'C')]
PCPM_8 = [('A','AB'), ('BC', 'CA'),('CA','A'), ('AB', 'C')]
PCPM_n = [PCPM_1, PCPM_2, PCPM_3, PCPM_4, PCPM_5, PCPM_6, PCPM_7, PCPM_8 ]

class PCPM(PCP):
  def __init__(self, pcpm):
    super().__init__(pcpm)

  def is_solution(self,index_solution):
    return super().is_solution(index_solution) and index_solution!= [] and index_solution[0]==1

  def to_PCP(self):
    pcp = []
    w_0 = '*'
    for a in self.pcp[0][0]:
      w_0 += a+'*'
    x_0 = ''
    for b in self.pcp[0][1]:
      x_0 += '*'+b
    pcp.append((w_0,x_0))
    for p in self.pcp:
      new_a = ''
      for a in p[0]:
        new_a += a+'*'
      new_b = ''
      for b in p[1]:
        new_b += '*'+b
      pcp.append((new_a,new_b))
    pcp.append(('$','*$'))
    return pcp

  def solution_PCMP_to_solution_PCP(self, index_solution_pcpm):
    index_solution_pcp = [1]
    for c in index_solution_pcpm[1:]:
      index_solution_pcp.append(c+1)
    index_solution_pcp.append(len(self))
    return index_solution_pcp
