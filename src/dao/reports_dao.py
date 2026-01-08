from src.dao.base import BaseDAO

class ReportsDAO(BaseDAO):
    def reservation_summary(self):
        return self.fetch_all("SELECT * FROM v_artist_reservation_summary ORDER BY total_revenue DESC")

    def review_summary(self):
        return self.fetch_all("SELECT * FROM v_artist_review_summary ORDER BY avg_rating DESC")

    def style_popularity(self):
        return self.fetch_all("SELECT * FROM v_style_popularity ORDER BY num_appointments DESC")
