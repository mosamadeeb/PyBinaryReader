from .br_struct import BrStruct, BrStructManager


def __decorator_factory(decorator_func):
    def arg_decorator(*decorator_args):
        def inner(actual_func):
            class_name = actual_func.__qualname__.split('.')[0]

            props = decorator_func(actual_func)
            attr_props = BrStructManager.get_attr_props(class_name)

            for a in decorator_args:
                if type(a) is tuple and len(a) == 2:
                    a, b = a
                    props['other'] = b
                if not attr_props.get(a, None):
                    attr_props[a] = dict()

                attr_props[a].update(props)

            BrStructManager.update_attr_props(class_name, attr_props)

            def wrapper(self: BrStruct, *args, **kwargs):
                return actual_func(self, *args, **kwargs)

            return wrapper
        return inner
    return arg_decorator


@__decorator_factory
def is_offset(*args):
    """[Write] tuple
    is offset"""
    props = dict()
    props['is_offset'] = True
    props['is_offset_func'] = args[0]
    return props


@__decorator_factory
def offset_of(*args):
    """[Read]
    offset of variable"""
    props = dict()
    props['has_offset'] = True
    props['offset_func'] = args[0]
    return props


@__decorator_factory
def type_of(*args):
    """[Read/Write]
    type of variable"""
    props = dict()
    props['has_type'] = True
    props['type_func'] = args[0]
    return props


@__decorator_factory
def count_of(*args):
    """[Read]
    count of iterable"""
    props = dict()
    props['has_count'] = True
    props['count_func'] = args[0]
    return props


@__decorator_factory
def length_of(*args):
    """[Read]
    length of string"""
    props = dict()
    props['str_length'] = args[0]
    return props

@__decorator_factory
def null(*args):
    """[Write]
    null terminated string"""
    props = dict()
    props['str_null'] = args[0]
    return props