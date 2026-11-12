from __future__ import annotations

import re
from collections.abc import (
    Callable,
    Iterable,
    Mapping,
)
from dataclasses import dataclass
from functools import partial
from html import escape


VOID_ELEMENTS = frozenset(
    "area base br col embed hr img input link meta source track wbr".split()
)


@dataclass(frozen=True)
class Element:
    name: str
    attributes: tuple[tuple[str, str], ...]
    children: tuple[Child, ...]


Child = str | Element


def _create_element(
    name: str,
    attributes: tuple[tuple[str, str], ...],
    children: Iterable[Child],
) -> Element:
    children = tuple(children)
    if name.lower() in VOID_ELEMENTS and children:
        raise ValueError(f"<{name}> cannot have children")
    return Element(name, attributes, children)


def tag(
    name: str,
) -> Callable[[Mapping[str, str]], Callable[[Iterable[Child]], Element]]:
    """Build an element in three stages: tag(name)(attributes)(children)."""
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9-]*", name):
        raise ValueError(f"Invalid tag name: {name!r}")

    def with_attributes(
        attributes: Mapping[str, str],
    ) -> Callable[[Iterable[Child]], Element]:
        pairs = tuple(attributes.items())
        for key, _ in pairs:
            if not re.fullmatch(r"[a-zA-Z_:][a-zA-Z0-9_.:-]*", key):
                raise ValueError(f"Invalid attribute name: {key!r}")
        return partial(_create_element, name, pairs)

    return with_attributes


def render(node: Child) -> str:
    """Turn a tree of elements and text into HTML."""
    if isinstance(node, str):
        return escape(node, quote=False)

    attributes = "".join(
        f' {name}="{escape(value)}"' for name, value in node.attributes
    )
    opening = f"<{node.name}{attributes}>"
    if node.name.lower() in VOID_ELEMENTS:
        return opening

    contents = "".join(render(child) for child in node.children)
    return f"{opening}{contents}</{node.name}>"


def render_procedural(node: Child) -> str:
    if isinstance(node, str):
        return escape(node, quote=False)

    markup = f"<{node.name}"
    for name, value in node.attributes:
        markup = f'{markup} {name}="{escape(value)}"'
    markup = f"{markup}>"
    if node.name.lower() in VOID_ELEMENTS:
        return markup

    for child in node.children:
        child_html = render_procedural(child)
        markup = markup + child_html
    return f"{markup}</{node.name}>"


def main() -> None:
    title = "DSL pentru generarea HTML"
    charset = tag("meta")({"charset": "utf-8"})([])
    tab_title = tag("title")({})([title])
    head = tag("head")({})([charset, tab_title])

    heading = tag("h1")({})([title])
    ticket = tag("strong")({})(["biletul nr. 19"])
    intro = tag("p")({})([
        "Exemplu pentru ",
        ticket,
        ". Text cu caractere speciale: 2 < 3 & 4 > 1.",
    ])

    item = tag("li")({"class": "feature"})
    topics = tag("ul")({})([
        item(["Currying"]),
        item(["Aplicarea parțială a funcțiilor"]),
    ])
    body = tag("body")({})([heading, intro, topics])
    page = tag("html")({"lang": "ro"})([head, body])

    html = render_procedural(page)
    print("<!doctype html>")
    print(html)


if __name__ == "__main__":
    main()
