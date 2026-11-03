import re


class MissingKeysError(KeyError):
    """Raised when placeholders reference keys absent from the mapping.

    Subclasses KeyError so callers that already catch KeyError keep working,
    but the message lists every missing key so a single failure tells the whole
    story instead of one key at a time.
    """

    def __init__(self, missing):
        self.missing = tuple(missing)
        super().__init__(self.missing)

    def __str__(self):
        return "missing keys: " + ", ".join(repr(k) for k in self.missing)


# Matches ${name} or {{name}}. The name is any run of characters that are not
# whitespace and not a closing brace. This deliberately excludes nested braces
# so that "${a{b}}" is not silently treated as a placeholder named "a{b}".
_PATTERN = re.compile(r"\$\{([^\s{}]+)\}|\{\{([^\s{}]+)\}\}")


def _iter_placeholders(text):
    """Yield (start, end, name) for each placeholder in text, left to right."""
    for match in _PATTERN.finditer(text):
        # Exactly one of the two groups is non-None; the alternation guarantees it.
        name = match.group(1) if match.group(1) is not None else match.group(2)
        yield match.start(), match.end(), name


class Substitutor:
    """Replaces ${name} and {{name}} placeholders using a mapping.

    The mapping is read through its __getitem__ on every call, so a mutable
    dict passed at construction reflects later updates. This is the behaviour
    most callers expect from a small formatting helper.
    """

    def __init__(self, values):
        self._values = values

    def substitute(self, text):
        """Return text with every placeholder replaced by str(values[name]).

        Raises MissingKeysError listing every key that was referenced but not
        present. The error is raised before any replacement is applied, so a
        failed call never returns a half-substituted string.
        """
        placeholders = list(_iter_placeholders(text))
        missing = []
        seen = set()
        for _, _, name in placeholders:
            if name in seen:
                continue
            seen.add(name)
            try:
                self._values[name]
            except KeyError:
                missing.append(name)
        if missing:
            raise MissingKeysError(missing)

        # Build the result by slicing around each placeholder. This avoids a
        # second regex pass and keeps the original text intact for unmatched
        # regions, including any stray braces.
        pieces = []
        cursor = 0
        for start, end, name in placeholders:
            pieces.append(text[cursor:start])
            pieces.append(str(self._values[name]))
            cursor = end
        pieces.append(text[cursor:])
        return "".join(pieces)

    __call__ = substitute


def substitute(text, values):
    """One-shot helper: Substitutor(values).substitute(text)."""
    return Substitutor(values).substitute(text)
