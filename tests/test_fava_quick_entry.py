"""All fava-quick-entry tests in one file."""
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Iterator

import pytest
from fava.application import create_app
from flask import Flask
from flask.testing import FlaskClient

from fava_quick_entry import (
    WriteError,
    atomic_write,
    find_insertion_point,
    format_transaction,
    suggest_target,
    verify_ledger,
    write_transaction,
)


FIXTURES_SRC = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_ledger(tmp_path: Path) -> Path:
    dst = tmp_path / "ledger"
    shutil.copytree(FIXTURES_SRC, dst)
    return dst


# ─── format_transaction ────────────────────────────────────────────────────

def test_format_basic_transaction() -> None:
    out = format_transaction({
        "date": "2024-04-15", "flag": "*", "payee": "Starbucks", "narration": "",
        "postings": [
            {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
            {"account": "Liabilities:CreditCard:Chase", "amount": "-5.50", "currency": "USD"},
        ],
    })
    assert '2024-04-15 * "Starbucks" ""' in out
    assert "5.50 USD" in out
    assert "-5.50 USD" in out


def test_format_omits_payee_when_empty() -> None:
    out = format_transaction({
        "date": "2024-04-15", "flag": "*", "payee": "", "narration": "lunch",
        "postings": [
            {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
            {"account": "Liabilities:CreditCard:Chase", "amount": "-5.50", "currency": "USD"},
        ],
    })
    assert out.splitlines()[0] == '2024-04-15 * "lunch"'


def test_format_posting_without_amount_for_autobalance() -> None:
    out = format_transaction({
        "date": "2024-04-15", "flag": "*", "payee": "Starbucks", "narration": "",
        "postings": [
            {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
            {"account": "Liabilities:CreditCard:Chase", "amount": "", "currency": "USD"},
        ],
    })
    assert any(line.strip() == "Liabilities:CreditCard:Chase" for line in out.splitlines())


# ─── find_insertion_point ──────────────────────────────────────────────────

def test_insertion_point_empty_file() -> None:
    assert find_insertion_point("", date(2024, 4, 15)) == 0


def test_insertion_point_appends_after_earlier_dates() -> None:
    text = (
        '2024-04-10 * "A" ""\n'
        '  Expenses:X  1 USD\n'
        '  Assets:Cash -1 USD\n'
        '\n'
        '2024-04-12 * "B" ""\n'
        '  Expenses:X  2 USD\n'
        '  Assets:Cash -2 USD\n'
    )
    idx = find_insertion_point(text, date(2024, 4, 15))
    assert "2024-04-12" not in "\n".join(text.splitlines()[idx:])


def test_insertion_point_before_later_dates() -> None:
    text = (
        '2024-04-20 * "C" ""\n'
        '  Expenses:X  1 USD\n'
        '  Assets:Cash -1 USD\n'
    )
    assert find_insertion_point(text, date(2024, 4, 15)) == 0


# ─── atomic_write ──────────────────────────────────────────────────────────

def test_atomic_write_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "out.beancount"
    atomic_write(str(target), "hello\n")
    assert target.read_text() == "hello\n"


def test_atomic_write_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "out.beancount"
    target.write_text("old\n")
    atomic_write(str(target), "new\n")
    assert target.read_text() == "new\n"


# ─── write_transaction (real ledger) ───────────────────────────────────────

def test_write_balanced_transaction_succeeds(fixture_ledger: Path) -> None:
    main = fixture_ledger / "main.beancount"
    target = fixture_ledger / "2024" / "04.beancount"
    written = write_transaction(str(main), str(target), {
        "date": "2024-04-15", "flag": "*", "payee": "Starbucks", "narration": "",
        "postings": [
            {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
            {"account": "Liabilities:CreditCard:Chase", "amount": "-5.50", "currency": "USD"},
        ],
    })
    assert "Starbucks" in written
    assert "Starbucks" in target.read_text()
    ok, errors = verify_ledger(str(main))
    assert ok, f"verify failed: {errors}"


def test_write_unbalanced_transaction_rolls_back(fixture_ledger: Path) -> None:
    main = fixture_ledger / "main.beancount"
    target = fixture_ledger / "2024" / "04.beancount"
    original = target.read_text()
    with pytest.raises(WriteError):
        write_transaction(str(main), str(target), {
            "date": "2024-04-15", "flag": "*", "payee": "Bad", "narration": "",
            "postings": [
                {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
                {"account": "Liabilities:CreditCard:Chase", "amount": "-3.00", "currency": "USD"},
            ],
        })
    assert target.read_text() == original


def test_write_with_unopened_account_rolls_back(fixture_ledger: Path) -> None:
    main = fixture_ledger / "main.beancount"
    target = fixture_ledger / "2024" / "04.beancount"
    original = target.read_text()
    with pytest.raises(WriteError):
        write_transaction(str(main), str(target), {
            "date": "2024-04-15", "flag": "*", "payee": "Bad", "narration": "",
            "postings": [
                {"account": "Expenses:NotOpened", "amount": "5.50", "currency": "USD"},
                {"account": "Liabilities:CreditCard:Chase", "amount": "-5.50", "currency": "USD"},
            ],
        })
    assert target.read_text() == original


# ─── routing ───────────────────────────────────────────────────────────────

def test_routing_no_template_returns_default() -> None:
    assert suggest_target(None, date(2024, 4, 15), "main.beancount") == "main.beancount"


def test_routing_simple_template() -> None:
    assert suggest_target("{year}/{month:02d}.beancount", date(2024, 4, 15), "main.beancount") == "2024/04.beancount"


def test_routing_template_with_day() -> None:
    assert (
        suggest_target("daily/{year}-{month:02d}-{day:02d}.beancount", date(2024, 4, 5), "main.beancount")
        == "daily/2024-04-05.beancount"
    )


def test_routing_template_with_month_abbr() -> None:
    assert (
        suggest_target("records/journal/{year}/{month:02d}-{month_abbr}.bean", date(2026, 4, 5), "main.beancount")
        == "records/journal/2026/04-Apr.bean"
    )


def test_routing_template_with_month_name() -> None:
    assert (
        suggest_target("{year}/{month_name}.bean", date(2026, 4, 5), "main.beancount")
        == "2026/April.bean"
    )


def test_routing_invalid_template_falls_back() -> None:
    assert suggest_target("{nonexistent}.beancount", date(2024, 4, 15), "main.beancount") == "main.beancount"


# ─── HTTP API (Flask test client) ──────────────────────────────────────────

@pytest.fixture
def fava_app(tmp_path: Path) -> tuple[Flask, str, Path]:
    dst = tmp_path / "ledger"
    shutil.copytree(FIXTURES_SRC, dst)
    main = dst / "main.beancount"
    app = create_app([main])
    app.config["TESTING"] = True
    return app, app.config["LEDGERS"].first_slug(), dst


@pytest.fixture
def client(fava_app: tuple[Flask, str, Path]) -> Iterator[FlaskClient]:
    with fava_app[0].test_client() as c:
        yield c


@pytest.fixture
def slug(fava_app: tuple[Flask, str, Path]) -> str:
    return fava_app[1]


@pytest.fixture
def ledger_dir(fava_app: tuple[Flask, str, Path]) -> Path:
    return fava_app[2]


def url(slug: str, endpoint: str) -> str:
    return f"/{slug}/extension/FavaQuickEntry/{endpoint}"


def test_api_preview_balanced(client: FlaskClient, slug: str) -> None:
    r = client.post(url(slug, "preview"), json={
        "date": "2024-04-15", "flag": "*", "payee": "Starbucks", "narration": "",
        "postings": [
            {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
            {"account": "Liabilities:CreditCard:Chase", "amount": "-5.50", "currency": "USD"},
        ],
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert '2024-04-15 * "Starbucks" ""' in data["text"]


def test_api_preview_invalid_payload(client: FlaskClient, slug: str) -> None:
    r = client.post(url(slug, "preview"), json={"flag": "*"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is False
    assert "error" in data


def test_api_save_balanced_writes_file(client: FlaskClient, slug: str, ledger_dir: Path) -> None:
    target = ledger_dir / "2024" / "04.beancount"
    before = target.read_text()
    r = client.post(url(slug, "save"), json={
        "transaction": {
            "date": "2024-04-15", "flag": "*", "payee": "Starbucks", "narration": "",
            "postings": [
                {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
                {"account": "Liabilities:CreditCard:Chase", "amount": "-5.50", "currency": "USD"},
            ],
        },
        "target_file": "2024/04.beancount",
    })
    assert r.status_code == 200
    assert r.get_json()["ok"] is True
    after = target.read_text()
    assert "Starbucks" in after
    assert after != before


def test_api_save_unbalanced_rolls_back(client: FlaskClient, slug: str, ledger_dir: Path) -> None:
    target = ledger_dir / "2024" / "04.beancount"
    before = target.read_text()
    r = client.post(url(slug, "save"), json={
        "transaction": {
            "date": "2024-04-15", "flag": "*", "payee": "Bad", "narration": "",
            "postings": [
                {"account": "Expenses:Food:Coffee", "amount": "5.50", "currency": "USD"},
                {"account": "Liabilities:CreditCard:Chase", "amount": "-3.00", "currency": "USD"},
            ],
        },
        "target_file": "2024/04.beancount",
    })
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is False
    assert "bean-check failed" in data["error"]
    assert target.read_text() == before


def test_api_save_path_traversal(client: FlaskClient, slug: str) -> None:
    r = client.post(url(slug, "save"), json={
        "transaction": {"date": "2024-04-15", "flag": "*", "payee": "x", "narration": "", "postings": []},
        "target_file": "../etc/passwd",
    })
    assert r.status_code == 400
    assert "invalid target path" in r.get_json()["error"]


def test_api_files_lists(client: FlaskClient, slug: str) -> None:
    r = client.get(url(slug, "files"))
    assert r.status_code == 200
    data = r.get_json()
    files = set(data["files"])
    assert {"main.beancount", "2024/04.beancount"}.issubset(files)
    assert data["default"] == "main.beancount"


def test_api_files_create_valid(client: FlaskClient, slug: str, ledger_dir: Path) -> None:
    rel = "2024/05.beancount"
    r = client.post(url(slug, "files_create"), json={"path": rel})
    assert r.status_code == 200
    assert r.get_json()["ok"] is True
    assert (ledger_dir / rel).exists()
    assert f'include "{rel}"' in (ledger_dir / "main.beancount").read_text()


def test_api_files_create_traversal(client: FlaskClient, slug: str) -> None:
    r = client.post(url(slug, "files_create"), json={"path": "../escape.beancount"})
    assert r.status_code == 400
    assert "escapes" in r.get_json()["error"]


def test_api_files_create_bad_extension(client: FlaskClient, slug: str) -> None:
    r = client.post(url(slug, "files_create"), json={"path": "2024/05.txt"})
    assert r.status_code == 400
    assert ".beancount" in r.get_json()["error"]


def test_api_files_create_existing(client: FlaskClient, slug: str) -> None:
    r = client.post(url(slug, "files_create"), json={"path": "2024/04.beancount"})
    assert r.status_code == 400
    assert "exists" in r.get_json()["error"]


def test_api_accounts(client: FlaskClient, slug: str) -> None:
    r = client.get(url(slug, "accounts"))
    assert r.status_code == 200
    accounts = r.get_json()["accounts"]
    assert {"Assets:Cash", "Expenses:Food:Coffee", "Liabilities:CreditCard:Chase"}.issubset(accounts)
    assert accounts == sorted(accounts)


def test_api_payees(client: FlaskClient, slug: str) -> None:
    r = client.get(url(slug, "payees"))
    assert r.status_code == 200
    payees = r.get_json()["payees"]
    names = {p["name"] for p in payees}
    assert {"Whole Foods", "Uber"}.issubset(names)
    for p in payees:
        assert p["count"] >= 1
        assert p["last_used"]


def test_api_suggest_target(client: FlaskClient, slug: str) -> None:
    r = client.get(url(slug, "suggest_target"), query_string={"date": "2024-04-15"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert data["target_file"] == "2024/04.beancount"


def test_api_suggest_target_no_date(client: FlaskClient, slug: str) -> None:
    assert client.get(url(slug, "suggest_target")).status_code == 400


def test_api_suggest_target_invalid_date(client: FlaskClient, slug: str) -> None:
    assert client.get(url(slug, "suggest_target"), query_string={"date": "not-a-date"}).status_code == 400
