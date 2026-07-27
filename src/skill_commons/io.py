"""Strict structured-data helpers for the federated registry."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError

I_JSON_SAFE_INTEGER = (1 << 53) - 1
MAX_YAML_NESTING = 100


class StrictLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects aliases, duplicate keys, and excessive nesting."""

    def compose_node(self, parent: Any, index: Any) -> Any:
        depth = getattr(self, "_skill_commons_depth", 0)
        if depth >= MAX_YAML_NESTING:
            event = self.peek_event()
            raise ConstructorError(
                None,
                None,
                f"YAML nesting exceeds the {MAX_YAML_NESTING}-level input limit",
                event.start_mark,
            )
        self._skill_commons_depth = depth + 1
        try:
            if self.check_event(yaml.AliasEvent):
                event = self.get_event()
                raise ConstructorError(
                    None,
                    None,
                    f"YAML aliases are not allowed: *{event.anchor}",
                    event.start_mark,
                )
            return super().compose_node(parent, index)
        finally:
            self._skill_commons_depth = depth


def _construct_mapping(
    loader: StrictLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key: {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_yaml(text: str) -> Any:
    return yaml.load(text, Loader=StrictLoader)


def load_yaml_file(path: Path) -> Any:
    return load_yaml(path.read_text(encoding="utf-8"))


def json_safe(value: Any, *, _path: str = "$") -> Any:
    """Return JSON-compatible data while rejecting lossy YAML values."""

    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        if abs(value) > I_JSON_SAFE_INTEGER:
            raise ValueError(f"integer is outside the I-JSON safe range at {_path}")
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite number is not valid JSON at {_path}")
        return value
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"JSON object key is not a string at {_path}: {key!r}")
            result[key] = json_safe(item, _path=f"{_path}.{key}")
        return result
    if isinstance(value, list):
        return [json_safe(item, _path=f"{_path}[{index}]") for index, item in enumerate(value)]
    raise ValueError(f"unsupported JSON value at {_path}: {type(value).__name__}")
