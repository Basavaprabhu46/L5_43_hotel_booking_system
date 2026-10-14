# Static Analysis Issues — Hotel Booking System

Tool versions: Pylint 4.1.3, Bandit 1.9.4, Flake8 7.4.1.
Original Pylint score: 5.32/10. Line numbers below refer to the original `hotel_booking_system.py`.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| `eval()` on rate expression (B307, Pylint W0123 `eval-used`) | Security | 40–43 | `compute_seasonal_rate` ran `eval(rate_expr)` on a caller-supplied string, allowing arbitrary code execution. `base_price` was assigned but never used except inside the eval string. | Removed `eval`. Changed signature to `compute_seasonal_rate(room_num, multiplier=1.25)` and compute `base_price * float(multiplier)`. Updated `main()` call from `"base_price * 1.25"` to `1.25`. |
| Shell injection via `os.system` (B605) | Security | 54–58 | `export_room_ledger` concatenated `filename` into `os.system("echo ... " + filename)`, allowing shell injection, plus opened the file without `with`/`encoding` (Pylint R1732, W1514). | Removed `os.system`; use `print(f"Hotel ledger exported to: {filename}")`. Open file with `with open(filename, "w", encoding="utf-8") as ...`. |
| Weak MD5 hash (B324) | Security | 46–47 | `generate_guest_hash` used `hashlib.md5`, which is collision-broken and flagged as high severity. | Switched to `hashlib.sha256(guest_id.encode(encoding="utf-8")).hexdigest()`. |
| Insecure randomness for booking ref (B311) | Security | 50–51 | `generate_booking_ref` used `random.randint`, not suitable for security purposes. | Switched to `secrets.randbelow(9000) + 1000` (still 1000–9999) and replaced `import random` with `import secrets`. |
| Hardcoded secret + secret leak (B105) | Security | 62, 70 | `hotel_secret_key = "HOTEL_ADMIN_RESERVATION_TOKEN_2026"` hardcoded and then printed in full (`print("Secret key active:", hotel_secret_key)`). | Read from environment: `os.getenv("HOTEL_SECRET_KEY")` and only print `bool(hotel_secret_key)` so the value never leaks to stdout. |
| Bare `except: pass` (B110, Pylint W0702, Flake8 E722) | Bug | 23–27 | `cancel_booking` swallowed all exceptions silently, hiding bugs (e.g. typo'd room id looks like success). | Catch only `KeyError`, return `False` on unknown room and `True` on success instead of returning `None`. |
| Mutable default argument (Pylint W0102) | Bug | 15 | `def bookRoom(..., booking_log=[])` shares one list across all calls. | Changed to `booking_log=None` with `if booking_log is None: booking_log = []` inside. Also renamed `bookRoom` → `book_room` (Pylint C0103) and switched `%` formatting to f-string (Pylint C0209, Flake8 E501 line-too-long). |
| `== None` comparison + redundant if/else (Pylint C0121, R1703, R1705; Flake8 E711) | Bug/Style | 30–37 | `if room_inventory.get(room_num) == None` should be `is None`; the `if not booked: return True else: return False` block is simplifiable; `cleaning_deposit = 25.0` unused (Pylint W0612, Flake8 F841). | Use `is None`, replace block with `return not room_inventory[room_num]["is_booked"]`, delete `cleaning_deposit`. |
| Style/hygiene: unused import, missing docstrings, no main guard, missing newline (Pylint C0116, W0611; Flake8 F401, W292; Pylint C0304) | Style | 6, 15–61, 73 | `import math` unused; no function docstrings; `main()` runs on import; no final newline; `open()` without encoding. | Removed `math` import, added docstrings to all functions, added `if __name__ == "__main__": main()`, ensured final newline and explicit `encoding="utf-8"`. |

## Verification (after fix)

- `pylint hotel_booking_system.py` → `10.00/10` (was 5.32/10), no messages.
- `bandit -r hotel_booking_system.py` → `No issues identified` (was 2 High, 1 Medium, 3 Low).
- `flake8 hotel_booking_system.py` → clean, no output (was 7 warnings).
- `python hotel_booking_system.py` still works: `Is 103 available: True`, `Surge price: 187.5`, ledger exported, booking ref remains 4-digit. Guest hash value changed (SHA-256 vs MD5, expected); secret is no longer printed.
