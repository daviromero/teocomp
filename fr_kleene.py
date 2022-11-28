# Implementação em Python das Funções Recursivas de Kleene (*beta*)

# Funções Básicas:

# Natural Zero
def z(x):
  return 0
# Função Sucessor
def s(x):
  return x+1

# Função Projeção 1
def u_1(i,x):
  return x if i==1 else -1
# Função Projeção 2
def u_2(i,x,y):
  return x if i==1 else y if i==2 else -1
# Função Projeção 3
def u_3(i,x,y,z):
  return x if i==1 else y if i==2 else z if i==3 else -1
# Função Projeção 4 ...

# Em Python, podemos ter uma função Projeção para múltiplos argumentos
def u(i,*args):
  return args[i-1]

# Definição de Composição de Função
def composicao(*args):
  return lambda f, g: f(g(args))

def composicao_2(*args):
  return lambda f, g1,g2: f(g1(args),g2(args))

def composicao_3(*args):
  return lambda f, g1,g2,g3: f(g1(args),g2(args),g3(args))


# Definição Recursiva sem argumentos, só a recursividade
def rec_0(y):
  return lambda f,g: f if y==0 else g(y-1,rec_0(y-1)(f,g))

# Definição Recursiva com 1 argumento x
def rec_1(x,y):
  return lambda f,g: f(x) if y==0 else g(x,y-1,rec_1(x,y-1)(f,g))

# Definição Recursiva com 2 argumentos x1,x2
def rec_2(x1,x2,y):
  return lambda f,g: f(x1,x2) if y==0 else g(x1,x2,y-1,rec_2(x1,x2,y-1)(f,g))

# Definição Recursiva com 3 argumentos x1,x2,x3
def rec_3(x1,x2,x3,y):
  return lambda f,g: f(x1,x2,x3) if y==0 else g(x1,x2,x3,y-1,rec_3(x1,x2,x3,y-1)(f,g))

# Um definição geral de função recursiva, apenas inverte os argumentos pq em Python é necessário *args ser o último elemento.
def rec(*args):
  if len(args)>1:
    return rec_aux(args[-1],*tuple(args[:-1]))
  elif len(args)==1:
    return rec_0(args[-1])

# Um definição geral de função recursiva
def rec_aux(y,*xs):
#  print("rec_aux(y,*xs)",y,*xs)
  return lambda f,g: f(*tuple(xs)) if y==0 else g(*tuple(xs),y-1,(rec_aux(y-1,*tuple(xs))(f,g)))

## Definições de funções que serão utilizadas na minimização limitada
soma_aux = lambda x,y: rec(x,y)(lambda x: u(1,x), lambda x,y,z: s(u(3,x,y,z)))
mult_aux = lambda x,y: rec(x,y)(lambda x:z(x), lambda x,y,z: soma_aux(u(3,x,y,z),u(1,x,y,z)))
a_aux = lambda y: rec(y)(z(_), lambda y,z: u(1,y,z))
sub_aux = lambda x,y : rec(x,y)(lambda x:u(1,x),lambda x,y,z:a_aux(u(3,x,y,z)))
sub_abs_aux = lambda x,y: soma_aux(sub_aux(x,y),sub_aux(y,x))
isZero_aux = lambda x: sub_aux(s(z(_)),x)
d_aux = lambda x,y: isZero_aux(sub_abs_aux(x,y))
lnot_aux = lambda x: isZero_aux(x)

# Definição por casos (If-then-else)
def if_then_else(*xs):
  return lambda p,g,h: soma_aux(mult_aux(g(*(tuple(xs))),p(*(tuple(xs)))), mult_aux(h(*(tuple(xs))),isZero_aux(p(*(tuple(xs))))))

# Um definição geral de função recursiva, apenas inverte os argumentos pq em Python é necessário *args ser o último elemento.
def rec_f_y(*args):
  if len(args)>1:
    return rec_f_y_aux(args[-1],*tuple(args[:-1]))
  elif len(args)==1:
    return lambda f,g:rec_f_y_aux_0(*args[-1])(f,g)

# Um definição geral de função recursiva
def rec_f_y_aux(y,*xs):
#  print(y,*xs)
  return lambda f,g: f(*(tuple(xs)+tuple([y]))) if y==0 else g(*tuple(xs),y-1,(rec_f_y_aux(y-1,*tuple(xs))(f,g)))

def rec_f_y_aux_0(y):
  return lambda f,g: f(y) if y==0 else g(y-1,(rec_f_y_aux_0(y-1)(f,g)))

def somatorio(*args):
  if len(args)==1:
    return lambda f: somatorio_0(args,f)
  elif len(args)==2:
    return lambda f: somatorio_1(args[-2],args[-1],f)
  elif len(args)==3:
    return lambda f: somatorio_2(args[-3],args[-2],args[-1],f)
  elif len(args)==4:
    return lambda f: somatorio_3(args[-4],args[-3],args[-2],args[-1],f)

# Definição Recursiva sem argumentos, só a recursividade
somatorio_0 = lambda y,f: rec_f_y(y)(f,(lambda y,z: soma_aux(u(2,y,z),f(y+1))))
somatorio_1 = lambda x1,y,f: rec_f_y(x1,y)(f,(lambda x1,y,z: soma_aux(u(3,x1,y,z),f(x1,y+1))))
somatorio_2 = lambda x1,x2,y,f: rec_f_y(x1,x2,y)(f,(lambda x1,x2,y,z: soma_aux(u(4,x1,x2,y,z),f(x1,x2,y+1))))
somatorio_3 = lambda x1,x2,x3,y,f: rec_f_y(x1,x2,x3,y)(f,(lambda x1,x2,x3,y,z: soma_aux(u(5,x1,x2,x3,y,z),f(x1,x2,x3,y+1))))
#def somatorio_0(y):
#  return lambda f: rec_f_y(y)(f,(lambda y,z: soma_aux(u(2,y,z),f(y+1))))
#def somatorio_1(x1,y):
#  return lambda f: rec_f_y(x1,y)(f,(lambda x1,y,z: soma_aux(u(3,x1,y,z),f(x1,y+1))))
#def somatorio_2(x1,x2,y):
#  return lambda f: rec_f_y(x1,x2,y)(f,(lambda x1,x2,y,z: soma_aux(u(4,x1,x2,y,z),f(x1,x2,y+1))))


def produtorio(*args):
  if len(args)==1:
    return lambda f: produtorio_0(args,f)
  elif len(args)==2:
    return lambda f: produtorio_1(args[-2],args[-1],f)
  elif len(args)==3:
    return lambda f: produtorio_2(args[-3],args[-2],args[-1],f)
  elif len(args)==4:
    return lambda f: produtorio_3(args[-4],args[-3],args[-2],args[-1],f)

# Definição Recursiva sem argumentos, só a recursividade
#def produtorio_0(y):
#  return lambda f: rec_f_y(y)(f,(lambda y,z: mult_aux(u(2,y,z),f(y+1))))
#def produtorio_1(x1,y):
#  return lambda f: rec_f_y(x1,y)(f,(lambda x1,y,z: mult_aux(u(3,x1,y,z),f(x1,y+1))))
#def produtorio_2(x1,x2,y):
#  return lambda f: rec_f_y(x1,x2,y)(f,(lambda x1,x2,y,z: mult_aux(u(4,x1,x2,y,z),f(x1,x2,y+1))))


produtorio_0 = lambda y,f: rec_f_y(y)(f,(lambda y,z: mult_aux(u(2,y,z),f(y+1))))
produtorio_1 = lambda x1,y,f: rec_f_y(x1,y)(f,(lambda x1,y,z: mult_aux(u(3,x1,y,z),f(x1,y+1))))
produtorio_2 = lambda x1,x2,y,f: rec_f_y(x1,x2,y)(f,(lambda x1,x2,y,z: mult_aux(u(4,x1,x2,y,z),f(x1,x2,y+1))))
produtorio_3 = lambda x1,x2,x3,y,f: rec_f_y(x1,x2,x3,y)(f,(lambda x1,x2,x3,y,z: mult_aux(u(5,x1,x2,x3,y,z),f(x1,x2,x3,y+1))))


#def exists_leq(x,y):
#  return lambda f: isZero_aux(isZero_aux(somatorio(x,y,y)(f)))
#def forall_leq(x):
#  return lambda f: d_aux(produtorio(x,x)(f),s(z(_)))

def exists_leq(*args):
  return lambda f: isZero_aux(isZero_aux(somatorio(*(tuple(args)+tuple([args[-1]])))(f)))

def forall_leq(*args):
  return lambda f: d_aux(produtorio(*(tuple(args)+tuple([args[-1]])))(f),s(z(_)))

# Define a minimização limitada
def Min(*args):
  if len(args)==1:
    return lambda f: Min_0(args)(f)
  elif len(args)==2:
    return lambda f: Min_1(args[0],args[1])(f)
  elif len(args)==3:
    return lambda f: Min_2(args[0],args[1],args[2])(f)

prod_aux_1 = lambda f: (lambda y,t: produtorio_1(y,t,lambda y,t: lnot_aux(f(y,t))))
def Min_0(y):
  return lambda f: somatorio_1(y,y, prod_aux_1(f))  if exists_leq(y)(f) else z(_)

prod_aux_2 = lambda f: (lambda x,y,t: produtorio_2(x,y,t,lambda x,y,t: lnot_aux(f(x,y,t))))
def Min_1(x,y):
  return lambda f: somatorio_2(x,y,y, prod_aux_2(f))  if exists_leq(x,y)(f) else z(_)

prod_aux_3 = lambda f: (lambda x1,x2,y,t: produtorio_3(x1,x2,y,t,lambda x1,x2,y,t: lnot_aux(f(x1,x2,y,t))))
def Min_2(x1,x2,y):
  return lambda f: somatorio_3(x1,x2,y,y, prod_aux_3(f)) if exists_leq(x1,x2,y)(f) else z(_)
