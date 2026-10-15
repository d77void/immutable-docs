# d77void Immutable Docs

Community documentation of d77void Immutable:
how the system works and how to run and recover it yourself.

The pages are plain Markdown in [`src/`](src/), readable on GitHub, in any
editor or with `less`. [`src/SUMMARY.md`](src/SUMMARY.md) is the table of
contents and the only place where the order of the chapters is defined.

## Building the website

The website is generated with [mdBook](https://rust-lang.github.io/mdBook/),
with its default theme and no plugins. mdBook is only needed to build the
site; d77void Immutable itself does not need it.

```sh
mdbook build    # the site goes to book/
mdbook serve    # preview at http://localhost:3000, rebuilt on every change
```

A link in `SUMMARY.md` to a page that does not exist stops the build
(`create-missing = false` in `book.toml`).

## Rules for the content

- Everything is specific to d77void Immutable. General Void Linux topics are
  in the [Void Linux Handbook](https://docs.voidlinux.org/).
- Nothing is written from memory: commands, file names and behaviour are
  checked against the system's code and, where a page says so, on a real
  installation. What is not verified yet says so.
- The documentation shows commands; nothing here runs them.

## License

The documentation is licensed under
[Creative Commons Attribution-ShareAlike 4.0 International](LICENSE)
(CC BY-SA 4.0).
