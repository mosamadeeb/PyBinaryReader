from .br_struct import BrStruct


def __decorator_factory(decorator_func):
    def arg_decorator(*decorator_args):
        def inner(actual_func):
            class_name = actual_func.__qualname__.split('.')[0]

            props = decorator_func(actual_func)
            attr_props = BrStruct.get_attr_props(class_name)

            for a in decorator_args:
                if not attr_props.get(a, None):
                    attr_props[a] = dict()

                attr_props[a].update(props)

            BrStruct.update_attr_props(class_name, attr_props)

            def wrapper(self: BrStruct, *args, **kwargs):
                return actual_func(self, *args, **kwargs)

            return wrapper
        return inner
    return arg_decorator


@__decorator_factory
def count_of(*args):
    """count of iterable"""
    props = dict()
    props['has_count'] = True
    props['count_func'] = args[0]
    return props


@__decorator_factory
def length_of(*args):
    """length of string"""
    props = dict()
    props['str_length'] = args[0]
    return props
