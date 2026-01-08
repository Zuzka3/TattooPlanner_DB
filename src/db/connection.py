import json
from pathlib import Path
import pyodbc

from src.services.exceptions import ConfigError, DatabaseError

def load_config(path: str = "config.json") -> dict:
    p = Path(path)
    if not p.exists():
        raise ConfigError(
            "Chybí config.json. Vytvoř ho podle config.example.json a doplň přihlašovací údaje."
        )
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"config.json není validní JSON: {e}")

    if "db" not in data:
        raise ConfigError("V config.json chybí sekce 'db'.")

    required = ["driver", "server", "database", "username", "password"]
    missing = [k for k in required if k not in data["db"]]
    if missing:
        raise ConfigError(f"V config.json chybí DB klíče: {', '.join(missing)}")

    return data

def _build_conn_str(db_cfg: dict) -> str:
    driver = db_cfg["driver"]
    server = db_cfg["server"]
    database = db_cfg["database"]
    username = db_cfg["username"]
    password = db_cfg["password"]
    encrypt = "yes" if db_cfg.get("encrypt", False) else "no"
    trust = "yes" if db_cfg.get("trust_server_certificate", True) else "no"

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust};"
    )

def get_connection(config: dict):
    try:
        conn_str = _build_conn_str(config["db"])
        cnxn = pyodbc.connect(conn_str, timeout=5)
        cnxn.autocommit = False
        return cnxn
    except pyodbc.Error as e:
        raise DatabaseError(
            "Nepodařilo se připojit k databázi. Zkontroluj config.json a jestli běží SQL Server/ODBC driver."
        ) from e
