import unittest
from typing import Union, Collection, Optional
from typomancy.handlers import type_wrangler


class TestBuiltins(unittest.TestCase):
    def test_str(self):
        value = "test"
        cast = type_wrangler(value, str)
        self.assertEqual(cast, value)
        value = "second_te,sdf.,f,124-014dfjlsdfj,123,2kfkfjst"
        cast = type_wrangler(value, str)
        self.assertEqual(cast, value)
        return

    def test_bool(self):
        self.assertTrue(type_wrangler("true", bool))
        self.assertTrue(type_wrangler("True", bool))
        self.assertFalse(type_wrangler("false", bool))
        self.assertFalse(type_wrangler("False", bool))
        self.assertTrue(type_wrangler("1", bool))
        self.assertFalse(type_wrangler("0", bool))
        self.assertRaises(TypeError, type_wrangler, ["123", bool])
        return

    def test_int(self):
        value = "1"
        cast = type_wrangler(value, int)
        self.assertEqual(cast, 1)
        value = "1.0"
        cast = type_wrangler(value, int)
        self.assertEqual(cast, 1)

        value = "1.1"
        self.assertRaises(TypeError, type_wrangler, (value, int))

        return

    def test_float(self):
        value = "1"
        cast = type_wrangler(value, float)
        self.assertEqual(cast, 1.0)
        value = "1.1"
        cast = type_wrangler(value, float)
        self.assertEqual(cast, 1.1)
        value = "-1.1"
        cast = type_wrangler(value, float)
        self.assertEqual(cast, -1.1)
        self.assertRaises(TypeError, type_wrangler, ("test", float))
        return

    def test_list(self):
        value = "1,2,3,4"
        cast = type_wrangler(value, list)
        self.assertEqual(cast, [1,2,3,4])

        value = "'a','b'"
        cast = type_wrangler(value, list)
        self.assertEqual(cast, ["a", "b"])

        value = "9"
        cast = type_wrangler(value, list)
        self.assertEqual(cast, [9])

        value = "'abc', 'def', 'ghi,jkl', 'mnop'"
        cast = type_wrangler(value, list)
        self.assertEqual(cast, ["abc", "def", "ghi,jkl", "mnop"])
        return

    def test_set(self):
        value = "2,3,4,5"
        cast = type_wrangler(value, set)
        # sets are unordered, assertEqual looks at elements; instead, confirm that the sets entirely overlap
        s = {2,3,4,5}
        diff0 = s.difference(cast)
        diff1 = cast.difference(s)
        self.assertTrue(len(diff0) == 0)
        self.assertTrue(len(diff1) == 0)

        value = "4, '5'"
        cast = type_wrangler(value, set)
        s = {4, '5'}
        diff0 = s.difference(cast)
        diff1 = cast.difference(s)
        self.assertTrue(len(diff0) == 0)
        self.assertTrue(len(diff1) == 0)

        value = "4"
        cast = type_wrangler(value, set)
        self.assertEqual(cast, {4})

        value = "4, 4, 5"
        self.assertRaises(TypeError, type_wrangler, (value, set))
        return

    def test_tuple(self):
        value = "5,6,7"
        cast = type_wrangler(value, tuple)
        self.assertEqual(cast, (5,6,7))

        value = "'a', 'b', 'c'"
        cast = type_wrangler(value, tuple)
        self.assertEqual(cast, ("a", "b", "c"))

        value = "2.0"
        cast = type_wrangler(value, tuple)
        self.assertEqual(cast, (2.0,))
        return


class TestTypings(unittest.TestCase):
    def test_Union(self):
        value = "2"
        # could be an int, float, or str
        # str has lowest priority since it always works
        cast = type_wrangler(value, Union[int])
        self.assertEqual(cast, 2)
        cast = type_wrangler(value, Union[float])
        self.assertEqual(cast, 2.0)
        cast = type_wrangler(value, Union[str])
        self.assertEqual(cast, "2")
        cast = type_wrangler(value, Union[float, int])
        self.assertEqual(cast, 2)
        cast = type_wrangler(value, Union[str, float])
        self.assertEqual(cast, 2.0)
        self.assertTrue(type(cast) is not str)  # str has lower priority
        cast = type_wrangler(value, Union[int, str])
        self.assertEqual(cast, 2)
        self.assertTrue(type(cast) is not str)  # str has lower priority
        cast = type_wrangler(value, Union[str, bool])
        self.assertEqual(cast, "2")
        cast = type_wrangler(value, Union[str, list])
        self.assertEqual(cast, [2])

        value = "2.2"
        # could be float or str
        cast = type_wrangler(value, Union[float, int])
        self.assertEqual(cast, 2.2)
        cast = type_wrangler(value, Union[int, str])
        self.assertEqual(cast, "2.2")
        self.assertRaises(TypeError, type_wrangler, value, Union[int, bool])
        return

    def test_Collection(self):
        # test ints
        value = "1,2,3,4"
        cast = type_wrangler(value, Collection[int])
        self.assertTrue(issubclass(type(cast), Collection))
        # Check that every element is an int
        for el in cast:
            self.assertTrue(type(el) is int)

        # test floats
        value = "1, 1.0, 1.4, 1.2"
        cast = type_wrangler(value, Collection[float])
        self.assertTrue(issubclass(type(cast), Collection))
        for el in cast:
            self.assertTrue(type(el) is float)

        # test str
        value = "a, f, 6, d, 2398.9"
        cast = type_wrangler(value, Collection[str])
        self.assertTrue(issubclass(type(cast), Collection))
        for el in cast:
            self.assertTrue(type(el) is str)

        # test union
        value = "1, 1.1, abc, a1.125f3, 2.42334f"
        cast = type_wrangler(value, Collection[Union[int, float, str]])
        self.assertTrue(issubclass(type(cast), Collection))
        self.assertTrue(cast[0] == 1)
        self.assertTrue(cast[1] == 1.1)
        self.assertTrue(cast[2] == "abc")
        self.assertTrue(cast[3] == "a1.125f3")
        self.assertTrue(cast[4] == "2.42334f")

        self.assertRaises(TypeError, type_wrangler, value, Collection[Union[int, float]])
        cast = type_wrangler(value, Collection[Union[int, str]])
        self.assertTrue(cast[0] == 1)
        self.assertTrue(cast[1] == "1.1")
        self.assertTrue(cast[2] == "abc")
        self.assertTrue(cast[3] == "a1.125f3")
        self.assertTrue(cast[4] == "2.42334f")
        return

    def test_Optional(self):
        value = ""
        cast = type_wrangler(value, Optional[str])
        self.assertTrue(cast is None)

        value = "123"
        cast = type_wrangler(value, Optional[str])
        self.assertEqual(cast, "123")
        cast = type_wrangler(value, Optional[int])
        self.assertEqual(cast, 123)

        value = ""
        cast = type_wrangler(value, Optional[int])
        self.assertTrue(cast is None)
        return
