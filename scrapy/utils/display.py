"""
pprint and pformat wrappers with colorization support
"""

import sys
from packaging.version import parse
from platform import version
from pprint import pformat as pformat_


def _colorize(text, colorize=True):
    if not colorize or not sys.stdout.isatty():
        return text
    try:
        import pygments.util
        from pygments.formatters import get_formatter_by_name
        from pygments import highlight
        from pygments.lexers import PythonLexer
    except ImportError:
        return text

    # All Windows versions >= "10.0.14393" interpret ANSI escape sequences
    # using terminal processing.
    #
    # Enable enivornment variable `ENABLE_VIRTUAL_TERMINAL_PROCESSING`
    # to activate terminal processing.
    if sys.platform == "win32" and parse(version()) >= parse("10.0.14393"):
        try:
            import ctypes
            from ctypes import FormatError
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            # set `ENABLE_VIRTUAL_TERMINAL_PROCESSING` flag
            if not kernel32.SetConsoleMode(handle, 7):
                raise ValueError
        except ValueError:
            sys.stderr.write(FormatError(kernel32.GetLastError()))
            return text
    if _color_support_info() == 256:
        format_alias = 'terminal256'
        format_options = {'style': 'default'}
    else:
        format_alias = 'terminal'
        format_options = {'bg': 'dark'}
    try:
        formatter = get_formatter_by_name(format_alias, **format_options)
    except pygments.util.ClassNotFound as err:
        sys.stderr.write(str(err) + "\n")
        formatter = get_formatter_by_name(format_alias)

    return highlight(text, PythonLexer(), formatter)


def _color_support_info():
    try:
        import curses
    except ImportError:
        # Usually Windows, which doesn't have great curses support
        return 16
    curses.setupterm()
    return curses.tigetnum('colors')


def pformat(obj, *args, **kwargs):
    return _colorize(pformat_(obj), kwargs.pop('colorize', True))


def pprint(obj, *args, **kwargs):
    print(pformat(obj, *args, **kwargs))
