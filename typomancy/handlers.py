from ast import literal_eval
from collections import defaultdict as dd
from typing import Union, Collection, Optional
from types import NoneType
from collections import abc


def type_wrangler(input_data: str,
                  typecast):
    """
    Top-level type handler. Identifies the desired type and passes it off for type casting.
    Parameters
    ----------
    input_data : str
        String to parse and convert to specified type
    typecast
        Type to cast the input into.
    Returns
    -------
    Any
        The input_str parsed and cast to typecast

    Raises
    ------
    TypeError
        If the input_str could not be converted to the specified type.
    """
    if typecast is str:
        return input_data
    if _isbuiltin(typecast):
        # No need for anything fancy; builtins come with their own converters!
        try:
            if typecast is bool and isinstance(input_data, str):
                # JS has lower-case bools; need to check against that
                input_data = input_data[0].upper() + input_data[1:].lower()
            cast_data = literal_eval(input_data)  # "13" resolves to int, even if it would be fine as a float

            try:
                tmp_cast = typecast(cast_data)
                if _isequal(cast_data, tmp_cast):  # if there's no loss of data, do conversion; otherwise fail
                    cast_data = tmp_cast
                else:
                    raise TypeError(f"Converting input to type {typecast} results in data loss.")
            except TypeError as ex:
                tp = type(cast_data)
                if tp is float or tp is int or tp is str or tp is bool:
                    if typecast is list or typecast is tuple or typecast is set:
                        cast_data = typecast([cast_data])
                else:
                    raise ex

            if isinstance(cast_data, typecast):
                return cast_data
        except ValueError:  # be nice and assume that the error is in the type, not the user's input
            raise TypeError(f"Unable to convert input of type {type(input_data)} to {typecast}")
    elif _istyping(typecast):
        # Try to do casting
        caster = cast_map[typecast.__origin__]
        if caster is None:
            raise TypeError(f"Unable to convert input of type {type(input_data)} to {typecast}")
        cast_data = caster(input_data, typecast)
        return cast_data
    return


def _isbuiltin(type_to_check) -> bool:
    """Checks whether the specified type is a Python built-in"""
    return type_to_check.__class__.__module__ == "builtins"


def _istyping(type_to_check) -> bool:
    """Checks whether the specified type is a Python type from the typing module"""
    return type_to_check.__module__ == "typing"


def _isequal(data0, data1):
    """Compares the two inputs and returns True if they are meaningfully equal. The purpose is to be able to compare
    numeric types (ints/floats) using the same function as the comparison for iterables (tuples/lists). For our
    purposes, we don't care that tuples and lists are different, only that their contents are the same."""
    # Casting can cause data loss; without knowing the input types, we don't know which direction would result
    # in loss. The only way is to convert both inputs and make sure that data is conserved both ways
    class0 = data0.__class__
    class1 = data1.__class__
    if class0 is set or class1 is set:
        diff0 = set(data0).difference(set(data1))
        diff1 = set(data1).difference(set(data0))
        return (len(diff0) == 0) and (len(diff1) == 0)
    eq_class0 = data0 == class0(data1)
    eq_class1 = class1(data0) == data1
    return eq_class0 and eq_class1


def union_cast(data: str, typecast):
    """Attempts to cast data to one of the acceptable types listed in Union."""
    # Union is a list of acceptable types. Any of the possible arguments will work
    check_str = False
    if NoneType in typecast.__args__:
        return optional_cast(data, typecast)
    for typ in typecast.__args__:
        if typ is str:
            check_str = True
            continue
        else:
            try:
                cast_data = type_wrangler(data, typ)
                if type(cast_data) == typ or issubclass(type(cast_data), typ):
                    return cast_data
            except TypeError:
                continue
            except SyntaxError:
                continue
    if check_str:
        try:
            cast_data = type_wrangler(data, str)
            if type(cast_data) == str or issubclass(type(cast_data), str):
                return cast_data
        except TypeError:
            pass
    raise TypeError(f"Unable to convert input of type {type(data)} to {typecast}")


def collection_cast(data: str, typecast):
    """Attempts to cast data to a collection of one of the acceptable types listed in Collection."""
    # Easy for builtins, tricky for Union; elements can be any of the types inside
    # First need to be able to convert input to Collection, regardless of elements
    # We don't know yet what the elements will be; assume strings.
    # Separate elements by ','; use \ as escape char.
    split_data = split_with_escape(data, split_char=",", escape_char="\\")
    cast_collection = []
    for entry in split_data:
        cast_entry = type_wrangler(entry, typecast.__args__[0])  # Collection only takes 1 arg
        cast_collection.append(cast_entry)
    return cast_collection


def optional_cast(data: str, typecast):
    """Casts the input string to the optional argument. If the string is empty, returns None."""
    if len(data) == 0:
        return None
    else:
        return type_wrangler(data, typecast.__args__[0])


def split_with_escape(str_to_split: str, split_char: str = ",", escape_char="\\") -> list[str]:
    idx_list = get_all_indices(str_to_split, split_char, escape_char)
    return split_at_indices(str_to_split, idx_list)


def get_all_indices(str_to_check: str, str_to_find: str, escape_char="\\") -> list[int]:
    """Finds unescaped strings and returns their indices"""
    idx = 0
    find_len = len(str_to_find)
    idx_list = []
    while idx < len(str_to_check)-find_len:
        if str_to_check[idx:].startswith(str_to_find):
            idx_list.append(idx)
        elif str_to_check[idx:].startswith(escape_char):
            if str_to_check[idx+1:].startswith(str_to_find):
                idx += len(str_to_find)+1
            else:
                idx += 1
            continue
        idx += 1
    return idx_list


def split_at_indices(str_to_split: str, indices: list) -> list[str]:
    """Splits the input string at the specified indices."""
    full_idx = [-1] + indices.copy() + [len(str_to_split)+1]
    split_str = []
    for start_idx, end_idx in zip(full_idx, full_idx[1:]):
        s = str_to_split[start_idx+1: end_idx]
        split_str.append(s.strip())
    return split_str


def _configure_cast_map():
    cast_map = dd(lambda: None)
    cast_map[Union] = union_cast
    cast_map[Collection] = collection_cast
    cast_map[abc.Collection] = cast_map[Collection]
    cast_map[Optional] = optional_cast
    return cast_map


cast_map = _configure_cast_map()
