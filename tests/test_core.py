import unittest

from template_variable_placeholder_substitutor import (
    MissingKeysError,
    Substitutor,
    substitute,
)


class SubstituteTests(unittest.TestCase):
    def test_dollar_braces(self):
        self.assertEqual(substitute("hello ${name}", {"name": "ada"}), "hello ada")

    def test_double_braces(self):
        self.assertEqual(substitute("hello {{name}}", {"name": "ada"}), "hello ada")

    def test_mixed_styles(self):
        got = substitute("${a} and {{b}}", {"a": 1, "b": 2})
        self.assertEqual(got, "1 and 2")

    def test_non_string_values_are_stringified(self):
        self.assertEqual(substitute("${n}", {"n": 42}), "42")
        self.assertEqual(substitute("{{n}}", {"n": None}), "None")

    def test_repeated_placeholder(self):
        self.assertEqual(substitute("${x}-${x}", {"x": "y"}), "y-y")

    def test_no_placeholders(self):
        self.assertEqual(substitute("plain text", {}), "plain text")

    def test_empty_string(self):
        self.assertEqual(substitute("", {}), "")

    def test_unmatched_braces_are_left_alone(self):
        self.assertEqual(substitute("a { b } c", {}), "a { b } c")
        self.assertEqual(substitute("${}", {}), "${}")
        self.assertEqual(substitute("${", {}), "${")
        self.assertEqual(substitute("{{}}", {}), "{{}}")

    def test_whitespace_inside_braces_is_not_a_placeholder(self):
        self.assertEqual(substitute("${ a }", {}), "${ a }")
        self.assertEqual(substitute("{{ a }}", {}), "{{ a }}")

    def test_nested_braces_are_not_placeholders(self):
        self.assertEqual(substitute("${a{b}}", {"a{b": "no"}), "${a{b}}")

    def test_missing_single_key(self):
        with self.assertRaises(MissingKeysError) as ctx:
            substitute("hi ${name}", {})
        self.assertEqual(ctx.exception.missing, ("name",))
        self.assertIn("name", str(ctx.exception))

    def test_missing_keys_are_all_listed_once(self):
        with self.assertRaises(MissingKeysError) as ctx:
            substitute("${a} ${b} ${a}", {"c": 1})
        self.assertEqual(ctx.exception.missing, ("a", "b"))

    def test_missing_error_is_a_key_error(self):
        with self.assertRaises(KeyError):
            substitute("${nope}", {})

    def test_failed_call_does_not_return_partial_output(self):
        # The error must be raised before any substitution, so no string is
        # produced at all. We check by confirming nothing is returned.
        with self.assertRaises(MissingKeysError):
            substitute("${a}${b}", {"a": 1})

    def test_substitutor_reflects_mapping_updates(self):
        values = {"name": "ada"}
        sub = Substitutor(values)
        self.assertEqual(sub.substitute("${name}"), "ada")
        values["name"] = "grace"
        self.assertEqual(sub.substitute("${name}"), "grace")

    def test_substitutor_is_callable(self):
        sub = Substitutor({"x": "1"})
        self.assertEqual(sub("${x}"), "1")

    def test_substitutor_accepts_custom_mapping(self):
        class Mapping:
            def __getitem__(self, key):
                if key == "k":
                    return "v"
                raise KeyError(key)

        self.assertEqual(Substitutor(Mapping()).substitute("${k}"), "v")

    def test_missing_keys_error_exposes_attribute(self):
        err = MissingKeysError(["x", "y"])
        self.assertEqual(err.missing, ("x", "y"))
        self.assertEqual(err.args, (("x", "y"),))


if __name__ == "__main__":
    unittest.main()
