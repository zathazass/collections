'''
This module about convert various types of format based on list of dictionaries data.
If suppose we collect data from db using sql connection query, then may be modify it as
list of dictionaries based on column and rows. So that I created this module for extracting 
and modifying data easily without every time you want to do it in your projects.

module name zlidy means zass's list of dictionaries.

Example Data:
we can fetch this data
----------------------
[{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]

By using this code
------------------
cursor.execute(query)
columns = [col[0] for col in cursor.description]
rows = cursor.fetchall()
data = [dict(zip(columns, row)) for row in rows]


APIs
---------
1. sorting (asc, desc)          -> ld_sort_by_key

2. extract (pk)
    dict                        -> ld_extract_as_dict_by_pk
    list (ordered)              -> ld_extract_as_dict_by_ordered_list

3. group (with/without order)   -> ld_group_by_key

4. tuple                        -> ld_extract_as_tuple

NOTE: ld_ indicates input data type [{}] list of dictionaries

'''


def ld_sort_by_key(iter, key, reverse=False):
    '''
    >>> data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 6}, {'a': 3, 'b': 4}]
    >>> ld_sort_by_key(data, 'a')
    [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}]
    >>> ld_sort_by_key(data, 'a', reverse=True)
    [{'a': 5, 'b': 6}, {'a': 3, 'b': 4}, {'a': 1, 'b': 2}]
    '''
    return sorted(iter, key=lambda x: x[key], reverse=reverse)


def ld_extract_as_dict_by_pk(iter, key):
    '''
    >>> data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 6}, {'a': 3, 'b': 4}]
    >>> ld_extract_as_dict_by_pk(data, 'a')
    {1: {'a': 1, 'b': 2}, 5: {'a': 5, 'b': 6}, 3: {'a': 3, 'b': 4}}
    '''
    data = {}
    for i in iter:
        if i[key] in data: raise Exception(f'Key {key} is not a pk')
        data[i[key]] = i
    return data


def ld_extract_as_dict_by_ordered_list(iter):
    '''
    >>> data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 6}, {'a': 3, 'b': 4}]
    >>> ld_extract_as_dict_by_ordered_list(data)
    {'a': [1, 5, 3], 'b': [2, 6, 4]}
    '''
    data = {}
    for i in iter:
        for k in i.keys():
            data.setdefault(k, [])
            data[k].append(i[k])
    return data


def ld_group_by_key(iter, key, order=None, order_key=None):
    '''
    >>> data = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}, {'a': 1, 'b': 7}, {'a': 1, 'b': 3}]
    >>> ld_group_by_key(data, 'a')
    {1: [{'a': 1, 'b': 2}, {'a': 1, 'b': 7}, {'a': 1, 'b': 3}], 3: [{'a': 3, 'b': 4}], 5: [{'a': 5, 'b': 6}]}
    >>> ld_group_by_key(data, 'a', order='asc', order_key='b')
    {1: [{'a': 1, 'b': 2}, {'a': 1, 'b': 3}, {'a': 1, 'b': 7}], 3: [{'a': 3, 'b': 4}], 5: [{'a': 5, 'b': 6}]}
    '''
    data = {}
    for i in iter:
        data.setdefault(i[key], [])
        data[i[key]].append(i)

    if order is None: reverse = None
    elif order.lower() == 'asc': reverse = False
    elif order.lower() == 'desc': reverse = True
    else: reverse = None

    if reverse is not None and order_key is not None:
        for k in data.keys():
            data[k] = ld_sort_by_key(data[k], order_key, reverse=reverse)

    return data


def ld_extract_as_tuple(iter):
    '''
    >>> data = [{'a': 1, 'b': 2}, {'a': 5, 'b': 6}, {'a': 3, 'b': 4}]
    >>> ld_extract_as_tuple(data)
    ((('a', 1), ('b', 2)), (('a', 5), ('b', 6)), (('a', 3), ('b', 4)))
    '''
    data = []
    for i in iter:
        data.append(tuple(zip(i.keys(), i.values())))
    return tuple(data)