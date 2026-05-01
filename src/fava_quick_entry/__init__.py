"""fava-quick-entry — Fava extension for quick Beancount transaction entry."""
from __future__ import annotations

import os
import tempfile
from collections import Counter
from datetime import date as _date
from typing import Any, Iterable

from beancount import loader
from beancount.core.data import Custom, Transaction
from fava.ext import FavaExtensionBase, extension_endpoint
from flask import jsonify, request


# ─── writer ─────────────────────────────────────────────────────────────────

class WriteError(Exception):
    """Raised when a write fails verification and is rolled back."""


ACCOUNT_COLUMN = 50
AMOUNT_COLUMN = 14


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def format_transaction(tx_data: dict[str, Any]) -> str:
    """Format a transaction dict to Beancount text.

    A posting with empty/None amount is allowed; Beancount auto-balances.
    """
    date = tx_data["date"]
    flag = tx_data.get("flag", "*")
    payee = tx_data.get("payee", "")
    narration = tx_data.get("narration", "")

    if payee:
        lines = [f'{date} {flag} "{_escape(payee)}" "{_escape(narration)}"']
    else:
        lines = [f'{date} {flag} "{_escape(narration)}"']

    for p in tx_data.get("postings", []):
        account = (p.get("account") or "").strip()
        if not account:
            continue
        amount = p.get("amount")
        if amount is None or str(amount).strip() == "":
            lines.append(f"  {account}")
        else:
            currency = (p.get("currency") or "").strip()
            amt_str = f"{amount} {currency}".strip()
            padded = f"  {account}".ljust(ACCOUNT_COLUMN)
            lines.append(f"{padded}{amt_str.rjust(AMOUNT_COLUMN)}")

    return "\n".join(lines)


def find_insertion_point(file_text: str, tx_date: _date) -> int:
    """Line index where a tx with `tx_date` should be inserted: after the
    last block dated <= tx_date, or at end-of-file if none matches."""
    lines = file_text.splitlines()
    last_match_block_end = -1
    first_dated_line = -1

    for i, line in enumerate(lines):
        if len(line) >= 10 and line[0:4].isdigit() and line[4] == "-" and line[7] == "-":
            try:
                line_date = _date.fromisoformat(line[0:10])
            except ValueError:
                continue
            if first_dated_line == -1:
                first_dated_line = i
            if line_date <= tx_date:
                j = i + 1
                while j < len(lines) and (
                    lines[j].startswith(" ")
                    or lines[j].startswith("\t")
                    or lines[j].strip() == ""
                ):
                    j += 1
                last_match_block_end = j

    if last_match_block_end != -1:
        return last_match_block_end
    if first_dated_line != -1:
        return first_dated_line
    return len(lines)


def atomic_write(file_path: str, content: str) -> None:
    dir_ = os.path.dirname(os.path.abspath(file_path)) or "."
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=".qe-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, file_path)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass
        raise


def verify_ledger(main_file: str) -> tuple[bool, list[Any]]:
    _, errors, _ = loader.load_file(main_file)
    return (len(errors) == 0, errors)


def write_transaction(
    main_file: str,
    target_file: str,
    tx_data: dict[str, Any],
    raw_text: str | None = None,
) -> str:
    """Format → insert → atomic write → verify → rollback on failure.

    If `raw_text` is given, write it verbatim instead of formatting `tx_data`.
    `tx_data["date"]` is still used to find the insertion point.
    """
    tx_text = raw_text if raw_text is not None else format_transaction(tx_data)
    tx_date = _date.fromisoformat(tx_data["date"])

    if os.path.exists(target_file):
        with open(target_file, "r") as f:
            original = f.read()
    else:
        original = ""

    insertion = find_insertion_point(original, tx_date)
    lines = original.splitlines()
    block_lines = ["", *tx_text.splitlines(), ""]
    new_content = "\n".join(lines[:insertion] + block_lines + lines[insertion:])
    if not new_content.endswith("\n"):
        new_content += "\n"

    atomic_write(target_file, new_content)

    ok, errors = verify_ledger(main_file)
    if not ok:
        atomic_write(target_file, original)
        msgs = [str(e.message if hasattr(e, "message") else e) for e in errors]
        raise WriteError("bean-check failed: " + "; ".join(msgs[:5]))

    return tx_text


# ─── routing ────────────────────────────────────────────────────────────────

def parse_qe_target_template(entries: Iterable[Any]) -> str | None:
    """Read the `qe-target default` template string, if any."""
    for e in entries:
        if not isinstance(e, Custom) or e.type != "qe-target":
            continue
        try:
            if e.values[0].value == "default":
                return e.values[1].value
        except IndexError:
            continue
    return None


def suggest_target(template: str | None, tx_date: _date, default_main: str) -> str:
    """Substitute date placeholders into `template`.

    Supported placeholders:
      {year}, {month}, {month:02d}, {day}, {day:02d}
      {month_name}  → e.g. "April"
      {month_abbr}  → e.g. "Apr"
      {day_name}    → e.g. "Tuesday"
      {day_abbr}    → e.g. "Tue"
    """
    if not template:
        return default_main
    try:
        return template.format(
            year=tx_date.year,
            month=tx_date.month,
            day=tx_date.day,
            month_name=tx_date.strftime("%B"),
            month_abbr=tx_date.strftime("%b"),
            day_name=tx_date.strftime("%A"),
            day_abbr=tx_date.strftime("%a"),
        )
    except (KeyError, ValueError):
        return default_main


# ─── extension ──────────────────────────────────────────────────────────────

def _is_within(child: str, parent: str) -> bool:
    """True iff `child` resolves to a path inside `parent`. Defeats `..` traversal."""
    parent_real = os.path.realpath(parent)
    child_real = os.path.realpath(child)
    try:
        return os.path.commonpath([child_real, parent_real]) == parent_real
    except ValueError:
        return False


class FavaQuickEntry(FavaExtensionBase):
    """Quick transaction entry page for Fava with live Beancount preview."""

    report_title = "Quick Entry"
    has_js_module = True

    @extension_endpoint("preview", methods=["POST"])
    def api_preview(self) -> Any:
        try:
            text = format_transaction(request.get_json(force=True))
            return jsonify({"ok": True, "text": text})
        except Exception as e:
            return jsonify({"ok": False, "text": "", "error": str(e)})

    @extension_endpoint("save", methods=["POST"])
    def api_save(self) -> Any:
        try:
            body = request.get_json(force=True)
            main = self.ledger.beancount_file_path
            ledger_dir = os.path.dirname(main)
            target = os.path.join(ledger_dir, body["target_file"])

            if not _is_within(target, ledger_dir):
                return jsonify({"ok": False, "error": "invalid target path"}), 400

            raw_text = body.get("raw_text")
            written = write_transaction(main, target, body["transaction"], raw_text=raw_text)

            try:
                self.ledger.changed()
            except Exception:
                pass

            return jsonify({"ok": True, "text": written})
        except WriteError as e:
            return jsonify({"ok": False, "error": str(e)})
        except Exception as e:
            return jsonify({"ok": False, "error": f"unexpected error: {e}"}), 500

    @extension_endpoint("files", methods=["GET"])
    def api_files(self) -> Any:
        main = self.ledger.beancount_file_path
        ledger_dir = os.path.dirname(main)
        files: list[str] = []
        for root, _, names in os.walk(ledger_dir):
            for name in names:
                if name.endswith(".beancount") or name.endswith(".bean"):
                    files.append(os.path.relpath(os.path.join(root, name), ledger_dir))
        files.sort()
        return jsonify({"files": files, "default": os.path.basename(main)})

    @extension_endpoint("files_create", methods=["POST"])
    def api_files_create(self) -> Any:
        rel = (request.get_json(force=True).get("path") or "").strip()
        if not rel or not (rel.endswith(".beancount") or rel.endswith(".bean")):
            return jsonify({"ok": False, "error": "path must end in .beancount"}), 400

        main = self.ledger.beancount_file_path
        ledger_dir = os.path.dirname(main)
        full = os.path.join(ledger_dir, rel)

        if not _is_within(full, ledger_dir):
            return jsonify({"ok": False, "error": "path escapes ledger directory"}), 400
        if os.path.exists(full):
            return jsonify({"ok": False, "error": "file already exists"}), 400

        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write("")
        try:
            with open(main, "a") as f:
                f.write(f'\ninclude "{rel}"\n')
        except OSError:
            try:
                os.unlink(full)
            except OSError:
                pass
            raise

        return jsonify({"ok": True, "path": rel})

    @extension_endpoint("accounts", methods=["GET"])
    def api_accounts(self) -> Any:
        return jsonify({"accounts": sorted(self.ledger.attributes.accounts)})

    @extension_endpoint("payees", methods=["GET"])
    def api_payees(self) -> Any:
        counts: Counter[str] = Counter()
        last_used: dict[str, str] = {}
        for entry in self.ledger.all_entries:
            if isinstance(entry, Transaction) and entry.payee:
                counts[entry.payee] += 1
                d = entry.date.isoformat()
                if entry.payee not in last_used or last_used[entry.payee] < d:
                    last_used[entry.payee] = d
        items = [{"name": p, "count": counts[p], "last_used": last_used[p]} for p in counts]
        items.sort(key=lambda x: (x["last_used"], x["count"]), reverse=True)
        return jsonify({"payees": items[:200]})

    @extension_endpoint("suggest_target", methods=["GET"])
    def api_suggest_target(self) -> Any:
        date_str = request.args.get("date")
        if not date_str:
            return jsonify({"ok": False, "error": "missing date"}), 400
        try:
            tx_date = _date.fromisoformat(date_str)
        except ValueError:
            return jsonify({"ok": False, "error": "invalid date"}), 400

        template = parse_qe_target_template(self.ledger.all_entries)
        main_rel = os.path.basename(self.ledger.beancount_file_path)
        return jsonify({
            "ok": True,
            "target_file": suggest_target(template, tx_date, main_rel),
            "template_configured": template is not None,
        })
