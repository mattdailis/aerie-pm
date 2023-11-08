def group_by(elements, key):
    res = {}
    for element in elements:
        value = key(element)
        if value not in res:
            res[value] = []
        res[value].append(element)
    return res
