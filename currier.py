# %% [markdown]
# # Decorator for Currying in Python
#
#
# In this text we are going to think about how to write decorators that are able
# to curry functions.
#
# Currying is the process of converting a multiple argument function into
# multiple single argument functions.
# Supose we have a 3 argument function function `f`.
# Such a function, in Python, is applyed like so: `f(x, y, z)`,
# with all of the 3 arguments being bundled (as a tuple) and passed to `f` simultaneously.
# The function then returns precisely 1 value (even if the value is `None` or a tuple of values)
# A curried version of `f` allows for each of the 3 arguments to be passed separetely
# Something like `f(x)(y)(z)` (Or `f(x)(y)` waiting for z).
# This behaviour exists in Python, even if it's uncommon.
# But there are conditions for functions to be able to act like that.
# Let's visualize this by splitting things up and naming the steps.
# ```python
# f_x = f(x)
# f_x_y = f_x(y)
#
# assert f(x)(y)(z) == f_x_y(z)
# ```
# %% [markdown]
# Function `f` was kept undefined in the above example, and for good reason.
# The above code would produce an error for usual Python functions.
# The question is, what sort of unusual function `f` could be called like this?
#
# To work with a concrete example, let's use a simple multiple argument function:
# usual adition of 2 values.
# %%
def usual_add(x, y):
    return x + y

assert usual_add(3, 5) == 3 + 5

# %% [markdown]
# So, we wannt to pass the arguments `3` and `5`, one at a time.
# Notice, first, we can define a function that adds 3 to whatever value we pass:
# %%
def add_3(y):
    return 3 + y
# %% [markdown]
# But we don't want to be able to only add the value 3 to any other, we want
# it to be an argument.
# What we want to do here is find a way of building `add_x` functions, where
# x is an argument that can be passed.
#
# This pattern of receiving a value and returning a fuction is known as closure.
# And it is a feature of the Python languge (among many many others).
#
# In Python, we are allowed to define funnctions inside another function's body.
# We can also pass functions around as arguments, or return them.
# This is sufficient for our addition example.
# %%
def add_constructor(x):

    def add_x(y):               # add_x being definned internally
        return usual_add(x, y)  # notice add_x "remembers" the passed x value
                                # despite not having itself an x argument
    return add_x                # return value of add_constructor function
                                # is the add_x function

add_3 = add_constructor(3)      # We can now define add_3 function, by calling 
                                # add_constructor with the value 3
                                # add_3 will then be the returned add_x function
                                # wich "remembers" the value 3 to pass to usual_add

assert add_3(5) == 3 + 5

# %% [markdown]
# Works!
#
# But we still haven't reached are goal.
# In the code above, we made a intermediate function to fix the value for
# the first argument
# We want to be able to acomplish both steps at once
#
# If, however, we observe carefully what was done, we can see all the work has
# been done already.
# If `add_3 == add_constructor(3)` and `add_3(5) == 8`, we expect for
# `add_constructor(3)(5)` to result in  `8`.
# %%
curried_add = add_constructor

assert curried_add(3)(5) == 3 + 5

# %% [markdown]
# Cool! Now, let's try to abstract this pattern into a decorator.
#
# For this, is better to briefly discuss what decorators are and how they are defined
#
# ## Decorators
#
# Decorator is a (Python specific) sintatic sugar for a particular kind of closure.
# The following one:
#
# ```python
# def decorator(func_to_decorate):
#
#   def new_decorated_func(*args):
#       ... # func_to_decorate is (usually) applied here somehow
#
#   return new_decorated_func
#
# def my_func(*args):
#     ...
#
# my_func = decorator(my_func)
# ```
# Decorators are closures for functions.
# In particular, decoratos have a function for its paremeter,
# and they return a function.
# Also, the decorator sintax includes a step where the original function is
# replace by the one returned by the decorator.
# With the sintactic sugar, the definition given above would be:
# ```python
# @decorator
# def my_func(*args):
#     ...
# ```
#
# The key insight here is that `curried_add` is defined exactly like `add_constructor`,
# even conceptually.
# Both expect a single value, to return a function which expects another value.
# This means we are not yet in decorator land, since we need a function as an argument.
#
# So, going back to our `usual_add` example, we need to find a way to, with a function,
# alter the behaviour of the `usual_add` function itself.
# instead of receiving 2 values and returning 1 value we want it to recieve 1 value
# and return a function (that will then take the other value and return the final result)
#
# In defining `curried_add`, we did use `usual_add` inside the closure.
# So, if `usual_add` was a function argument, we could apply it programatically.
# In fact, we could pass in any function we want, and the currying behaviour should persist.
#
# To do this, we have to wrap what we already done into yet another layer of function creation.
#%%
def two_step_curry(uncurried_func):

    def gets_fst_arg(x):

        def gets_snd_arg(y):
            # Knowing both arguments, we can apply uncurried_func
            return uncurried_func(x, y)

        return gets_snd_arg

    return gets_fst_arg

@two_step_curry
def two_step_add(x, y):
    return x + y

assert two_step_add(3)(5) == 3 + 5


#%% [markdown]
#
# Probably obvious by the names of the functions involved but...
# there are some limitations in the solution we just found.
#
# Let's deal with the simpler first
#
# `two_step_curry` defined a function that takes a single argument,
# aptly named `get_fst_arg`.
# However, the function it returns recieves a single argument and then
# has to return a value.
# This means we can only apply the solution to functions of 2 arguments, exactly.
#
# We can lightly adjust our implementation to produce a decorator to partially
# apply the first argument only, returning a function that takes a paremeter
# and returns a function with one less argument, however many.
# To acomplish this, we're going to use the unpacking operator `*`.
#
# We've used `*args` before, in the decorator example, without more explanation.
# For a superficial explanation, the `*` operator unpacks iterable objects.
# Usually this means lists or tuples.
# In the case of function arguments, they will be tuples.
# Dicts (and map-like objects) have `**`. We won't go trough it in detail, but
# they are also used in these contexts.
# `**kwargs` is used to unpack keyword arguments in functions, for instance.
# We will refrain from using `**kwargs` here, so that the code reads easier.
#
# Back to currying...
# By adding a `*args` to the innermost function, we can abstract the number of arguments.
# This will make the original function take all remaining arguments, however many.

#%%
def fst_arg_curry(uncurried_func):

    def get_fst_arg(x):

        def get_other_args(*args):
            # Apply uncurried_func and returns
            return uncurried_func(x, *args)

        return get_other_args

    return get_fst_arg

@fst_arg_curry
def add_3_values(x, y, z):
    return x + y + z

assert add_3_values(3)(5, 7) == 3 + 5 + 7

#%% [markdown]
#
# Passing last 2 arguments at once was no accident.
# Let's see what happens if we try to use it as fully curried.

#%%
try:
    add_3_values(3)(5)(7)
except TypeError as t:
    assert str(t) == "add_3_values() missing 1 required positional argument: 'z'"

#%% [markdown]
# We get a `TypeError` informing us about not providing an argument.
# In particular, we missed passing `z`.
#
# This indicates `fst_arg_curry` is indeed a good name.
# Let's understand what happened.
# By following what the decorator does, we can see that `add_3_values` was
# replace by a `get_fst_arg` function.
# We can actually read this from a `TypeError` message if we pass no arguments to it
# %%
try:
    add_3_values()
except TypeError as t:
    assert str(t) == "get_fst_arg() missing 1 required positional argument: 'x'"
# %% [markdown]
# So, when we call `add_3_values(3)` we are getting back the function returned by
# `get_fst_arg`, which is `get_other_args`.
# Since `get_other_args` is uncurried, `y` and `z` are its arguments.
# If we give only 5 for `y`, `z` is still missing.
#
# And, this is also why we can't just reaply our decorator to get the fully
# curried version.

#%%
@fst_arg_curry
@fst_arg_curry
def add_3_values_reapply_curry(x, y, z):
    return x + y + z

try:
    add_3_values_reapply_curry(3)(5)(7)
except TypeError as t:
    assert str(t) == "get_fst_arg() takes 1 positional argument but 2 were given"

#%% [markdown]
#
# We can, however, keep reapplying `fst_arg_curry` if we also keep applying
# some value to the results.
#%%
@fst_arg_curry
def add_3_values_strangely(x, y, z):
    return x + y + z

puts_3_to_sum = add_3_values_strangely(3)
puts_3_to_sum = fst_arg_curry(puts_3_to_sum)

assert puts_3_to_sum(5)(7) == 3 + 5 + 7

#%% [markdown]
#
# That code is strange. Confusing, even
# Take your time with it.
# Perhaps, fire up a Python console or something, and poke at it a little.
# Or maybe make some tea or a coffe.
#
# Ok. Let's remind ourselves what `@fst_arg_curry` does.
# To meake it easier to understand, let's cut out the innermost functions.
# At this moment they are mostly noise.
#
# ```python
# def fst_arg_curry(uncurried_func):
# 
#   def get_fst_arg(x):
#     ...
#   
#   return get_fst_arg
# ```
#
# After applying the decorator once, we have ourselves a 1 argument function
# It makes no sense to curry it since it it already curried.
# The function it returns is the one that still isn't curried.
#
# Ok, ok. So what do we learn from this particular failure?
# Well, one way to interpret what happened is that, by fundamentally
# altering the function signature, we prevent ourselves from recurring
# to the same problem, and can't then reuse the same solution.
#
# Let's, then, look for a solution that preserves our function signature enough
# for us to reapply our solution.
# We need a decorator that, given a function produces an uncurried function, but
# when given all parameters, produces a single argument function.
# Something like `add_3(x, y, z) -> add_2_then_1(x, y)(z)`
# That way, if we keep reapplying our solution, we keep falling into the same
# situation as before, except with one argument less.
# Like `add_2_then_1(x, y) -> add_1_at_a_time(x)(y)` being a 1 argument function
#
# Let's try our luck with addition function first.

#%%
def add_3_values_curried_last(x, y):

    def get_last_and_add_all(z):
        return x + y + z

    return get_last_and_add_all

assert add_3_values_curried_last(3, 5)(7) == 3 + 5 + 7

#%% [markdown]
#
# Looks promising.
# `add_3_values_curried_last` is a 2 argument function, so it makes sense
# to curry it.
#
# Let's try:

#%%
add_3_curried = fst_arg_curry(add_3_values_curried_last)

assert add_3_curried(3)(5)(7) == 3 + 5 + 7

#%% [markdown]
#
# Now we're cooking with fire!
# For our next trick, abtracting this into a decorator...
#%%
def curry_last(func):

    def func_with_last_applied(*args):

        def get_last_arg(arg):
            return func(*args, arg)

        return get_last_arg

    return func_with_last_applied

@curry_last
def add_2_values_then_a_3rd(x, y, z):
    return x + y + z

assert add_2_values_then_a_3rd(3, 5)(7) == 3 + 5 + 7

#%% [markdown]
# Now we have a partially curried function, but one that still takes in 2
# arguments and can, therefore, be curried.
#
# We could apply `fst_arg_curry` and be done with currying the `add_3` function.
# But, as we've been pointing to, we can also reapply `curry_last`.
# In this 3 argument example, at this point it makes no difference which one we apply.
# But using only one currying function makes it easier to read, so...

#%%
@curry_last
@curry_last
def add_3_curried(x, y, z):
    return x + y + z

assert add_3_curried(3)(5)(7) == 3 + 5 + 7

#%% [markdown]
# There is still some more generalization to be done here.
# The way it is, we need to apply `curry_last` several times
# One less then the number of arguments, actually.
# We don't like to repeat ourselves that much.
#
# It's better to find a way to programatically specify how many times to apply
# our `curry_last` decorator.
# After all the complication we've been trough, this one is a bit easier.

#%%
def curry_n_args(n, func):

    for _ in range(n-1):
        func = curry_last(func)

    return func

def add_3_using_n_args(x, y, z):
    return x + y + z

add_3_using_n_args = curry_n_args(3, add_3_using_n_args)

assert add_3_using_n_args(3)(5)(7) == 3 + 5 + 7

#%% [markdown]
# Ok, it works, but we sort of ruined the docorator.
# At least in the fact we can't use the `@` sintax any more.
# The thing preventing us from using it is that decorators are required
# to be single argument functions.
# ALso, the argument must be, itself, a function.
# But it looks like we need a decorator which can take other arguments.
# How can this possibly be?
# We've just sen decorators must be single argument functions!
#
# Well, this is where things become truly interesting!
# We want a multiple argument function, but we also want to be able to
# pass in all of its arguments, except for the last one and.. that is it!
# This is precisely what we are doing here the whole time.
# What we need to do is curry the last argument of our multiple argument decorator.
#%%
curry = curry_last(curry_n_args)

@curry(4)
def add_4_curried(x, y, z, w):
    return x + y + z + w

assert add_4_curried(1)(2)(3)(4) == 1 + 2 + 3 + 4

#%% [markdown]
# That is pretty good.
# But we can go back a step and find a different solution.
# There is still a way to use `fst_arg_curry`.
#
# The problem there was that we could not reaply the decorator to a single
# argument function.
# Well, more accurately, we couldn't reaply the decorator until
# we passed it an argument.
# There is room to work with that!
#
# Idea is for the decorator to return a 1 argument fuction, but one
# with the capability to further curry arguments when an argument is passed to it.
#
# %%
def keep_currying_it(func):

    def get_one_arg(arg):
        get_one_arg_curried_func = fst_arg_curry(func)
        applied_one_arg = get_one_arg_curried_func(arg)
        # at this point apply_one_arg is a regular python function
        # because of fst_arg_curry this one can receive any ammount of arguments
        return keep_currying_it(applied_one_arg)

    return get_one_arg

@keep_currying_it
def keep_adding(x,y,z,w):
    return x+y+z+w

assert keep_adding(1)(2)(3)(4) != 10
assert keep_adding(1)(2)(3)(4)(5) != 10
assert keep_adding(1)(2)(3)(4)(5) != 15

# %% [markdown]
# Ok, this time there was no `Exception` in sight. What gives?
# The big problem there is that func is never applied.
# So the original, unaltered `keep_adding` never gets called and can't
# produce a result.
# There is also the fact that `fst_arg_curry` returns a function with `*args`.
# Because of it, we can never pass too many or too few arguments,
# as long as we pass them one at a time
#
# But the import thing is, for now, that we are able to pass in arguments one
# at a time.
# We just need to find out how to apply `func`
#
# Let's start by following the code, line by line, in a small example.
# %%
def another_add(x,y,z):
    return x+y+z

get_one_arg_curried_func = fst_arg_curry(another_add)
applied_1 = get_one_arg_curried_func(1)

assert applied_1(2,3) == 1+2+3

# %% [markdown]
# Now, `applied_1` had its first argument curried just fine.
# So far so good.
# Let's keep going.
# Notice that, thos time we are to apply our decorator to `applied_1`
# %%
get_one_arg_curried_func = fst_arg_curry(applied_1)
applied_1_2 = get_one_arg_curried_func(2)

assert applied_1_2(3) == 1+2+3
# %% [markdown]
# One more step...
#%%
get_one_arg_curried_func = fst_arg_curry(applied_1_2)
applied_1_2_3 = get_one_arg_curried_func(3)

assert applied_1_2_3() == 1+2+3

# %% [markdown]
# At this point, we applied every argument already.
# But there is no base to that recursion.
# There is nothing in that code forcing the evaluation
# Nothing like `applied_1_2(3)` or `applied_1_2_3()` anywhere.
#
# The next step is to `keep_currying_it`.
# From here on, we are no longer able to end the function call without a `TypeError`
# informing the passing of more than 3 positional arguments.
#
# So, we need to check wether or not we have enough arguments to apply the function
# There are good ways of doing it.
# But we will do something else.
# We are just going to try to apply the function.
# If it returns a value it returns a value.
# Otherwise, we apply the decoretor recursively.
# %%
def curry(func):

    def get_one_arg(arg):
        try:
            return func(arg)
        except TypeError:
            applied_one_arg = fst_arg_curry(func)(arg)
            return curry(applied_one_arg)

    return get_one_arg

@curry
def add_4(x,y,z,w):
    return x+y+z+w

@curry
def add_5(x,y,z,w,r):
    return x+y+z+w+r

assert add_4(1)(2)(3)(4) == 1+2+3+4
assert add_5(1)(2)(3)(4)(5) == 1+2+3+4+5
# %% [markdown]
# We did it!
# By putting that function call as the first step (the base of our recursion)
# we made sure to apply the function at just the right time... well,
# we kept trying when it wasn't time, but we were ready for it.
#
# It's interesting to note that we can only pass arguments oe at a time.
# This is the case because what the decorator actually returns is a version of
# `get_one_arg`, which is a single argument function.
# And we aren't going to miss any TypeErrors given from the user side of things
# because if an user tries to pass more than one value at a time, the `TypeError`
# happens at the `get_one_arg`, not with the internal call of `func`.
# %%
try:
    add_4(1)(2)(3,4)
except TypeError as t:
    assert str(t) == "get_one_arg() takes 1 positional argument but 2 were given"

try:
    add_4(1)(2)()
except TypeError as t:
    assert str(t) == "get_one_arg() missing 1 required positional argument: 'arg'"

# %% [markdown]
# We've come very far and made a very cool thing from scratch!
# That said, the point of the exercise was to learn more about how Python
# works.
# In particular, how decorators work. How we can write decorators with arguments.
#
# If you do need to curry something for real, then don't use this code, use
# the functools module.

# %%
