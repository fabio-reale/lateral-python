
# %% [markdown]
# # Decorador Y - o Combinador Y em Python
#
# O objetivo desse texto é introduzir o conceito de decoradores em Python por meio de uma
# aplicação não trivial do conceito.
#
# O nome "decorador Y" faz referência ao "combinador Y".
# Não lidaremos com o que é esse combinador por algum tempo.
# Em princípio, tenha em mente que esse combinador é algo que pode ser usado para
# implementar recursões em contextos onde isso seria proibido, desde que seja permitido
# o uso de funções de primeira classe, ou seja, se funções podem ser passadas para
# outras funções como parâmetro.
# 
# Então, vamos impor limitações artificiais em Python para que estejamos nas 
# condições onde o combinador Y é a solução que precisamos.
# As restrições são:
#  - Não usar loops de nenhum tipo (for e while estão proibidos)
#  - Não usar recursão explicitamente (não usar o nome `func` em `def func():...`)
#
#
# Lembre-se que ainda podemos usar funções como parâmetros de outras funções e também
# funções que estejam no escopo global dentro de outras funções.
# Só estamos proibidos de utilizar a exata função que está sendo definida como se
# ela **já** estivesse no escopo global
# %% [markdown]
# Para esclarecer um pouco a restrição de recursão e termos um exemplo concreto com o
# qual trabalhar, suponhamos que queremos escrever uma função `t_menos(t)`.
# Essa função, dado um inteiro t, imprime a contagem regressiva de t até 1, seguido
# de alguma mensagem indicando que houve um lançamento

# %%
def t_menos_loop(t):

    for n in range(t, 0, -1):
        print(f'T menos {n}s para o lançamento')

    print('Temos uma decolagem!!\n...e veio do loop')

def t_menos_recursao(t):

    if t==0:
        print('Temos uma decolagem!! t_menos_recursao FTW!!')
    else:
        print(f'T menos {t}s para o lançamento')
        t_menos_recursao(t-1)

t_menos_loop(5)
print('\n------------------\n')
t_menos_recursao(5)

# %% [markdown]
# Ambas as funções estão proibidas. `t_menos_loop` é a versão considerada pythonica (pythonistas preferem loops a recursões) mas contém um loop `for`. Já a `t_menos_recursive` chama a si mesma na última linha. Note que não existe nenhum problema em chamar a função `print()`, essa faz parte do escopo global então é perfeitamente lícita!
# %% [markdown]
# Com as nossas restrições, a `t_menos_loop` não tem a menor chance. Mas a `t_menos_recursao` só precisa resolver a última linha. Como poderíamos resolver isso?
#
# Bom, note que as restrições que nos colocamos impedem que a função chamada na última linha seja a própria `t_menos_recursao`. Como é permitido chamar funções do escopo global, se tivéssemos uma `t_menos_func` funcionando no escopo global, poderíamos simplesmente chamá-la:

# %%
def t_menos_recursao_hack(t):

    if t==0:
        print('Temos uma decolagem hackeada!! Hacks invisíveis são os melhores!')
    else:
        print(f'T menos {t}s para o lançamento')
        t_menos_recursao(t-1)

t_menos_recursao_hack(5)

# %% [markdown]
# Isso funciona mas requer que já tenhamos uma função `t_menos` definida e funcionando.
# Como isso já é exatamente o que pretendemos, isso não parece muito viável.
#
# Então, vamos supor que a função que estamos definindo irá funcionar de forma que poderemos chamá-la de lá de dentro.
# Porém, por conta da nossa restrição, não podemos chamá-la pelo nome.
# Uma solução pra esse problema é acrescentar uma função como parâmetro de entrada, chamar essa função passada como parâmetro no lugar da chamada recursiva.
# Dessa forma, uma vez definida a função, ela pode receber a si mesma como parâmetro e aí poderá se "*enchergar*" no próprio escopo

# %%
def t_menos_1a_classe(t_menos_func, t):

    if t==0:
        print('Temos decolagem de primeira classe!!')
    else:
        print(f'T menos {t}s para o lançamento')
        t_menos_func(t-1)

t_menos_1a_classe(t_menos_recursao, 3)

print('\n----------------------\n')

try:
    t_menos_1a_classe(t_menos_1a_classe, 3)
except Exception as e:
    print('.\n.\nHouve uma Exception:')
    print(e)

# %% [markdown]
# Essa função é ótima! Não quebra nenhuma de nossas regras!!
#
# Pena que essa também precisa de uma `t_menos_func` funcionando pra poder funcionar.
# E, mais uma vez, é justamente esse o problema que queremos resolver!! E agora?
#
# Uma maneira de entender o que deu errado com a `t_menos_1a_classe` é que mudamos a assinatura de argumentos dela.
# Transformamos ela numa função cujo 1º argumento esperado é outra função.
# Então a função que ela recebe como parâmetro não pode mais ser ela mesma.
#
# De cara podemos pensar em 2 maneiras de resolver esse problema. Vamos com uma de cada vez. A primeira ideia é considerar que a função parâmetro tem a mesma assinatura que `t_menos_1a_classe` e mudar a chamada da função da última linha

# %%
def t_menos_1a_classe_recebendo_1a_classe(t_menos_1a_classe_func, t):

    if t==0:
        print('Temos decolagem de primeira classe no estilo Inception!! ')
    else:
        print(f'T menos {t}s para o lançamento')
        t_menos_1a_classe_func(t_menos_1a_classe_func, t-1)

t_menos_1a_classe_recebendo_1a_classe(t_menos_1a_classe_recebendo_1a_classe, 3)

# %% [markdown]
# Essa de fato funciona, mas precisamos chamá-la passando ela mesma como parâmetro! Idealmente a função teria apenas o parâmetro `t`.
# Tem mais de um motivo pra querermos isso.
# 
# Mas principalmente, porque poderiam chamar a função com outra função como parâmetro e algo horrível pode acontecer nesse caso

# %%
def t_menos_trololo(func_ignorado, param_ingnorado):
    print("Sequência Fracassada! Astronautas morreram e a culpa é toda sua!!")

t_menos_1a_classe_recebendo_1a_classe(t_menos_trololo, 3)

# %% [markdown]
# Ó! Temos que salvar os astronautas desse destino horrível!!
# 
# Precisamos fazer com que nossa função **tenha** que receber a si própria. Faremos isso através de uma aplicação parcial da `t_menos_1a_classe_recebendo_1a_classe`
# 
# Em algumas linguagens, como Haskell, esse tipo de aplicação é o comportamento padrão de funções.
# Em Python existem bibliotecas que realizam esse serviço, mas podemos fazer nós mesmos através de um fechamento (closure).
# Fechamentos consistem em definir uma função dentro de outra função e retorná-la.

# %%
def auto_aplicador(func):

    def func_auto_aplicada(param):
        return func(func, param)

    return func_auto_aplicada

t_menos_auto_aplicada = auto_aplicador(t_menos_1a_classe_recebendo_1a_classe)

t_menos_auto_aplicada(5)

# %% [markdown]
# Ufa! Salvamos os astronautas!!
#
# E, no processo descobrimos quais os contratempos que precisam ser vencidos para implementar recursões sem loops e sem auto-referência.
#
# Agora, já que já chegamos nesse ponto, por quê não ir além e generalizar a solução?
# Vamos criar algo que possa fazer essas mesmas transformações passo a passo e automatizar o processo!! \o/
# %% [markdown]
# Mas antes, um pequeno passeio pelo açúcar sintático dos decoradores em Python.
#
# Decoradores nada mais são que uma maneira de escrever exatamente o que acabamos
# de fazer, se tivéssemos sobrescrito a função `t_menos_1a_classe_recebendo_1a_classe` chamando
# `t_menos_1a_classe_recebendo_1a_classe = auto_aplicador(t_menos_1a_classe_recebendo_1a_classe)`
#
# Vamos rescrever essa função usando a sintaxe de decorador para esclarecer:

# %%
def t_menos_auto_aplicada_sem_decorator(f, t):

    if t==0:
        print('Temos uma decolagem!! Sem decoração :-(')
    else:
        print(f'T menos {t}s para o lançamento')
        f(f, t-1)

t_menos_auto_aplicada_sem_decorator = auto_aplicador(t_menos_auto_aplicada_sem_decorator)

@auto_aplicador
def t_menos_auto_aplicada_com_decorator(f, t):

    if t==0:
        print("Temos uma decolagem!! Com decorated :-)")
    else:
        print(f'T menos {t}s para o lançamento')
        f(f, t-1)

t_menos_auto_aplicada_sem_decorator(3)
print()

t_menos_auto_aplicada_com_decorator(3)
print()

# %% [markdown]
# O decorador muda a função logo após sua definição e re-atribui àquele nome, alterando o comportamento da função sem precisar mudar seu nome.
#
# Bom, já vimos como resolver o problema da `t_menos_1a_classe_recebendo_1a_classe`, que é a função que recebe uma função com a mesma assinatura que ela e aplica passando a si mesma como parâmetro.
#
# Vamos agora tentar resolver o problema da `t_menos_1a_classe`.
# Uma ideia é tentar fazer com que a `t_menos_1a_classe` se comporte como a `t_menos_1a_classe_recebendo_1a_classe`.
# Como já conseguimos resolver essa outra fazendo uma aplicação dela nela mesma, parece um bom caminho.
#
# Porém, já vimos o que ocorre quando aplicamos `t_menos_1a_classe` em si mesma.
# Acontece uma `Exception` que nos avisa que não passamos um parâmetro obrigatório.
# Isso ocorre pois a função que estamos passando (a própria `t_menos_1a_classe`) recebe 2 parâmetros, enquanto a função parâmetro (`t_menos_func`) é aplicada em apenas 1.
#
# Recordando a definição da função:
# ```python
# def t_menos_1a_classe(t_menos_func, t):
#
#     if t==0:
#         print('Temos uma decolagem!!')
#     else:
#         print(f'T menos {t}s para o lançamento')
#         t_menos_func(t-1)
# ```
# %% [markdown]
# Aqui vemos que precisamos fazer algo mais complicado.
# Precisamos mudar a assinatura da `t_menos_func` que chega como parâmetro!
#
# Como pretendemos aplicar a função nela mesma, percebemos que o que precisamos fazer é, precisamente, passar um segundo parâmetro.
# E o destino horrível dos astronautas já nos ensinou que precisamos garantir que seja a própria função que seja passada.
#
# Mas para não complicar demais, vamos um passo por vez.
#
# O primeiro passo é alterar o comportamento da `t_menos_func` (a função parâmetro).
#
# Porém, para que possamos fazer qualquer alteração no parâmetro da função, precisaremos de um fechamento.
# Chamemos isso de o zerésimo passo.
# E comecemos alterando o parâmetro inteiro t.
# Vai ser mais didático dessa forma!

# %%
def altera_param_de_func(func):

    def nova_func(t):
        novo_t = t+1
        return func(novo_t)

    return nova_func

mais_longa_t_menos = altera_param_de_func(t_menos_auto_aplicada_com_decorator)

mais_longa_t_menos(3)

# %% [markdown]
# Então vemos que, com um fechamento, conseguimos alterar os parâmetros antes da nossa função base encontrá-los.
#
# Agora estamos prontos para consertar a nossa `t_menos_1a_classe`.
# Precisamos fazer um fechamento como esse.
#
# Porém, a alteração de comportamento que precisamos executar já foi implementada: `auto_aplicador`.
# Essa função recebe uma função de 2 parâmetros e a transforma numa função que recebe um parâmetro tendo fixado ela própria como parâmetro.
#
# Observe que tinha que ser a própria `auto_aplicador` pois estamos resolvendo exatamente o mesmo problema que estávamos resolvendo na ocasião.
# A única diferença é que dessa vez estamos resolvendo o problema da função que é passada como parâmetro para a outra função.
# E por conta dessa diferença é que teremos de fazer o fechamento.
# Para acessar a função parâmetro (`t_menos_func`).

# %%
def auto_aplica_func_interna(func):

    def nova_func(func_param, t):

        func_param = auto_aplicador(func_param)

        return func(func_param, t)

    return nova_func

@auto_aplica_func_interna
def t_menos_1a_classe_corrigida(t_menos_func, t):

    if t==0:
        print('\nProblemas foram resolvidos!\nTemos uma decolagem!!\n')
    else:
        print(f'T menos {t}s para o lançamento')
        t_menos_func(t-1)

t_menos_1a_classe_corrigida(t_menos_1a_classe_corrigida, 3)

# %% [markdown]
# Como último passo, observe que caímos mais uma vez no problema de segurança dos astronautas.
# Não haverá criatividade nesse momento, aplicaremos a mesma solução.
#
# Mas, vamos aproveitar a oportunidade para ver como decoradores encadeados funcionam.
#
# Primeiro queremos realizar o passo que acabamos de realizar e apenas depois queremos fazer a auto aplicação da função final.
# Nesses casos o primeiro decorador colocado deve ser o último da cadeia

# %%
@auto_aplicador
@auto_aplica_func_interna
def t_menos(rec, t):

    if t==0:
        print('\nTemos uma decolagem!!\nE nenhuma recursão ocorreu explicitamente!\n')
    else:
        print(f'T menos {t}s para o lançamento')
        rec(t-1)

t_menos(5)

# %% [markdown]
# Nesse momento você pode estar se perguntando: "e onde está o combinador Y?"
#
# Muito justa a pergunta. O combinador Y é exatamente o que acabamos de deduzir aqui nesse processo.
# Em Python, o vocabulário de decoradores para descrever funções que alteram o comportamento de outras funções ajuda na compreensão:
#
# O combinador Y é um decorador!
# Y espera receber uma função que tem por parâmetro alguma função.
# Além disso, é importante que essa função seja aplicada e que tenha um parâmetro a menos (o de outra função)
# A alteração de comportamento causada pelo decorador é realizar a autoaplicação tanto da própria função quanto da função passada como parâmetro.
# %% [markdown]
# Para fechar, vamos definir a Y (mantendo a convenção de case do python) e aplicá-la para fazer uma definição não recursiva e sem loops da função fatorial:

# %%
def decorador_y(func):
    return auto_aplicador( auto_aplica_func_interna(func) )

@decorador_y
def fact(rec, n):

    if n==0:
        return 1
    else:
        return n*rec(n-1)

assert fact(5) == 5*4*3*2*1
