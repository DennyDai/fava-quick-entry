# fava-quick-entry

A Fava extension that adds a Quick Entry page with live Beancount text preview.

## Install

```bash
uv pip install git+https://github.com/DennyDai/fava-quick-entry.git
```

## Enable

Add this directive to your ledger:

```beancount
2010-01-01 custom "fava-extension" "fava_quick_entry"
```

Restart Fava. **Quick Entry** appears in the sidebar.

## Develop

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```
