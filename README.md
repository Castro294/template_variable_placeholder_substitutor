# template_variable_placeholder_substitutor

Replaces `${name}` and `{{name}}` placeholders in a string with values from a
dictionary, raising one clear error that lists every missing key.

```python
from template_variable_placeholder_substitutor import substitute, MissingKeysError

print(substitute("Hello ${name}!", {"name": "Ada"}))
# Hello Ada!

print(substitute("Hello {{name}}!", {"name": "Ada"}))
# Hello Ada!

try:
    substitute("${greeting}, ${name}", {"name": "Ada"})
except MissingKeysError as exc:
    print(exc.missing)  # ('greeting',)
    print(str(exc))     # missing keys: 'greeting'
```

The exported names are `substitute`, `Substitutor`, and `MissingKeysError`.
`Substitutor` holds a mapping and exposes `substitute(text)` (also callable as
`__call__`), and reads the mapping on each call so later changes are visible.
`MissingKeysError` subclasses `KeyError` and exposes the missing names as the
`missing` tuple.

## Why this exists

String formatting helpers usually fail on the first missing key, which forces a
caller to fix one typo, run again, and repeat. This library scans the whole
template first and reports all missing keys at once. It also supports both
`${x}` and `{{x}}` because templates arrive from several sources and the two
styles are common in practice.

## The trade-off

Placeholder names are any run of non-whitespace characters that are not braces.
That means `${a{b}}` is *not* a placeholder, and neither is `${ a }`. The
library does not attempt to nest or parse braces; it treats the inner brace as
ordinary text. If you need a literal `${` in your output, no escape sequence is
provided — the library leaves unmatched sequences alone, so `${` with no
closing brace is returned verbatim.

## The awkward edge

A missing key is detected before any substitution happens, so a failed call
never returns a half-substituted string. Repeated placeholders are reported
once in the error and substituted everywhere on success.
