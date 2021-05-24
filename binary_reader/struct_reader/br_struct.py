from typing import Any, Dict


class NameMeta(type):
    def __init__(self, name, bases, attrs):
        super(NameMeta, self).__init__(name, bases, attrs)
        self.class_name = name


class BrStruct(metaclass=NameMeta):
    def __init__(self):
        self.attr_props = BrStruct.get_attr_props(self.class_name)
        print(self.attr_props)

    __struct_attr_props: Dict[str, Dict[str, Any]] = dict()

    @classmethod
    def get_attr_props(cls, name) -> Dict[str, Dict[str, Any]]:
        return cls.__struct_attr_props.get(name, dict())

    @classmethod
    def update_attr_props(cls, name, attr_props):
        if not cls.__struct_attr_props.get(name, None):
            cls.__struct_attr_props[name] = dict()

        cls.__struct_attr_props[name].update(attr_props)

    attr_props: Dict[str, Dict[str, Any]]
