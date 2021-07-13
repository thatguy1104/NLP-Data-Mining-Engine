import itertools
from itertools import permutations, chain


list_1 = [1, 2, 7]
list_2 = ['AI', 'Reg. M']
all_combinations = []

unique_combinations = []
permut = itertools.permutations(list_1, len(list_2))
for comb in permut:
    zipped = zip(comb, list_2)
    unique_combinations.append(list(zipped))

r = list(chain.from_iterable(unique_combinations))
r = list(dict.fromkeys(r))
print(r)
