import csv, json
from src.dao.artist_dao import ArtistDAO
from src.dao.customer_dao import CustomerDAO
from src.dao.style_dao import StyleDAO
from src.services.exceptions import ValidationError

class ImportService:
    def __init__(self, cnxn):
        self.cnxn = cnxn
        self.artists = ArtistDAO(cnxn)
        self.customers = CustomerDAO(cnxn)
        self.styles = StyleDAO(cnxn)

    def import_artists_csv(self, path: str) -> int:
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("name") or "").strip()
                email = (row.get("contact_email") or "").strip()
                if not name or not email:
                    raise ValidationError("CSV: name a contact_email jsou povinné.")
                specialty = (row.get("specialty") or "").strip() or None
                hourly_rate = float(row.get("hourly_rate") or 0)
                is_active = (row.get("is_active") or "1").strip() in ("1", "true", "True", "yes", "ano")

                artist_id = int(self.artists.create(name, specialty, email, hourly_rate, is_active))

                # styly
                style_names = [s.strip() for s in (row.get("styles") or "").split("|") if s.strip()]
                if style_names:
                    all_styles = {s["name"]: s["style_id"] for s in self.styles.list_all()}
                    style_ids = []
                    for n in style_names:
                        if n not in all_styles:
                            sid = int(self.styles.create(n, 500.0))
                            all_styles[n] = sid
                        style_ids.append(int(all_styles[n]))
                    self.styles.set_artist_styles(artist_id, style_ids)

                count += 1

        self.cnxn.commit()
        return count

    def import_customers_json(self, path: str) -> int:
        data = json.loads(open(path, "r", encoding="utf-8").read())
        if not isinstance(data, list):
            raise ValidationError("JSON musí být seznam zákazníků (array).")

        count = 0
        for c in data:
            email = (c.get("email") or "").strip()
            if not email:
                raise ValidationError("JSON: každý zákazník musí mít email.")
            if self.customers.get_by_email(email):
                continue
            self.customers.create(
                (c.get("first_name") or "").strip() or "Neznámé",
                (c.get("last_name") or "").strip() or "Neznámé",
                email,
                (c.get("phone") or None),
            )
            count += 1

        self.cnxn.commit()
        return count
