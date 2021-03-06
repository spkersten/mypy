# Stubs for argparse (Python 3.4)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Sequence

SUPPRESS = ... # type: Any
OPTIONAL = ... # type: Any
ZERO_OR_MORE = ... # type: Any
ONE_OR_MORE = ... # type: Any
PARSER = ... # type: Any
REMAINDER = ... # type: Any

class _AttributeHolder: pass

class HelpFormatter:
    def __init__(self, prog, indent_increment=2, max_help_position=24, width=None): pass
    def start_section(self, heading): pass
    def end_section(self): pass
    def add_text(self, text): pass
    def add_usage(self, usage, actions, groups, prefix=None): pass
    def add_argument(self, action): pass
    def add_arguments(self, actions): pass
    def format_help(self): pass

class RawDescriptionHelpFormatter(HelpFormatter): pass
class RawTextHelpFormatter(RawDescriptionHelpFormatter): pass
class ArgumentDefaultsHelpFormatter(HelpFormatter): pass
class MetavarTypeHelpFormatter(HelpFormatter): pass

class ArgumentError(Exception):
    argument_name = ... # type: Any
    message = ... # type: Any
    def __init__(self, argument, message): pass

class ArgumentTypeError(Exception): pass

class Action(_AttributeHolder):
    option_strings = ... # type: Any
    dest = ... # type: Any
    nargs = ... # type: Any
    const = ... # type: Any
    default = ... # type: Any
    type = ... # type: Any
    choices = ... # type: Any
    required = ... # type: Any
    help = ... # type: Any
    metavar = ... # type: Any
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _StoreAction(Action):
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _StoreConstAction(Action):
    def __init__(self, option_strings, dest, const, default=None, required=False, help=None,
                 metavar=None): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _StoreTrueAction(_StoreConstAction):
    def __init__(self, option_strings, dest, default=False, required=False, help=None): pass

class _StoreFalseAction(_StoreConstAction):
    def __init__(self, option_strings, dest, default=True, required=False, help=None): pass

class _AppendAction(Action):
    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None,
                 choices=None, required=False, help=None, metavar=None): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _AppendConstAction(Action):
    def __init__(self, option_strings, dest, const, default=None, required=False, help=None,
                 metavar=None): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _CountAction(Action):
    def __init__(self, option_strings, dest, default=None, required=False, help=None): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _HelpAction(Action):
    def __init__(self, option_strings, dest=..., default=..., help=None): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _VersionAction(Action):
    version = ... # type: Any
    def __init__(self, option_strings, version=None, dest=..., default=...,
                 help=''): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class _SubParsersAction(Action):
    def __init__(self, option_strings, prog, parser_class, dest=..., help=None,
                 metavar=None): pass
    def add_parser(self, name, **kwargs): pass
    def __call__(self, parser, namespace, values, option_string=None): pass

class FileType:
    def __init__(self, mode='', bufsize=-1, encoding=None, errors=None): pass
    def __call__(self, string): pass

class Namespace(_AttributeHolder):
    def __init__(self, **kwargs): pass
    def __eq__(self, other): pass
    def __ne__(self, other): pass
    def __contains__(self, key): pass

class _ActionsContainer:
    description = ... # type: Any
    argument_default = ... # type: Any
    prefix_chars = ... # type: Any
    conflict_handler = ... # type: Any
    def __init__(self, description, prefix_chars, argument_default, conflict_handler): pass
    def register(self, registry_name, value, object): pass
    def set_defaults(self, **kwargs): pass
    def get_default(self, dest): pass
    def add_argument(
        *args: str,
        action: str = None,
        nargs: str = None,
        default: Any = None,
        type: Any = None,
        choices: Any = None, # TODO: Container?
        required: bool = None,
        help: str = None,
        metavar: str = None,
        dest: str = None,
    ) -> None: pass
    def add_argument_group(self, *args, **kwargs): pass
    def add_mutually_exclusive_group(self, **kwargs): pass

class _ArgumentGroup(_ActionsContainer):
    title = ... # type: Any
    def __init__(self, container, title=None, description=None, **kwargs): pass

class _MutuallyExclusiveGroup(_ArgumentGroup):
    required = ... # type: Any
    def __init__(self, container, required=False): pass

class ArgumentParser(_AttributeHolder, _ActionsContainer):
    prog = ... # type: Any
    usage = ... # type: Any
    epilog = ... # type: Any
    formatter_class = ... # type: Any
    fromfile_prefix_chars = ... # type: Any
    add_help = ... # type: Any
    def __init__(self, prog=None, usage=None, description=None, epilog=None, parents=...,
                 formatter_class=..., prefix_chars='', fromfile_prefix_chars=None,
                 argument_default=None, conflict_handler='', add_help=True): pass
    def add_subparsers(self, **kwargs): pass
    def parse_args(self, args: Sequence[str] = None, namespace=None) -> Any: pass
    def parse_known_args(self, args=None, namespace=None): pass
    def convert_arg_line_to_args(self, arg_line): pass
    def format_usage(self): pass
    def format_help(self): pass
    def print_usage(self, file=None): pass
    def print_help(self, file=None): pass
    def exit(self, status=0, message=None): pass
    def error(self, message): pass
