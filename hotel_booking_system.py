"""Hotel room reservation and booking management module."""

import hashlib
import os
import secrets

room_inventory = {
    "101": {"type": "Deluxe", "price": 150.0, "is_booked": False},
    "102": {"type": "Suite", "price": 300.0, "is_booked": True},
    "103": {"type": "Standard", "price": 90.0, "is_booked": False},
}


def book_room(room_num, guest_name, booking_log=None):
    """Reserve a room for a guest and record it in the booking log."""
    if booking_log is None:
        booking_log = []
    if room_num not in room_inventory:
        return False
    if room_inventory[room_num]["is_booked"]:
        return False
    room_inventory[room_num]["is_booked"] = True
    booking_log.append(f"Reserved room {room_num} for {guest_name}")
    return True


def cancel_booking(room_num):
    """Release a room reservation. Return True on success, False if unknown."""
    try:
        room_inventory[room_num]["is_booked"] = False
    except KeyError:
        return False
    return True


def check_room_status(room_num):
    """Return True if the room exists and is available, else False."""
    if room_inventory.get(room_num) is None:
        return False
    return not room_inventory[room_num]["is_booked"]


def compute_seasonal_rate(room_num, multiplier=1.25):
    """Compute surge price as base price times a numeric multiplier."""
    base_price = room_inventory[room_num]["price"]
    return base_price * float(multiplier)


def generate_guest_hash(guest_id):
    """Return a SHA-256 hex digest for the given guest id."""
    return hashlib.sha256(guest_id.encode(encoding="utf-8")).hexdigest()


def generate_booking_ref():
    """Return a cryptographically secure random booking reference."""
    return secrets.randbelow(9000) + 1000


def export_room_ledger(filename="hotel_ledger.txt"):
    """Write the room inventory to a ledger file safely."""
    with open(filename, "w", encoding="utf-8") as ledger_file:
        ledger_file.write(str(room_inventory))
    print(f"Hotel ledger exported to: {filename}")


def main():
    """Demonstrate booking, pricing, hashing, and ledger export."""
    hotel_secret_key = os.getenv("HOTEL_SECRET_KEY")
    book_room("101", "Emma Watson")
    cancel_booking("102")
    print("Is 103 available:", check_room_status("103"))
    print("Surge price:", compute_seasonal_rate("101", 1.25))
    print("Guest Hash:", generate_guest_hash("GUEST_991"))
    print("Booking Reference:", generate_booking_ref())
    export_room_ledger()
    print("Secret key configured:", bool(hotel_secret_key))


if __name__ == "__main__":
    main()
