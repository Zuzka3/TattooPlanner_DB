from src.dao.base import BaseDAO
from typing import Optional

class ReviewDAO(BaseDAO):
    def create(self, appointment_id: int, artist_id: int, customer_id: int, rating: int, comment: Optional[str]):
        return self.exec_scalar(
            "INSERT INTO Reviews(appointment_id, artist_id, customer_id, rating, comment) "
            "VALUES(?, ?, ?, ?, ?); SELECT SCOPE_IDENTITY();",
            (appointment_id, artist_id, customer_id, rating, comment),
        )

    def list_for_artist(self, artist_id: int):
        return self.fetch_all(
            "SELECT r.review_id, r.rating, r.comment, r.created_at, c.first_name, c.last_name "
            "FROM Reviews r JOIN Customers c ON c.customer_id = r.customer_id "
            "WHERE r.artist_id = ? ORDER BY r.created_at DESC",
            (artist_id,),
        )
