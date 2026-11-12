from html_dsl import render, tag


def main() -> None:
    title = "DSL pentru generarea HTML"
    item = tag("li")({"class": "feature"})

    page = tag("html")({"lang": "ro"})([
        tag("head")({})([
            tag("meta")({"charset": "utf-8"})([]),
            tag("title")({})([title]),
        ]),
        tag("body")({})([
            tag("h1")({})([title]),
            tag("p")({})([
                "Exemplu pentru ",
                tag("strong")({})(["biletul nr. 19"]),
                ". Text cu caractere speciale: 2 < 3 & 4 > 1.",
            ]),
            tag("ul")({})([
                item(["Currying"]),
                item(["Aplicarea parțială a funcțiilor"]),
            ]),
        ]),
    ])

    print("<!doctype html>")
    print(render(page))


if __name__ == "__main__":
    main()
