# Reflection — Lab 5: Static Code Analysis

Questions from `reflection_lab5.txt`.

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

Easiest were the mechanical style/correctness fixes Pylint and Flake8 flagged,
each a one-line change with no design decision:

- `import math` unused (F401/W0611): delete the line.
- `== None` → `is None` (E711/C0121), `%` formatting → f-string (C0209),
  bare `except:` → `except KeyError:` (E722/W0702), `with open(..., encoding="utf-8")`
  (R1732/W1514), deleting `cleaning_deposit`, adding docstrings and the final newline.
- Simplifying `if not booked: return True / else: return False` to
  `return not room_inventory[room_num]["is_booked"]` (R1703/R1705).

Hardest were the two High-severity Bandit findings because they required an API/behavior decision, not just syntax:

- `eval(rate_expr)` (B307/W0123): removing `eval` meant changing the function
  signature from `compute_seasonal_rate(room_num, rate_expr="base_price * 1.25")`
  to `compute_seasonal_rate(room_num, multiplier=1.25)` and updating the call in
  `main()`. Any caller passing the old expression string would break, so this was
  the only intentionally breaking change.
- `os.system("echo ..." + filename)` (B605): required deciding what the call was
  even for (just a status message) and replacing it with `print()`, plus choosing
  `with open()` semantics. The hardcoded secret (B105) was similarly judgment-based:
  moved to `os.getenv("HOTEL_SECRET_KEY")` and changed `print(secret)` to
  `print(bool(secret))` so the value never leaks.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

No true false positives — every flag I kept mapped to a genuine weakness, verified
by reading the flagged line. The closest candidates were the two Low-severity
Bandit findings, which look like overkill in a toy program but are valid on inspection:

- Example: B311 flags `random.randint(1000, 9999)` in `generate_booking_ref()`.
  One could argue a demo booking number needs no cryptographic randomness, so the
  flag feels like a false positive. I treated it as valid because booking references
  should be unpredictable, and the fix is trivial (`secrets.randbelow(9000) + 1000`,
  same 1000–9999 range). Same reasoning for B105 on the demo secret string: harmless
  here, but hardcoding + printing secrets is exactly the habit Bandit is meant to break.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Editor/IDE:** enable Pylint + Flake8 live (format-on-save, line length 79/100)
  so style and basic bug patterns are caught while typing.
- **Pre-commit hook:** run `flake8` and `bandit -r` on staged files; block commits
  on new High/Medium Bandit findings or Flake8 errors.
- **CI gate:** run all three on every pull request; fail the build if Pylint drops
  below an agreed threshold (e.g. 9.5/10 as in this lab), if Bandit reports any
  High/Medium issue, or if Flake8 reports anything. Store the reports as build
  artifacts, the same way this lab keeps `pylint_report.txt` / `bandit_report.txt` /
  `flake8_report.txt`.
- **Review process:** document accepted findings in an `issues.md`-style table
  (severity first) and require re-runs proving fixes, reserving human review for
  what tools miss (business logic, output correctness — e.g. Bandit flagged the
  hardcoded secret but not the `print(secret)` disclosure; only running the program
  caught that).

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

Measured, not subjective:

- **Pylint:** 5.32/10 → **10.00/10**, zero messages (was 22 messages).
- **Bandit:** 6 findings (2 High, 1 Medium, 3 Low) → **No issues identified**.
- **Flake8:** 7 warnings → **clean**.
- **Robustness:** arbitrary code execution via `eval` gone; shell injection via
  `os.system` gone; silent `except: pass` replaced with explicit `except KeyError`
  returning `False`; shared mutable default (`booking_log=[]`) fixed with `None`
  sentinel; weak MD5 → SHA-256; predictable `random` → `secrets`; secret no longer
  printed to stdout.
- **Readability:** `bookRoom` → `book_room`, f-strings, docstring on every function,
  `if __name__ == "__main__":` guard, `with open(..., encoding="utf-8")`.
- **Behavior preserved:** `python hotel_booking_system.py` still prints
  `Is 103 available: True` and `Surge price: 187.5` and exports the ledger; only
  intended output changes are the SHA-256 hash value (longer than MD5) and the
  secret line now showing `Secret key configured: False` instead of the raw token.
