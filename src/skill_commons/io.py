"""Strict-enough YAML and package input helpers for Phase 0."""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import rfc8785
import yaml
from yaml.constructor import ConstructorError

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
I_JSON_SAFE_INTEGER = (1 << 53) - 1
MAX_YAML_NESTING = 100


class StrictLoader(yaml.SafeLoader):
    """Safe loader that rejects aliases and duplicate mapping keys."""

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
    return load_yaml(path.read_bytes().decode("utf-8"))


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def load_json_file(path: Path) -> Any:
    return json.loads(
        path.read_bytes().decode("utf-8"),
        parse_constant=_reject_json_constant,
        object_pairs_hook=_strict_json_object,
    )


def dump_yaml(value: Any) -> str:
    return yaml.safe_dump(
        json_safe(value),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100,
    )


def parse_skill_text(text: str) -> tuple[dict[str, Any], str, str]:
    """Parse one already-decoded SKILL.md without normalizing its body."""

    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("SKILL.md has no complete leading YAML frontmatter block")
    frontmatter = load_yaml(match.group(1))
    if not isinstance(frontmatter, dict):
        raise ValueError("SKILL.md frontmatter is not a mapping")
    body = text[match.end() :]
    return frontmatter, body, text


def parse_skill(skill_dir: Path) -> tuple[dict[str, Any], str, str]:
    skill_md = skill_dir / "SKILL.md"
    return parse_skill_text(skill_md.read_bytes().decode("utf-8"))


def json_safe(value: Any, *, _path: str = "$") -> Any:
    """Return JSON-compatible data, rejecting lossy or non-finite YAML values."""

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


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    """Return RFC 8785 JSON Canonicalization Scheme bytes."""

    try:
        return rfc8785.dumps(json_safe(value))
    except (TypeError, ValueError, rfc8785.CanonicalizationError) as exc:
        raise ValueError("canonical input must use the finite JSON data model") from exc


def semantic_digest(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def safe_relative_path(path: Path, root: Path) -> str:
    resolved_root = root.resolve()
    resolved = path.resolve()
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"path escapes package root: {path}")
    return resolved.relative_to(resolved_root).as_posix()
