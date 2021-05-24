from typing import get_args, get_origin, get_type_hints

from .br_struct import BrStruct


def call_read_func(br: 'BinaryReader', cls: type) -> BrStruct:
    br_struct: BrStruct = cls()
    attr_props = br_struct.attr_props

    if not attr_props:
        br_struct.attr_props = dict()

    for attr, attr_type in get_type_hints(cls).items():
        if attr.startswith('_') or attr == 'attr_props':
            # Ignore protected/private attributes
            continue

        args = []
        props = attr_props.get(attr, dict())

        if props.get('has_offset', False):
            # Executes offset_func and passes offset_var to it
            br.seek(evaluate_func(props.get('offset_func', br.pos()), br_struct))

        if props.get('has_type', False):
            attr_type = evaluate_func(
                props.get('type_func', attr_type), br_struct)

        count = 1
        value_type = attr_type
        if get_origin(attr_type) is list or get_origin(attr_type) is tuple:
            if len(get_args(attr_type)) != 1 or get_origin(get_args(attr_type)[0]):
                raise Exception(
                    f'BinaryReader Error: generic type {attr_type} is expected to have exactly 1 non-generic argument.')

            count = 0
            if props.get('has_count', False):
                count = evaluate_func(
                    props.get('count_func', br.pos()), br_struct)

            value_type = get_args(attr_type)[0]
            type_name = value_type.__name__

            if issubclass(value_type, BrStruct):
                value_list = []

                for i in range(count):
                    value_list.append(call_read_func(br, attr_type))

                setattr(br_struct, attr, value_list)
                continue

            if type_name != 'str':
                args.append(count)

        elif get_origin(attr_type):
            raise Exception(
                f'BinaryReader Error: generic type {attr_type} is not supported by BinaryReader.')
        else:
            type_name = attr_type.__name__

        if issubclass(value_type, BrStruct):
            setattr(br_struct, attr, call_read_func(br, attr_type))
            continue

        read_func = getattr(br, f'read_{type_name}', None)
        if read_func is None:
            raise Exception(
                f'BinaryReader Error: type {attr_type} is not supported by BinaryReader.')

        if type_name == 'str':
            args.append(evaluate_func(props.get('str_length', 1), br_struct))
            args.append(evaluate_func(
                props.get('str_encoding', None), br_struct))

            if not isinstance(attr_type, str):
                # iterable
                value_list = list()

                for i in range(count):
                    value_list.append(read_func(*args))

                setattr(br_struct, attr, value_list)
                continue

        setattr(br_struct, attr, read_func(*args))

    return br_struct


def call_write_func(br: 'BinaryReader', br_struct: BrStruct):
    offsets = []
    attr_props = br_struct.attr_props

    if not attr_props:
        br_struct.attr_props = dict()

    for attr, attr_type in get_type_hints(br_struct).items():
        if attr.startswith('_'):
            # Ignore protected/private attributes
            continue

        args = []
        value = getattr(br_struct, attr)
        props = attr_props.get(attr, dict())

        props['offset'] = br.pos()

        if props.get('has_type', False):
            attr_type = evaluate_func(
                props.get('type_func', attr_type),
                br_struct)

        if props.get('is_offset_of', None):
            offsets.append((attr, attr_type))
            continue

        if value is None:
            value = 0

            if get_origin(attr_type):
                continue

            if attr_type is str:
                value = ''

        value_type = attr_type
        if get_origin(attr_type) is list or get_origin(attr_type) is tuple:
            if len(get_args(attr_type)) != 1 or get_origin(get_args(attr_type)[0]):
                raise Exception(
                    f'BinaryReader Error: generic type {attr_type} is expected to have exactly 1 non-generic argument.')

            if issubclass(get_args(attr_type)[0], BrStruct):
                for s in value:
                    call_write_func(br, s)
                continue

            value_type = get_args(attr_type)[0]
            type_name = value_type.__name__

            if type_name != 'str':
                args.append(True)

        elif get_origin(attr_type):
            raise Exception(
                f'BinaryReader Error: generic type {attr_type} is not supported by BinaryReader.')
        else:
            type_name = attr_type.__name__

        if issubclass(value_type, BrStruct):
            call_write_func(br, value if value else attr_type())
            continue

        write_func = getattr(br, f'write_{type_name}', None)
        if write_func is None:
            raise Exception(
                f'BinaryReader Error: type {attr_type} is not supported by BinaryReader.')

        if type_name == 'str':
            args.append(props.get('str_null', False))
            args.append(props.get('str_encoding', None))

            if not isinstance(value, str):
                # iterable
                for s in value:
                    write_func(value, *args)
                continue

        write_func(value, *args)

    for o, t in offsets:
        props = attr_props.get(o, dict())
        if props.get('offset', -1) != -1:
            br.seek(props['offset'])

            item = attr_props.get(props.get('is_offset_of', ''), dict())

            write_func = getattr(br, f'write_{t.__name__}', None)
            write_func(evaluate_func(
                props.get('offset_func', 0), 
                br_struct, 
                item.get('offset', 0) # calc offset from actual offset
            ))


def evaluate_func(func, br_struct, *args):
    if callable(func):
        return func(br_struct, *args)

    return func
