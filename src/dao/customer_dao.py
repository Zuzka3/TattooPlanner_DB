from src.dao.base import BaseDAO
from typing import Optional

class CustomerDAO(BaseDAO):
    def get_by_email(self, email: str):
        return self.fetch_one(
            "SELECT customer_id, first_name, last_name, email, phone FROM Customers WHERE email = ?",
            (email,),
        )

    def create(self, first_name: str, last_name: str, email: str, phone: Optional[str]):
        return self.exec_scalar(
            "INSERT INTO Customers(first_name, last_name, email, phone) "
            "VALUES(?, ?, ?, ?); SELECT SCOPE_IDENTITY();",
            (first_name, last_name, email, phone),
        )

    def update_contact(self, customer_id: int, first_name: str, last_name: str, phone: Optional[str]):
        self.exec(
            "UPDATE Customers SET first_name=?, last_name=?, phone=? WHERE customer_id=?",
            (first_name, last_name, phone, customer_id),
        )

    def list_all(self):
        return self.fetch_all(
            "SELECT customer_id, first_name, last_name, email, phone, created_at FROM Customers ORDER BY created_at DESC"
        )

    def delete(self, customer_id: int):
        self.exec("DELETE FROM Customers WHERE customer_id = ?", (customer_id,))
