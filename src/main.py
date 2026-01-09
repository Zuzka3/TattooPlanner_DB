from getpass import getpass

from src.db.connection import load_config, get_connection
from src.dao.artist_dao import ArtistDAO
from src.dao.style_dao import StyleDAO
from src.dao.customer_dao import CustomerDAO
from src.dao.appointment_dao import AppointmentDAO
from src.dao.reports_dao import ReportsDAO
from src.services.appointment_service import AppointmentService
from src.services.import_service import ImportService
from src.services.exceptions import AppError
from src.ui.menu import ask, ask_optional, pause, print_table, ask_enum, ask_style_ids, ask_phone_optional
from src.services.validators import require_nonempty, validate_email, validate_positive_int, validate_float, parse_datetime


STATUS = ["PENDING", "CONFIRMED", "DONE", "CANCELLED"]
SIZE = ["S", "M", "L", "XL"]


def require_admin(auth_state: dict, config: dict) -> bool:
    """Ověří admina přes PIN v config.app.admin_pin. True=ok, False=zpět."""
    if auth_state.get("is_admin"):
        return True

    pin_required = str(config.get("app", {}).get("admin_pin", "123"))
    for _ in range(3):
        entered = getpass("Zadej admin PIN: ").strip()
        if entered == pin_required:
            auth_state["is_admin"] = True
            print("OK, admin přihlášen.")
            return True
        print("Špatný PIN.")
    print("Příliš mnoho pokusů.")
    return False


def main():
    try:
        config = load_config()
        cnxn = get_connection(config)
    except AppError as e:
        print(f"[CHYBA] {e}")
        return

    artists = ArtistDAO(cnxn)
    styles = StyleDAO(cnxn)
    customers = CustomerDAO(cnxn)
    appointments = AppointmentDAO(cnxn)
    reports = ReportsDAO(cnxn)
    appt_service = AppointmentService(cnxn)
    import_service = ImportService(cnxn)

    auth_state = {"is_admin": False}

    while True:
        print("\n=== Tattoo Planner ===")
        print("1) Zákazník: vytvořit rezervaci")
        print("2) Zákazník: moje rezervace podle e-mailu")

        if not auth_state["is_admin"]:
            print("9) Admin: přihlásit (PIN)")
        else:
            print("3) Admin: správa tatérů")
            print("4) Admin: reporty ")
            print("5) Admin: import ")
            print("6) Admin: správa rezervací")
            print("8) Admin: odhlásit")

        print("0) Konec")

        choice = ask("-> ")

        try:
            if choice == "1":
                create_reservation_flow(config, cnxn, artists, styles, appt_service)
            elif choice == "2":
                list_my_reservations_flow(appointments)

            elif choice == "9":
                require_admin(auth_state, config)

            elif choice == "8" and auth_state["is_admin"]:
                auth_state["is_admin"] = False
                print("Admin odhlášen.")

            elif choice in ("3", "4", "5", "6"):
                if not require_admin(auth_state, config):
                    continue

                if choice == "3":
                    admin_artists_flow(artists, styles)
                elif choice == "4":
                    reports_flow(reports)
                elif choice == "5":
                    import_flow(import_service)
                elif choice == "6":
                    admin_reservations_flow(appointments, styles, appt_service)

            elif choice == "0":
                print("Mějte se.")
                break
            else:
                print("Neplatná volba.")

        except AppError as e:
            print(f"[CHYBA] {e}")
            pause()


def create_reservation_flow(config, cnxn, artists: ArtistDAO, styles: StyleDAO, appt_service: AppointmentService):
    print("\n--- Vytvořit rezervaci ---")
    ar = artists.list_active()
    if not ar:
        print("Nejsou žádní aktivní tatéři. Importuj je nebo je přidej v adminu.")
        pause()
        return

    print("Tatéři:")
    for a in ar:
        print(f"  {a['artist_id']}: {a['name']} (specialty={a['specialty']})")

    artist_id = validate_positive_int(ask("Vyber artist_id: "), "artist_id")
    start_time = parse_datetime(ask("Start (YYYY-MM-DD HH:MM): "))

    duration = int(config.get("app", {}).get("default_duration_minutes", 90))
    custom_dur = ask_optional(f"Doba v minutách (Enter = default {duration}): ")
    if custom_dur:
        duration = validate_positive_int(custom_dur, "duration_minutes")

    status = ask_enum("Status", ["PENDING", "CONFIRMED"], default="PENDING")
    is_paid = ask_enum("Zaplaceno?", ["YES", "NO"], default="NO") == "YES"

    print("\nZákazník:")
    first = require_nonempty(ask("Jméno: "), "jméno")
    last = require_nonempty(ask("Příjmení: "), "příjmení")
    email = validate_email(ask("E-mail: "))
    phone = ask_phone_optional()

    print("\nDetail tetování:")
    size = ask_enum("Velikost", SIZE, default="M")
    color = require_nonempty(ask("Barva (např. black, color): "), "barva")
    notes = ask_optional("Poznámka (volitelné): ")
    price = validate_float(ask("Odhad ceny (float): "), "cena")

    style_rows = styles.list_all()
    chosen_style_ids = ask_style_ids(style_rows)

    appt_id = appt_service.create_reservation(
        customer_first=first,
        customer_last=last,
        customer_email=email,
        customer_phone=phone,
        artist_id=artist_id,
        start_time=start_time,
        duration_minutes=duration,
        status=status,
        is_paid=is_paid,
        tattoo_size=size,
        color=color,
        notes=notes,
        price_estimate=price,
        style_ids=chosen_style_ids,
    )
    print(f"OK! Vytvořena rezervace appointment_id={appt_id}")
    pause()


def list_my_reservations_flow(appointments: AppointmentDAO):
    print("\n--- Moje rezervace ---")
    email = validate_email(ask("Zadej e-mail: "))
    rows = appointments.list_for_customer_email(email)
    print_table(rows)
    pause()


def admin_artists_flow(artists: ArtistDAO, styles: StyleDAO):
    while True:
        print("\n--- Admin: Tatéři ---")
        print("1) Vypsat tatéry")
        print("2) Přidat tatéra")
        print("3) Upravit tatéra")
        print("4) Smazat tatéra")
        print("5) Nastavit styly tatéra")
        print("0) Zpět")

        c = ask("> ")
        if c == "0":
            return

        if c == "1":
            print_table(artists.list_all())
            pause()

        elif c == "2":
            name = require_nonempty(ask("Jméno: "), "jméno")
            spec = ask_optional("Specializace (volitelné): ")
            email = validate_email(ask("Kontakt e-mail: "))
            rate = validate_float(ask("Hodinovka (float): "), "hourly_rate")
            is_active = ask_enum("Aktivní?", ["YES", "NO"], default="YES") == "YES"
            new_id = int(artists.create(name, spec, email, rate, is_active))
            print(f"Vytvořen artist_id={new_id}")
            pause()

        elif c == "3":
            artist_id = validate_positive_int(ask("artist_id: "), "artist_id")
            a = artists.get(artist_id)
            if not a:
                print("Tatér neexistuje.")
                pause()
                continue

            name = require_nonempty(ask(f"Jméno [{a['name']}]: ") or a["name"], "jméno")
            spec = ask_optional(f"Specializace [{a['specialty'] or ''}]: ") or a["specialty"]
            email = validate_email(ask(f"Kontakt e-mail [{a['contact_email']}]: ") or a["contact_email"])
            rate = validate_float(ask(f"Hodinovka [{a['hourly_rate']}]: ") or a["hourly_rate"], "hourly_rate")
            is_active = ask_enum("Aktivní?", ["YES", "NO"], default=("YES" if a["is_active"] else "NO")) == "YES"

            artists.update(artist_id, name, spec, email, rate, is_active)
            print("Upraveno.")
            pause()

        elif c == "4":
            artist_id = validate_positive_int(ask("artist_id ke smazání: "), "artist_id")
            artists.delete(artist_id)
            artists.cnxn.commit()
            print("Smazáno.")
            pause()

        elif c == "5":
            artist_id = validate_positive_int(ask("artist_id: "), "artist_id")
            style_rows = styles.list_all()
            chosen = ask_style_ids(style_rows)
            styles.set_artist_styles(artist_id, chosen)
            styles.cnxn.commit()
            print("Nastaveno.")
            pause()

        else:
            print("Neplatná volba.")


def reports_flow(reports: ReportsDAO):
    while True:
        print("\n--- Reporty ---")
        print("1) Souhrn rezervací podle tatéra")
        print("2) Souhrn recenzí podle tatéra")
        print("3) Popularita stylů")
        print("0) Zpět")

        c = ask("> ")
        if c == "0":
            return

        if c == "1":
            print_table(reports.reservation_summary())
            pause()
        elif c == "2":
            print_table(reports.review_summary())
            pause()
        elif c == "3":
            print_table(reports.style_popularity())
            pause()
        else:
            print("Neplatná volba.")


def import_flow(import_service: ImportService):
    print("\n--- Import ---")
    print("1) Import tatérů z CSV (včetně stylů)")
    print("2) Import zákazníků z JSON")
    print("0) Zpět")

    c = ask("> ")
    if c == "0":
        return

    if c == "1":
        path = require_nonempty(ask("Cesta k CSV (např. data/artists.csv): "), "path")
        n = import_service.import_artists_csv(path)
        print(f"Import hotov, vloženo {n} tatérů.")
        pause()
    elif c == "2":
        path = require_nonempty(ask("Cesta k JSON (např. data/customers.json): "), "path")
        n = import_service.import_customers_json(path)
        print(f"Import hotov, vloženo {n} zákazníků.")
        pause()
    else:
        print("Neplatná volba.")


def admin_reservations_flow(appointments: AppointmentDAO, styles: StyleDAO, appt_service: AppointmentService):
    while True:
        print("\n--- Admin: Rezervace ---")
        print("1) Vypsat všechny rezervace")
        print("2) Upravit rezervaci")
        print("3) Smazat rezervaci")
        print("0) Zpět")

        c = ask("> ")
        if c == "0":
            return

        elif c == "1":
            rows = appointments.fetch_all(
                "SELECT TOP 50 ap.appointment_id, c.first_name + ' ' + c.last_name AS customer, "
                "a.name AS artist, ap.start_time, ap.status, d.tattoo_size, d.color, d.price_estimate "
                "FROM Appointments ap "
                "JOIN Customers c ON c.customer_id = ap.customer_id "
                "JOIN TattooArtists a ON a.artist_id = ap.artist_id "
                "LEFT JOIN AppointmentDetails d ON d.appointment_id = ap.appointment_id "
                "ORDER BY ap.appointment_id DESC"
            )
            if not rows:
                print("(Žádné rezervace.)")
            else:
                for r in rows:
                    print(f"[{r['appointment_id']}] {r['customer']} → {r['artist']} | {r['start_time']} | {r['status']} | {r['color']} | {r['price_estimate']}")
            pause()

        elif c == "2":
            appt_id = validate_positive_int(ask("Zadej appointment_id: "), "appointment_id")

            row = appointments.fetch_one(
                "SELECT ap.appointment_id, ap.customer_id, c.first_name, c.last_name, c.phone, "
                "ap.start_time, ap.duration_minutes, ap.status, ap.is_paid, "
                "d.tattoo_size, d.color, d.notes, d.price_estimate "
                "FROM Appointments ap "
                "JOIN Customers c ON c.customer_id = ap.customer_id "
                "LEFT JOIN AppointmentDetails d ON d.appointment_id = ap.appointment_id "
                "WHERE ap.appointment_id = ?", (appt_id,)
            )
            if not row:
                print("Rezervace nenalezena.")
                pause()
                continue

            print("Uprav data (Enter = ponechat původní):")
            f = ask_optional(f"Jméno [{row['first_name']}]: ") or row['first_name']
            l = ask_optional(f"Příjmení [{row['last_name']}]: ") or row['last_name']
            ph = ask_optional(f"Telefon [{row['phone'] or ''}]: ") or row['phone']

            start_in = ask_optional(f"Začátek [{row['start_time']}]: ")
            start_val = row["start_time"] if not start_in else parse_datetime(start_in)

            dur_in = ask_optional(f"Doba (min) [{row['duration_minutes']}]: ")
            dur_val = row["duration_minutes"] if not dur_in else validate_positive_int(dur_in, "duration_minutes")

            status_val = ask_enum("Status", STATUS, default=row["status"])
            paid_default = "YES" if int(row["is_paid"]) == 1 else "NO"
            paid_val = ask_enum("Zaplaceno?", ["YES", "NO"], default=paid_default) == "YES"

            size_val = ask_enum("Velikost", SIZE, default=row["tattoo_size"])
            color_val = require_nonempty(ask(f"Barva [{row['color']}]: ") or row["color"], "barva")
            notes_val = ask_optional(f"Poznámka [{row['notes'] or ''}]: ") or row["notes"]

            price_in = ask_optional(f"Cena [{row['price_estimate']}]: ")
            price_val = float(row["price_estimate"]) if not price_in else validate_float(price_in, "price_estimate")

            try:
                appt_service.update_reservation_and_customer(
                    appointment_id=appt_id,
                    customer_id=row['customer_id'],
                    customer_first=f,
                    customer_last=l,
                    customer_phone=ph,
                    start_time=start_val,
                    duration_minutes=int(dur_val),
                    status=status_val,
                    is_paid=paid_val,
                    tattoo_size=size_val,
                    color=color_val,
                    notes=notes_val,
                    price_estimate=float(price_val),
                )
                print("Rezervace byla úspěšně upravena.")
            except Exception as e:
                print(f"Chyba: {e}")

            pause()

        elif c == "3":
            appt_id = validate_positive_int(ask("Zadej appointment_id ke smazání: "), "appointment_id")
            try:
                appointments.delete(appt_id)
                appointments.cnxn.commit()
                print("Rezervace smazána (včetně detailů a vazeb).")
            except Exception as e:
                appointments.cnxn.rollback()
                print(f"Chyba při mazání: {e}")
            pause()

        else:
            print("Neplatná volba.")


if __name__ == "__main__":
    main()
