from src.dao.base import BaseDAO
from typing import Optional

class ArtistDAO(BaseDAO):
    def list_active(self):
        return self.fetch_all(
            "SELECT artist_id, name, specialty, contact_email, hourly_rate, is_active "
            "FROM TattooArtists WHERE is_active = 1 ORDER BY name"
        )

    def list_all(self):
        return self.fetch_all(
            "SELECT artist_id, name, specialty, contact_email, hourly_rate, is_active "
            "FROM TattooArtists ORDER BY name"
        )

    def get(self, artist_id: int):
        return self.fetch_one(
            "SELECT artist_id, name, specialty, contact_email, hourly_rate, is_active "
            "FROM TattooArtists WHERE artist_id = ?",
            (artist_id,),
        )

    def create(self, name: str, specialty: Optional[str], email: str, hourly_rate: float, is_active: bool = True):
        return self.exec_scalar(
            "INSERT INTO TattooArtists(name, specialty, contact_email, hourly_rate, is_active) "
            "VALUES(?, ?, ?, ?, ?); SELECT SCOPE_IDENTITY();",
            (name, specialty, email, hourly_rate, 1 if is_active else 0),
        )

    def update(self, artist_id: int, name: str, specialty: Optional[str], email: str, hourly_rate: float, is_active: bool):
        self.exec(
            "UPDATE TattooArtists SET name=?, specialty=?, contact_email=?, hourly_rate=?, is_active=? WHERE artist_id=?",
            (name, specialty, email, hourly_rate, 1 if is_active else 0, artist_id),
        )

    def delete(self, artist_id: int):
        self.exec("DELETE FROM TattooArtists WHERE artist_id = ?", (artist_id,))
