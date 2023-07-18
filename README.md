# Typomancy
###### "Cheese or typos, I'm not sure."
Typomancy is a Python package for parsing string inputs and converting them into data types expected by a Python 
function or class using type annotations.

The purpose is to facilitate the interaction between user inputs supplied through a public-facing interface (e.g., HTML page) and 
a Python-based backend. Since end users shouldn't need to know about expected datatypes, their inputs are loosely-structured 
strings. The typical solution would be for functions to parse the input and perform the typecasting. This is fine, but in the case 
of inherited classes, it seems cleaner to perform the typecasting generically to avoid requiring all children to do similar
typecasting.  
  
The package makes use of Python's `typing` library in addition to Python's built-in types (`int`, `str`, `bool`, etc.). Typomancy 
performs opinionated typecasting for non-specific type annotations, casting the argument to a built-in type that satisfies the 
annotation. For example, `Collection` and `Iterable` would cause the input to be cast to `tuple`. Similarly, `Collection[str]`
causes the input to be cast to a `tuple` with `str` elements.