def merge_dicts(d1, d2):
    for key in d2:
        val2 = d2[key]
        if key in d1:
            val1 = d1[key]
            if type(val1) == dict and type(val2) == dict:
                merge_dicts(val1, val2)
            elif type(val1) == list and type(val2) == list:
                d1[key] = val1 + val2
            elif type(val1) == tuple and type(val2) == tuple:
                d1[key] = val1 + val2
            elif type(val1) == set and type(val2) == set:
                d1[key] = val1 | val2
            else:
                d1[key] = val2
        else:
            d1[key] = val2
dict_a = {'a': 1, 'b': {'c': 1, 'f': 4}}
dict_b = {'d': 1, 'b': {'c': 2, 'e': 3}}
merge_dicts(dict_a, dict_b)
print(dict_a)
