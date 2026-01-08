USE TattooPlanner;
GO

INSERT INTO TattooStyles(name, base_price) VALUES
('Linework', 900.0),
('Realism', 1500.0),
('Traditional', 1100.0),
('Blackwork', 1000.0);

INSERT INTO TattooArtists(name, specialty, contact_email, hourly_rate, is_active) VALUES
('Anna Ink', 'Linework', 'anna@tattoo.local', 1200.0, 1),
('Karel Shade', 'Realism', 'karel@tattoo.local', 1500.0, 1);


INSERT INTO ArtistStyles(artist_id, style_id)
SELECT 1, style_id FROM TattooStyles WHERE name IN ('Linework','Blackwork');
INSERT INTO ArtistStyles(artist_id, style_id)
SELECT 2, style_id FROM TattooStyles WHERE name IN ('Realism','Traditional');

INSERT INTO Customers(first_name, last_name, email, phone) VALUES
('Jan', 'Novák', 'jan.novak@email.cz', '+420 777 111 222'),
('Petra', 'Svobodová', 'petra.s@email.cz', '+420 777 333 444');


DECLARE @aid INT;
INSERT INTO Appointments(customer_id, artist_id, start_time, duration_minutes, status, is_paid)
VALUES(1, 1, DATEADD(day, 2, SYSUTCDATETIME()), 90, 'CONFIRMED', 0);
SET @aid = SCOPE_IDENTITY();

INSERT INTO AppointmentDetails(appointment_id, tattoo_size, color, notes, price_estimate)
VALUES(@aid, 'M', 'black', 'Růže na předloktí', 1800.0);

INSERT INTO AppointmentStyles(appointment_id, style_id)
SELECT @aid, style_id FROM TattooStyles WHERE name='Linework';
GO
