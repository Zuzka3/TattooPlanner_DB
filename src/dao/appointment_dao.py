from src.dao.base import BaseDAO
from typing import Optional

class AppointmentDAO(BaseDAO):
    def create_appointment(self, customer_id: int, artist_id: int, start_time, duration_minutes: int, status: str, is_paid: bool):
        return self.exec_scalar(
            "INSERT INTO Appointments(customer_id, artist_id, start_time, duration_minutes, status, is_paid) "
            "VALUES(?, ?, ?, ?, ?, ?); SELECT SCOPE_IDENTITY();",
            (customer_id, artist_id, start_time, duration_minutes, status, 1 if is_paid else 0),
        )

    def create_details(self, appointment_id: int, size: str, color: str, notes: Optional[str], price_estimate: float):
        self.exec(
            "INSERT INTO AppointmentDetails(appointment_id, tattoo_size, color, notes, price_estimate) "
            "VALUES(?, ?, ?, ?, ?)",
            (appointment_id, size, color, notes, price_estimate),
        )

    def set_appointment_styles(self, appointment_id: int, style_ids: list[int]):
        self.exec("DELETE FROM AppointmentStyles WHERE appointment_id = ?", (appointment_id,))
        for sid in style_ids:
            self.exec("INSERT INTO AppointmentStyles(appointment_id, style_id) VALUES(?, ?)", (appointment_id, sid))

    def list_for_customer_email(self, email: str):
        return self.fetch_all(
            "SELECT ap.appointment_id, ap.start_time, ap.duration_minutes, ap.status, ap.is_paid, "
            "ar.name AS artist_name, d.tattoo_size, d.color, d.price_estimate "
            "FROM Appointments ap "
            "JOIN Customers c ON c.customer_id = ap.customer_id "
            "JOIN TattooArtists ar ON ar.artist_id = ap.artist_id "
            "LEFT JOIN AppointmentDetails d ON d.appointment_id = ap.appointment_id "
            "WHERE c.email = ? "
            "ORDER BY ap.start_time DESC",
            (email,),
        )

    def update_reservation(self, appointment_id: int, start_time, duration_minutes: int, status: str, is_paid: bool):
        self.exec(
            "UPDATE Appointments SET start_time=?, duration_minutes=?, status=?, is_paid=? WHERE appointment_id=?",
            (start_time, duration_minutes, status, 1 if is_paid else 0, appointment_id),
        )

    def update_details(self, appointment_id: int, size: str, color: str, notes: Optional[str], price_estimate: float):
        self.exec(
            "UPDATE AppointmentDetails SET tattoo_size=?, color=?, notes=?, price_estimate=? WHERE appointment_id=?",
            (size, color, notes, price_estimate, appointment_id),
        )

    def delete(self, appointment_id: int):
        self.exec("DELETE FROM Appointments WHERE appointment_id = ?", (appointment_id,))
