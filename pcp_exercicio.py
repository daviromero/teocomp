from IPython.display import display
import ipywidgets as widgets
from bcolors import bcolors
from pcp import PCP
from encoder_lu2pcpm import Encoder_LU_to_PCPM


class Exercicio_PCP:
  @staticmethod    
  def gerar_exemplo(pcp,input_solution=''):
    layout = widgets.Layout(width='300px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_solution,
        placeholder=f'Digite os indíces de uma solução para o PCP',
        description=f'',
        layout=layout
        )
    output = widgets.Output()
    #pcp = PCP(input_pcp)
    pcp.display()
    wInputBox= widgets.HBox([input,run])
    display(wInputBox,output)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        solution = [int(i) for i in input.value.strip().split(' ')]
        if (pcp.is_solution(solution)):
          print(f"\n{bcolors.OKBLUE}Parabéns, você encontrou uma solução!")
          pcp.display_solution(solution)
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a solução! Tente novamente!")
    run.on_click(on_button_run_clicked)

  @staticmethod    
  def converter_pcpm(pcpm, input_solution='', input_pcp=[], input_solution_pcp=''):
    layout = widgets.Layout(width='350px')
    run = widgets.Button(description="Verificar")
    input = widgets.Text(
        value=input_solution,
        placeholder=f'Digite os indíces de uma solução para o PCPM',
        description=f'',
        layout=layout
        )
    input_text_pcp = widgets.Text(
        value=input_solution_pcp,
        placeholder=f'Digite os indíces da solução para o PCP obtida do PCPM',
        description=f'',
        layout=layout
        )    
    k = pcpm.size()
    lI = [widgets.HTML('<center><b>Indices</b></center>')]+[widgets.HTML('<center>i'+str(i+1)+'</center>') for i in range(k+2)]

    if k+2==len(input_pcp):
      lA = [widgets.HTML('<center><b>Lista A</b></center>')]+[widgets.Text(value=input_pcp[i][0].strip(), placeholder=f'Digite w{i}') for i in range(k+2)]
      lB = [widgets.HTML('<center><b>Lista B</b></center>')]+[widgets.Text(value=input_pcp[i][1].strip(), placeholder=f'Digite x{i}') for i in range(k+2)]
    else:
      lA = [widgets.HTML('<center><b>Lista A</b></center>')]+[widgets.Text('', placeholder=f'Digite w{i}') for i in range(k+2)]
      lB = [widgets.HTML('<center><b>Lista B</b></center>')]+[widgets.Text('', placeholder=f'Digite x{i}') for i in range(k+2)]
    wColunas = widgets.HBox([widgets.VBox(lI), widgets.VBox(lA), widgets.VBox(lB)])
    wPCPM = widgets.Output(layout=layout)    
    with wPCPM:
      pcpm.display()
    wAllPCPM = widgets.VBox([widgets.HTML("<b>PCPM</b>"),wPCPM])
    wAllPCP = widgets.VBox([widgets.HTML("<b>PCP</b>"),wColunas])
    output = widgets.Output()
    wPCPM_PCP= widgets.VBox([widgets.HBox([wAllPCPM,wAllPCP]),
                                          widgets.HBox([widgets.HTML("<b>Solução PCPM:</b>",layout=layout), widgets.HTML("<b>Solução PCP:</b>",layout=layout)]), 
                                          widgets.HBox([input,input_text_pcp])])
    display(wPCPM_PCP, run, output)#, layout=layout)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        solution = [int(i) for i in input.value.strip().split(' ')] if input.value.strip()!= '' else []
        new_solution_pcp = [int(i) for i in input_text_pcp.value.strip().split(' ')] if input_text_pcp.value.strip()!= '' else []
        l_pcp = [(lA[i+1].value.strip(), lB[i+1].value.strip()) for i in range(k+2)] 
        new_pcp = PCP(l_pcp)
        if (set(l_pcp)==set(pcpm.to_PCP())):
          print(f"\n{bcolors.OKBLUE}Parabéns, você converteu corretamente a PCPM em uma PCP!")
          new_pcp.display()
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a conversão! Tente novamente!")
        if (pcpm.is_solution(solution) and len(solution)>0):
          print(f"\n{bcolors.OKBLUE}Parabéns, você encontrou uma solução para a PCPM!")
          pcpm.display_solution(solution)
          if (new_pcp.is_solution(new_solution_pcp) and len(new_solution_pcp)>0):
            print(f"\n{bcolors.OKBLUE}Parabéns, você encontrou uma solução para o PCP!")
            new_pcp.display_solution(new_solution_pcp)
          else:
            print(f"\n{bcolors.FAIL}Infelizmente, você errou a solução da PCP! Tente novamente!")
            new_pcp.display_solution(new_solution_pcp)
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você errou a solução da PCPM! Tente novamente!")
          pcpm.display_solution(solution)

    run.on_click(on_button_run_clicked)



  @staticmethod    
  def converter_MT(MT_pcpm, word, input_solution=''):
    layout = widgets.Layout(width='350px')
    run = widgets.Button(description="Verificar")
    input_solution = widgets.Text(
        value=input_solution,
        placeholder=f'Digite os indíces de uma solução para o PCPM',
        description=f'',
        layout=layout
        )
    wPCPM_MT = widgets.Output(layout=layout)    
    with wPCPM_MT:
      print("Seja a Máquina de Turing:")
      display(MT_pcpm.visualizar())
      encoded_pcpm = Encoder_LU_to_PCPM(MT_pcpm,word).encode()
      print(f"Seja o PCPM convertido a partir da MT acima e da palavra {word}")
      encoded_pcpm.display()

    output = widgets.Output()
    display(wPCPM_MT, input_solution, run, output)#, layout=layout)
    
    def on_button_run_clicked(_):
      output.clear_output()
      with output:
        solution = [int(i) for i in input_solution.value.strip().split(' ')]
        if (encoded_pcpm.is_solution(solution)):
          print(f"\n{bcolors.OKBLUE}Parabéns, você acertou uma solução que simula a palavra reconhecida pela Máquina de Turing")
        else:
          print(f"\n{bcolors.FAIL}Infelizmente, você ainda não conseguiu encontrar uma solução que simula a palavra reconhecida pela Máquina de Turing. Tente novamente!!")
        encoded_pcpm.display_solution(solution)
    run.on_click(on_button_run_clicked)


