import re

from sqlalchemy.orm import DeclarativeBase, declared_attr


def camel_to_snake(value: str) -> str:
    first_pass = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", first_pass).lower()


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)
