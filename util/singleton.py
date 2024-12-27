from typing import Any, Dict, Tuple, Type


class SingletonMeta(type):
    _instances: Dict[Type[Any], object] = {}

    def __call__(cls, *args: Tuple[Any], **kwargs: Dict[str, Any]) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
