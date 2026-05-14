from datetime import datetime

from openf1.openf1_payload import JSONValue


def to_str(json: JSONValue) -> str:
    if json is None:
        raise ValueError(f"cannot be None: {json}")
    return str(json)


def to_datetime(json: JSONValue) -> datetime:
    if json is None:
        raise ValueError(f"cannot be None: {json}")
    return datetime.fromisoformat(str(json))


def to_optional_datetime(json: JSONValue) -> datetime | None:
    if json is None:
        return None
    return datetime.fromisoformat(str(json))


def to_int(json: JSONValue) -> int:
    if json is None:
        raise ValueError(f"cannot be None: {json}")
    return int(json)


def to_optional_int(json: JSONValue) -> int | None:
    if json is None:
        return None
    return int(json)


def to_float(json: JSONValue) -> float:
    if json is None:
        raise ValueError(f"cannot be None: {json}")
    return float(json)


def to_optional_float(json: JSONValue) -> float | None:
    if json is None:
        return None
    return float(json)
