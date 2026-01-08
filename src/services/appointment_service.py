from src.dao.customer_dao import CustomerDAO
from src.dao.appointment_dao import AppointmentDAO
from src.services.exceptions import TransactionError, ValidationError
from src.services.validators import validate_email
from typing import Optional

class AppointmentService:
    def __init__(self, cnxn):
        self.cnxn = cnxn
        self.customers = CustomerDAO(cnxn)
        self.appointments = AppointmentDAO(cnxn)

    def create_reservation(
        self,
        customer_first: str,
        customer_last: str,
        customer_email: str,
        customer_phone: Optional[str],
        artist_id: int,
        start_time,
        duration_minutes: int,
        status: str,
        is_paid: bool,
        tattoo_size: str,
        color: str,
        notes: Optional[str],
        price_estimate: float,
        style_ids: list[int],
        simulate_failure: bool = False,
    ) -> int:
        customer_email = validate_email(customer_email)
        try:
            cur = self.cnxn.cursor()
            existing = self.customers.get_by_email(customer_email)
            if existing:
                customer_id = existing["customer_id"]
                self.customers.update_contact(customer_id, customer_first, customer_last, customer_phone)
            else:
                customer_id = int(self.customers.create(customer_first, customer_last, customer_email, customer_phone))

            appointment_id = int(
                self.appointments.create_appointment(customer_id, artist_id, start_time, duration_minutes, status, is_paid)
            )

            self.appointments.create_details(appointment_id, tattoo_size, color, notes, price_estimate)

            self.appointments.set_appointment_styles(appointment_id, style_ids)

            if simulate_failure:
                raise TransactionError("Simulovaná chyba platby — transakce se musí vrátit zpět (ROLLBACK).")

            self.cnxn.commit()
            return appointment_id

        except (ValidationError, TransactionError):
            self.cnxn.rollback()
            raise
        except Exception as e:
            self.cnxn.rollback()
            raise TransactionError("Transakce selhala, změny byly vráceny zpět (rollback).") from e

    def update_reservation_and_customer(
        self,
        appointment_id: int,
        customer_id: int,
        customer_first: str,
        customer_last: str,
        customer_phone: Optional[str],
        start_time,
        duration_minutes: int,
        status: str,
        is_paid: bool,
        tattoo_size: str,
        color: str,
        notes: Optional[str],
        price_estimate: float,
    ):
        try:
            self.customers.update_contact(customer_id, customer_first, customer_last, customer_phone)
            self.appointments.update_reservation(appointment_id, start_time, duration_minutes, status, is_paid)
            self.appointments.update_details(appointment_id, tattoo_size, color, notes, price_estimate)
            self.cnxn.commit()
        except Exception as e:
            self.cnxn.rollback()
            raise TransactionError("Úprava rezervace selhala — změny byly vráceny zpět.") from e
