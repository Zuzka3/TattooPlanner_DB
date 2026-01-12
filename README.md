# Tattoo Planner 

Konzolová aplikace v **Pythonu**, která slouží jako jednoduchý „tattoo planner“ – správa **tatérů**, **zákazníků**, **stylů tetování** a **rezervací** nad relační databází **Microsoft SQL Server**.

---

## Software požadavky

Aplikace vyžaduje:
- **Python 3.9** (doporučeno)
- **Microsoft SQL Server** + ideálně **SQL Server Management Studio (SSMS)**
- **ODBC driver pro SQL Server** (typicky „ODBC Driver 17 for SQL Server“ nebo „ODBC Driver 18 for SQL Server“)
- Python balíčky z `requirements.txt`:
  - `pyodbc`
  - `reportlab` 

---

## Instalace a spuštění aplikace

### 1) Otevření projektu v CMD
1. Otevři **CMD** (Win + R → `cmd`).
2. Přejdi do složky projektu (tam, kde je `src/`, `requirements.txt`, `config.example.json`):

```bat
cd C:\cesta\k\TattooPlanner_DB
```
---

### 2) Instalace závislostí (virtuální prostředí)
V kořeni projektu spusť:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3) Vytvoření a nastavení databáze
1. Otevři v SSMS soubor:
   - `sql/schema.sql`
2. Spusť skript – vytvoří databázi **TattooPlanner** (pokud neexistuje) a tabulky + view.
3. Volitelně naplň ukázková data spuštěním:
   - `sql/seed.sql`


### 4) Konfigurační soubor
1. Zkopíruj `config.example.json` → `config.json`
2. Do `config.json` doplň přihlašovací údaje k SQL Serveru:

```json
{
  "db": {
    "driver": "ODBC Driver 17 for SQL Server",
    "server": "PC000",
    "database": "TattooPlanner",
    "username": "CHANGE_ME",
    "password": "CHANGE_ME",
    "trust_server_certificate": true,
    "encrypt": false
  },
  "app": {
    "default_duration_minutes": 90,
    "default_hourly_rate": 1200.0,
    "currency": "CZK",
    "admin_pin": "123"
  }
}
```
> Poznámka k ODBC driveru:
> Hodnota `db.driver` musí přesně odpovídat názvu driveru nainstalovanému ve Windows.
> Nejčastěji je to `ODBC Driver 17 for SQL Server` nebo `ODBC Driver 18 for SQL Server`

### 5) Spuštění aplikace (přes CMD)
V kořeni projektu (stále v CMD) spusť:

```bat
python -m src.main
```

---

## Ovládání aplikace

Po spuštění se zobrazí hlavní menu:

- **Zákazník**
  - vytvoření rezervace
  - vypsání vlastních rezervací podle e‑mailu

- **Admin**
  - přihlášení pomocí PINu (PIN je v `config.json` → `app.admin_pin`, defaultně `123`)
  - správa tatérů 
  - správa rezervací 
  - import dat
  - reporty 

---

## Import dat (CSV / JSON)

Ukázkové soubory jsou ve složce **`data/`**.

### `artists.csv`
- Umístění: `data/artists.csv`
- Sloupce (pořadí):  
  `name,specialty,contact_email,hourly_rate,is_active,styles`
- `styles` se zapisují jako seznam oddělený znakem `|` (např. `Dotwork|Linework`) a názvy musí existovat v tabulce `TattooStyles` (buď ze `seed.sql`, nebo si je přidej ručně).

Ukázka:

```csv
name,specialty,contact_email,hourly_rate,is_active,styles
Michaela Dot,Dotwork,misa@tattoo.local,1100,1,Dotwork|Linework
Tom Oldschool,Traditional,tom@tattoo.local,1300,1,Traditional
```

### `customers.json`
- Umístění: `data/customers.json`
- Formát: JSON pole objektů s poli:
  - `first_name`
  - `last_name`
  - `email` (musí být unikátní)
  - `phone` (volitelně)

Ukázka:

```json
[
  {
    "first_name": "Lucie",
    "last_name": "Kovářová",
    "email": "lucie.k@email.cz",
    "phone": "+420 777 555 666"
  }
]
```

---

## Struktura projektu

- `sql/`
  - `schema.sql` – vytvoření DB struktury (tabulky, vazby, VIEW)
  - `seed.sql` – ukázková data
- `src/`
  - `db/` – připojení k DB, načtení konfigurace
  - `dao/` – DAO vrstvy 
  - `services/` – logika aplikace + transakce/validace
  - `ui/` – konzolové UI (menu, vstupy, výpisy)
- `data/` – ukázkové importní soubory

---

## Nejčastější problémy

- **Nepřipojí se to k DB**
  - zkontroluj `config.json`
  - ověř, že běží SQL Server a máš správné přihlašovací údaje
  - ověř, že je nainstalovaný správný ODBC driver (17/18) a že název driveru v configu odpovídá instalaci

---

