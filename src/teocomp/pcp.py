import pandas as pd
from IPython.display import HTML
from IPython.display import display

class PCP:
  def __init__(self, pcp):
    self.pcp = pcp

  def to_dataframe(self):
    lI = []
    l0 = []
    l1 =[]
    lC =[]
    i = 1
    for p in self.pcp:
      lI.append('i'+str(i))
      i+=1
      l0.append(p[0])
      l1.append(p[1])
      lC.append(p[1])
    d_pcp = {'indices':lI, 'Lista A':l0, 'Lista B':l1 }
    df = pd.DataFrame.from_dict(d_pcp)
    return df
  
  def display(self):
    display(HTML(self.to_dataframe().to_html(index=False)))

  def display_solution(self, index_solution):
    lA = [self.pcp[s-1][0] for s in index_solution]
    lB = [self.pcp[s-1][1] for s in index_solution]
    lIndices = ['i'+str(i) for i in index_solution]
    data = {'Lista A': lA, 'Lista B': lB}
    df = pd.DataFrame.from_dict(data, orient='index',
                        columns=lIndices)
    display(HTML(df.to_html()))

  def get_solution(self,index_solution):
    w= ''
    x= ''
    for c in index_solution:
      w += self.pcp[c-1][0]
      x += self.pcp[c-1][1]
    return (w,x)

  def is_solution(self,index_solution):
    w, x = self.get_solution(index_solution)
    return w==x
  
  def __eq__(self, other):
    return set(self.cpc)==set(other.cpc)

  def size(self):
    return len(self.pcp)

