from typing import Any, Iterable
from src.services.exceptions import DatabaseError
import pyodbc

class BaseDAO:
    def __init__(self, cnxn):
        self.cnxn = cnxn

    def fetch_all(self, sql: str, params: Iterable[Any] = ()):
        try:
            cur = self.cnxn.cursor()
            cur.execute(sql, params)
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        except pyodbc.Error as e:
            raise DatabaseError("Chyba při čtení dat z DB.") from e

    def fetch_one(self, sql: str, params: Iterable[Any] = ()):
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def exec(self, sql: str, params: Iterable[Any] = ()):
        try:
            cur = self.cnxn.cursor()
            cur.execute(sql, params)
            return cur
        except pyodbc.Error as e:
            raise DatabaseError("Chyba při zápisu do DB.") from e

    def exec_scalar(self, sql: str, params: Iterable[Any] = ()):
        cur = self.exec(sql, params)
        while True:
            if cur.description is not None:
                row = cur.fetchone()
                return row[0] if row else None

            if not cur.nextset():
                return None

