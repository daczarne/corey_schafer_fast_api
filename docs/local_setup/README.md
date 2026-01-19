# Setting up the local environment

This guide explains how to setup the basic local environment that comes with this repository. For more specialized use
cases, update and modify as needed.

## Creating a new environment with `uv`

The environment includes the following libraries:

- [`PyYAML`][pyyaml-repo]

And the following dev libraries:

- [`ruff`][ruff-repo]
- [`YAMLlint`][yamllint-repo]
- [`pytest`][pytest-repo]

To create a new environment using the `uv.lock` run the following commands:

```shell
uv sync --locked --all-extras --dev
```

Because of how `uv` works, just running `uv sync` will take care of creating a virtual env (if none exists) and
installing all dependencies in the environment, including the dev ones.

If you still want to activate the environment use:

```shell
source .venv/bin/activate
```

You can verify that the environment was correctly created by running:

```shell
$ uv tree
Resolved 7 packages in 4ms
python-projects v0.1.0
├── pyyaml v6.0.2
├── pytest v8.3.5 (group: dev)
│   ├── iniconfig v2.1.0
│   ├── packaging v25.0
│   └── pluggy v1.6.0
├── ruff v0.13.0 (group: dev)
└── yamllint v1.37.1 (group: dev)
    ├── pathspec v0.12.1
    └── pyyaml v6.0.2
```

The output of the `uv tree` command might look slightly different in the future, but the main packages should be there.

## Set the correct interpreter

Once the environment has been setup, make sure to update the path to the correct Python interpreter in
`.vscode/settings.json`.

```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
}
```

This will ensure that when VS Code is launched the correct environment will be automatically loaded.

## Running YAMLlint locally

To run YAMLlint locally use:

```shell
yamllint -c .yamllint.yaml .
```

## Running Markdown lint locally

To run Markdownlint locally use:

```shell
markdownlint-cli2 --config ".markdownlint.yaml" "**/*.md"
```

Beware of local, untracked files that may cause this to fail. If they are inside py-cached folders, these can usually
be removed safely.

**Reference documents**:

- [Markdown lint][markdown-lint-repo]
- [Markdown lint CLI][markdown-lint-cli-repo]
- [Markdown lint action][markdown-lint-action-repo]

## Running CSpell locally

To run CSpell locally use:

```shell
cspell lint --config ".cspell.json" --dot .
```

**Reference documents**:

- [CSpell][cspell-repo]
- [CSpell CLI][cspell-cli-repo]

## Running ruff locally

To run ruff locally use:

```shell
uv run ruff check --preview .
```

[cspell-cli-repo]: https://github.com/streetsidesoftware/cspell/tree/main/packages/cspell
[cspell-repo]: https://github.com/streetsidesoftware/cspell/tree/main
[markdown-lint-action-repo]: https://github.com/DavidAnson/markdownlint-cli2-action
[markdown-lint-cli-repo]: https://github.com/DavidAnson/markdownlint-cli2
[markdown-lint-repo]: https://github.com/DavidAnson/markdownlint
[pytest-repo]: https://github.com/pytest-dev/pytest
[pyyaml-repo]: https://github.com/yaml/pyyaml
[yamllint-repo]: https://github.com/adrienverge/yamllint
[ruff-repo]: https://github.com/astral-sh/ruff
