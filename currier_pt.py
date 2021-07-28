# %% [markdown]
# # Decorador para Currying em Python
#
# Neste texto vamos pensar em como podemos construir um decorador que transforme
# funções usuais em funções curried.
#
# Currying é o processo de converter funções de múltiplos parâmetros em
# múltiplas funções de um único parâmetro.
# Suponha que temos uma função `f` que recebe 3 parâmetros.
# Como toda função em Python, aplicações dessa função são da forma `f(x, y, z)`,
# ou seja, requerem que 3 argumentos devam ser passados de uma vez só, através 
# de uma tupla que então retorna um único valor (eventualmente `None`,
# eventualmente uma tupla de valores).
# Uma versão curried da `f` permitirá que esses parâmetros sejam passados separadamente.
# Algo como `f(x)(y)(z)`.
# Funções podem ser chamadas dessa forma em Python, como veremos adiante.
# Mas existem condições que precisam ser estabelecidas para que funções
# funcionem dessa forma.
# Fica mais fácil de visualizar o que acontece se atribuirmos nomes aos passos
# intermediários.
# ```python
# f_x = f(x)
# f_x_y = f_x(y)
# 
# assert f(x)(y)(z) == f_x_y(z)
# ```
# A função `f` não foi definida no exemplo acima.
# Portanto, o "código" não pode ser rodado da forma que está.
# Então a questão a resolver aqui será: como definir uma tal `f`?
#
# Para facilitar o raciocínio, vamos usar uma função `f` bem simples e tomá-la
# como uma função que recebe 2 argumentos numéricos e retorna a soma deles.

# %%
def adicao_classica(x, y):
    return x + y

assert adicao_classica(3, 5) == 3 + 5

# %% [markdown]
# Agora queremos passar os argumentos `3` e  `5` um de cada vez.
# Nós poderíamos simplesmente definir uma função `soma_3` como 
#```python
# def soma_3(y):
#     return 3 + y
#```
# Mas não queremos apenas ser capazes de somar 3.
# Queremos ser capazes de passar qualquer valor a ser somado.
# Ou seja, queremos fazer uma função `soma_x`.
# Além disso, já temos uma função que faz a soma.
# Queremos apenas adicionar a funcionalidade de passar um argumento por vez para
# nossa função.
# Então vamos seguir o princípio de não nos repetirmos (DRY) e aproveitarmos a
# função existente.
#
# Bom, já entendemos que `soma_x` deve ser uma função.
# Além disso, vemos que `soma_x` deve ser parametrizável, ou seja, precisamos
# de uma função que receba a primeira parcela da soma (que estamos chamando de `x`)
# e retorne a função `soma_x`.
# Esse padrão tem o nome de fechamento (em inglês o termo é closure).
#
# Python nos permite definir funções dentro de outras funções.
# Também nos permite retornar essas funções.
# Dessa forma, podemos produzir nosso somador curried da seguinte forma:
# %%
def construtor_de_adicao(x):

    def somador_parcial(y):           # soma_x sendo definido internamente
        return adicao_classica(x, y)  # observe que somador_parcial "lembra" o valor
                                      # de x mesmo x não sendo parâmetro de somador_parcial

    return somador_parcial            # valor de retorno de construtor_de_adicao é uma função

soma_3 = construtor_de_adicao(3)      # Invocamos construtor_de_adicao com valor 3 para que
                                      # somador_parcial passe esse 3 adiante quando invocar
                                      # adicao_classica

assert soma_3(5) == 3 + 5

# %% [markdown]
# Funciona!
#
# Mas ainda não estamos fazendo exatamente o que nos propusemos a fazer.
# No código acima produzimos uma função intermediária que fixa o valor da 1ª parcela.
# Queremos conseguir pular esse passo intermediário se desejarmos.
#
# Ao observar com cuidado o que acabamos de fazer, podemos ver que já temos o
# que precisamos para termos o comportamento desejado.
# Pois `soma_3 == construtor_de_adicao(3)` e `soma_3(5) == 8`
# Portanto, `construtor_de_adicao(3)(5)` deve resultar em `8`.

# %%
soma_curried = construtor_de_adicao

assert soma_curried(3)(5) == 3 + 5

# %% [markdown]
# Legal! Vamos tentar abstrair o padrão e generalizar a solução em um decorador.
#
# Então vamos antes dar uma olhadinha em decoradores.
#
# ## Decoradores
#
# Em Python, decorador é um açúcar sintático para um padrão específico de fechamento.
# O seguinte padrão:
#
# ```python
# def decorador(funcao_a_decorar):
#
#   def nova_funcao_decorada(*args):
#       ... # funcao_a_decorar é aplicada aqui dentro
#
#   return nova_funcao_decorada
#
# funcao_a_decorar = decorador(funcao_a_decorar)
# ```
# Decoradores são fechamentos para funções.
# Em particular, são fechamentos que recebem uma função como entrada e retornam
# uma outra função como saída.
# Além disso, o decorador realiza a substituição da função original pela função
# decorada no namespace.
# Com o açúcar sintático já na definição da `funcao_a_decorar` fica da seguinte forma:
# ```python
# @decorador
# def funcao_a_decorar(*args):
#   ...
# ```
#
# O importante de observar aqui é que nosso `soma_curried` é definido a partir de
# `construtor_de_adicao` que espera receber um parâmetro numérico e não uma função.
# Portanto não podemos utilizá-la como decorador da maneira como foi definida.
#
# Então, voltando ao nosso exemplo com `adicao_classica`, buscamos uma
# maneira de tornar a própria função `adicao_classica` como parâmetro.
#
# Pensando bem, utilizamos `adicao_classica` dentro do fechamento.
# Faz até mais sentido passar a função como parâmetro, pois aí podemos generalizar
# o processo e passar outras funções para nosso pretenso decorador.
# Seguindo o padrão dos decoradores, faz sentido, então, colocar todo aquele
# código do `construtor_de_adicao` dentro de uma nova função que recebe a função
# a ser invocada lá no final do processo.

#%%
def curry_em_2_passos(funcao_sem_curry):

    def recebe_primeiro_parametro(x):

        def recebe_segundo_parametro(y):
            # Tendo ambos os parâmetros, aplica a função original e retorna
            return funcao_sem_curry(x, y)

        return recebe_segundo_parametro

    return recebe_primeiro_parametro

@curry_em_2_passos
def soma_2_parcelas(x, y):
    return x + y

assert soma_2_parcelas(3)(5) == 3 + 5


#%% [markdown]
#
# Pelos nomes utilizados, pode ter ficado claro que temos limitações na solução
# apresentada acima.
#
# Vamos lidar com a mais simples primeiro...
#
# Observe que foi definida uma função para receber cada parâmetro, o que faz
# muito sentido já que era o comportamento pretendido.
# Porém, isso limita a implementação para realizar currying apenas de funções
# com exatamente 2 parâmetros.
# Podemos mudar um pouco nossa implementação e fazer um decorador que realiza o
# currying somente do primeiro parâmetro, independentemente de quantos outros
# parâmetros a função original tenha.
# Para isso precisaremos utilizar o padrão `*args`.
#
# Já utilizamos `*args` no exemplo de decorador, mas sem dar maiores explicações.
# O operador `*` desempacota intancias de objetos que listam valores.
# Normalmente isso implica que tratamos de listas ou tuplas.
# E no caso da utilização em definições de funções, serão sempre tuplas.
# Como curiosidade, também existe o operador `**`, que lida com objetos como dicionários.
# `**kwargs` é bastante usado para os casos em que funções possuem argumentos nomeados
# (keyword arguments), mas ignoraremos ele aqui para facilitar a leitura dos códigos.
#
# Voltando ao currying...
# Ao adicionarmos `*args` à definição de nossa função mais interna, poderemos
# fazer o currying de funções com mais parâmetros do que apenas 2, uma vez que
# o `*args` desempacotará todos os argumentos remanescentes, independente de
# quantos sejam.

#%%
def currying_do_1o_arg(funcao_sem_curry):

    def recebe_primeiro_parametro(x):

        def recebe_todos_outros_parametros(*args):
            # Aplica função original e retorna
            return funcao_sem_curry(x, *args)

        return recebe_todos_outros_parametros

    return recebe_primeiro_parametro

@currying_do_1o_arg
def soma_3_parcelas(x, y, z):
    return x + y + z

assert soma_3_parcelas(3)(5, 7) == 3 + 5 + 7

#%% [markdown]
#
# Não foi por acidente que passamos os últimos 2 argumentos de uma única vez.
# Vamos ver o que acontece se tentarmos chamar `soma_3_parcelas` como se ela
# tivesse sido curried até o fim.

#%%
try:
    soma_3_parcelas(3)(5)(7)
except TypeError as t:
    assert str(t) == "soma_3_parcelas() missing 1 required positional argument: 'z'"

#%% [markdown]
# Como podemos observar, nesse caso temos um `TypeError` que nos informa termos
# deixado de passar 1 argumento posicional obrigatório para a função
# `soma_3_parcelas()`.
# Em particular, deixamos de passar o último, que chamamos de 'z'.
#
# Isso significa que `currying_do_1o_arg` faz juz ao próprio nome é só realiza
# o processo de currying até o primeiro argumento.
# Pra explicitar o ocorrido, `soma_3_parcelas` é uma função que recebe um único
# argumento e retorna uma função que recebe 2 argumentos.
# Dessa forma, quando tentamos invocar essa segunda função apenas com o argumento
# `5` para o parâmetro `y`, temos que o parâmetro `z` fica sem argumento.
#
# Essa também é a razão para não ser possível reaplicarmos o decorador repetidas
# vezes para obter o currying completo.

#%%
@currying_do_1o_arg
@currying_do_1o_arg
def soma_3_parcelas_nova_tantativa(x, y, z):
    return x + y + z

try:
    soma_3_parcelas_nova_tantativa(3)(5)(7)
except TypeError as t:
    assert str(t) == "recebe_primeiro_parametro() takes 1 positional argument but 2 were given"

#%% [markdown]
#
# Porém, conseguimos continuar reaplicando o decorador se formos realizando as
# aplicações parciais dos parâmetros que já foram curried.

#%%
@currying_do_1o_arg
def soma_3_parcelas_versao_estranha(x, y, z):
    return x + y + z

inclui_3_na_soma = soma_3_parcelas_versao_estranha(3)
inclui_3_na_soma = currying_do_1o_arg(inclui_3_na_soma)

assert inclui_3_na_soma(5)(7) == 3 + 5 + 7

#%% [markdown]
#
# O código acima é confuso.
# Tome um tempo para apreciá-lo com calma.
# Talvez suba um console Python e cutuque um pouco a função
# `soma_3_parcelas_versao_estranha`.
# Talvez até mesmo aproveite pra fazer um café ou um chá.
#
# Ok. Vamos lembrar o que o `@currying_do_1o_arg` faz.
# Para facilitar um pouco, vamos remover as funções mais internas que, nesse
# momento, são apenas ruído.
#
# ```python
# def currying_do_1o_arg(funcao_sem_curry):
# 
#   def recebe_primeiro_parametro(x):
#     ...
#   
#   return recebe_primeiro_parametro
# ```
#
# Observe que, depois de aplicar o decorador em qualquer função ela se torna uma
# função de um parâmetro só.
# Não faz nenhum faz sentido fazer currying de uma função que já é de parâmetro
# único.
#
# Ok, ok. E o que é que podemos aprender com esse fracasso em particular?
# Bom, uma maneira de ler a situação é que, ao alterar fundamentalmente a assinatura
# de parâmetros da função, nos impedimos de recair num caso em que o decorador
# de currying que fizemos pudesse ser reaplicado.
#
# Então vamos tentar pensar em uma solução que preserve a assinatura da função
# mesmo depois de aplicar o decorador.
#
# Quando aplicamos o decorador uma vez, chegamos num ponto em que a função
# pode ser chamada como `soma(x)(y, z)` mas aí o problema é que `soma` recebe
# parâmetro único, então não dá pra reaplicar a solução.
# Então, talvez seja interessante tentar produzir um decorador que, ao ser
# aplicado uma vez retorne uma função que possa ser chamada por `soma(x, y)(z)`.
# Sendo possível fazer o currying do último parâmetro, produziríamos uma função
# com ainda múltiplos parâmetros a serem curried, de forma que poderíamos
# reaplicar a solução até sobrar apenas 1 parâmetro.
#
# Sem começarmos do caso geral, vamos ver se conseguimos fazer isso diretamente
# com a função soma.

#%%
def soma_3_parcelas_com_z_curried(x, y):

    def recebe_z_e_soma(z):
        return x + y + z

    return recebe_z_e_soma

assert soma_3_parcelas_com_z_curried(3, 5)(7) == 3 + 5 + 7

#%% [markdown]
#
# Parece promissor
# `soma_3_parcelas_com_z_curried` é uma função de 2 parâmetros, então deve ser
# possível fazer currying com ela.
#
# Vamos testar.

#%%
soma_3_curried = currying_do_1o_arg(soma_3_parcelas_com_z_curried)

assert soma_3_curried(3)(5)(7) == 3 + 5 + 7

#%% [markdown]
#
# Aí sim! Vamos ver se conseguimos generalizar isso em um decorador.

#%%
def curry_ultimo(func):

    def func_sem_ultimo(*args):

        def recebe_ultimo(arg):
            return func(*args, arg)

        return recebe_ultimo

    return func_sem_ultimo

@curry_ultimo
def soma_2_parcelas_com_3a(x, y, z):
    return x + y + z

assert soma_2_parcelas_com_3a(3, 5)(7) == 3 + 5 + 7

#%% [markdown]
#
# Agora temos uma função parcialmente curried, mas que ainda pode ser curried
# nos argumentos que faltam.
#
# Nós poderíamos agora aplicar o decorador `currying_do_1o_arg` pra terminar o
# currying da função.
# Se bem que, nesse caso em que temos apenas 2 parâmetros, que diferença faz
# fazer currying do 1º ou do 2º parâmetro?
# A solução nova pareceu funcionar bem, por quê não aplicá-la novamente?

#%%
@curry_ultimo
@curry_ultimo
def soma_3_curried_nova(x, y, z):
    return x + y + z

assert soma_3_curried_nova(3)(5)(7) == 3 + 5 + 7

#%% [markdown]
#
# Temos um pouquinho mais de generalização a fazer.
# Do jeito que está, precisamos aplicar o decorador `curry_ultimo` tantas vezes
# quantos parâmetros tenhamos na função, além de 1.
#
# Precisamos de uma maneira de fazer tantas reaplicações quanto necessárias.
# Depois de tudo que já fizemos, esse passo não é tão complicado.

#%%
def curry_n_args(n, func):

    for _ in range(n-1):
        func = curry_ultimo(func)

    return func

def soma_3_parcelas_n_args(x, y, z):
    return x + y + z

soma_3_parcelas_n_args = curry_n_args(3, soma_3_parcelas_n_args)

assert soma_3_parcelas_n_args(3)(5)(7) == 3 + 5 + 7

#%% [markdown]
#
# Ok, funciona, mas estragamos o decorador.
# Parece que precisamos de um decorador para o qual possamos passar parâmetros.
# Como isso pode ser possível se os decoradores são feitos para receber
# unicamente uma função?
#
# Bem, caro leitor, é agora que a coisa fica interessante.
# Queremos definir uma função de 2 parâmetros que tem um inteiro como primeiro
# parâmetro e uma função como segundo.
# E com isso queremos criar uma função que se lembre do parâmetro inteiro mas
# que possui apenas um parâmetro, que no caso é uma função.
# Então, o que precisamos é precisamente fazer uma versão **curried** de nosso
# "decorador" `curry_n_args`!


#%%
curry = curry_ultimo(curry_n_args)

@curry(4)
def soma_4_curried(x, y, z, w):
    return x + y + z + w

assert soma_4_curried(1)(2)(3)(4) == 1 + 2 + 3 + 4

#%% [markdown]
#
# Já tá bom o suficiente pra mim.
# No entanto, tem mais uma alteração interessante que pode ser feita aqui.
# Podemos fazer um decorador que nem necessite receber o argumento para quantos
# parâmetros aplicar o currying.
# Com a implementação apresentada até agora, nós poderíamos cair na situação de
# receber um `TypeError` se modificarmos um programa de maneira a remover um
# parâmetro de uma função mas nos esqueçamos de ajustar o argumento passado ao
# decorador.
#
# Sem entrar em muito detalhes sobre como essa parte funciona, o módulo
# **inspect** pode nos ajudar.
# Esse módulo é capaz de extrair o número de parâmetros de uma função, de
# maneira que conseguiremos descobrir essa informação sem precisar passá-la
# explicitamente ao decorador.
#
# A seguir temos o `import` e uma definição de função que realiza o que precisamos.


# %%
from inspect import signature

def numero_de_parametros(func):

    sig = signature(func)
    params = sig.parameters

    return len(params)

#%% [markdown]
#
# E aí podemos utilizar a `curry_ultimo` pra fazer o decorador.

#%%
def curry_tudo(func):

    n = numero_de_parametros(func)

    for _ in range(n - 1):
        func = curry_ultimo(func)

    return func

@curry_tudo
def soma_4_curried_tudo(x, y, z, w):
    return x + y + z + w

@curry_tudo
def soma_5_curried_tudo(x, y, z, w, v):
    return x + y + z + w + v

assert soma_4_curried_tudo(1)(2)(3)(4) == 1 + 2 + 3 + 4
assert soma_5_curried_tudo(1)(2)(3)(4)(5) == 1 + 2 + 3 + 4 + 5