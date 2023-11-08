def make_table(columns, items, sort_by=None):
    if type(sort_by) == str:
        key = lambda x: x[sort_by]
    else:
        key = sort_by
    table = []
    if key is not None:
        items = sorted(items, key=lambda x: key(x))
    for issue in items:
        row = []
        for col in columns:
            if type(col) == str:
                row.append(issue[col])
            else:
                row.append(col(issue))
        table.append(row)
    return table