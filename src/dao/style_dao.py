from src.dao.base import BaseDAO

class StyleDAO(BaseDAO):
    def list_all(self):
        return self.fetch_all("SELECT style_id, name, base_price FROM TattooStyles ORDER BY name")

    def create(self, name: str, base_price: float):
        return self.exec_scalar(
            "INSERT INTO TattooStyles(name, base_price) VALUES(?, ?); SELECT SCOPE_IDENTITY();",
            (name, base_price),
        )

    def set_artist_styles(self, artist_id: int, style_ids: list[int]):
        self.exec("DELETE FROM ArtistStyles WHERE artist_id = ?", (artist_id,))
        for sid in style_ids:
            self.exec("INSERT INTO ArtistStyles(artist_id, style_id) VALUES(?, ?)", (artist_id, sid))

    def get_styles_for_artist(self, artist_id: int):
        return self.fetch_all(
            "SELECT s.style_id, s.name, s.base_price "
            "FROM TattooStyles s JOIN ArtistStyles a ON a.style_id = s.style_id "
            "WHERE a.artist_id = ? ORDER BY s.name",
            (artist_id,),
        )
