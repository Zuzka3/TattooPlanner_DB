IF DB_ID('TattooPlanner') IS NULL
BEGIN
    CREATE DATABASE TattooPlanner;
END
GO

USE TattooPlanner;
GO


IF OBJECT_ID('dbo.Reviews', 'U') IS NOT NULL DROP TABLE dbo.Reviews;
IF OBJECT_ID('dbo.AppointmentStyles', 'U') IS NOT NULL DROP TABLE dbo.AppointmentStyles;
IF OBJECT_ID('dbo.AppointmentDetails', 'U') IS NOT NULL DROP TABLE dbo.AppointmentDetails;
IF OBJECT_ID('dbo.Appointments', 'U') IS NOT NULL DROP TABLE dbo.Appointments;
IF OBJECT_ID('dbo.ArtistStyles', 'U') IS NOT NULL DROP TABLE dbo.ArtistStyles;
IF OBJECT_ID('dbo.TattooStyles', 'U') IS NOT NULL DROP TABLE dbo.TattooStyles;
IF OBJECT_ID('dbo.TattooArtists', 'U') IS NOT NULL DROP TABLE dbo.TattooArtists;
IF OBJECT_ID('dbo.Customers', 'U') IS NOT NULL DROP TABLE dbo.Customers;
GO

CREATE TABLE Customers (
    customer_id INT IDENTITY(1,1) PRIMARY KEY,
    first_name NVARCHAR(50) NOT NULL,
    last_name  NVARCHAR(50) NOT NULL,
    email      NVARCHAR(100) NOT NULL UNIQUE,
    phone      NVARCHAR(30) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE TattooArtists (
    artist_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    specialty NVARCHAR(100) NULL,
    contact_email NVARCHAR(100) NOT NULL UNIQUE,
    hourly_rate FLOAT NOT NULL,
    is_active BIT NOT NULL DEFAULT 1
);

CREATE TABLE TattooStyles (
    style_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    base_price FLOAT NOT NULL
);


CREATE TABLE ArtistStyles (
    artist_id INT NOT NULL,
    style_id INT NOT NULL,
    PRIMARY KEY (artist_id, style_id),
    CONSTRAINT FK_ArtistStyles_Artist FOREIGN KEY (artist_id) REFERENCES TattooArtists(artist_id) ON DELETE CASCADE,
    CONSTRAINT FK_ArtistStyles_Style  FOREIGN KEY (style_id)  REFERENCES TattooStyles(style_id) ON DELETE CASCADE
);


CREATE TABLE Appointments (
    appointment_id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    artist_id INT NOT NULL,
    start_time DATETIME2 NOT NULL,
    duration_minutes INT NOT NULL,
    status VARCHAR(10) NOT NULL CHECK (status IN ('PENDING', 'CONFIRMED', 'DONE', 'CANCELLED')),
    is_paid BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Appointments_Customer FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    CONSTRAINT FK_Appointments_Artist   FOREIGN KEY (artist_id)   REFERENCES TattooArtists(artist_id)
);


CREATE TABLE AppointmentDetails (
    detail_id INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    tattoo_size VARCHAR(2) NOT NULL CHECK (tattoo_size IN ('S','M','L','XL')),
    color NVARCHAR(30) NOT NULL,
    notes NVARCHAR(200) NULL,
    price_estimate FLOAT NOT NULL,
    CONSTRAINT FK_Details_Appointment FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id) ON DELETE CASCADE
);


CREATE TABLE AppointmentStyles (
    appointment_id INT NOT NULL,
    style_id INT NOT NULL,
    PRIMARY KEY (appointment_id, style_id),
    CONSTRAINT FK_AppStyle_Appointment FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id) ON DELETE CASCADE,
    CONSTRAINT FK_AppStyle_Style       FOREIGN KEY (style_id) REFERENCES TattooStyles(style_id)
);


CREATE TABLE Reviews (
    review_id INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    artist_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment NVARCHAR(500) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_Reviews_Appointment FOREIGN KEY (appointment_id) REFERENCES Appointments(appointment_id) ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_Artist FOREIGN KEY (artist_id) REFERENCES TattooArtists(artist_id),
    CONSTRAINT FK_Reviews_Customer FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);
GO

IF OBJECT_ID('dbo.v_artist_reservation_summary', 'V') IS NOT NULL DROP VIEW dbo.v_artist_reservation_summary;
GO
CREATE VIEW dbo.v_artist_reservation_summary AS
SELECT
    a.artist_id,
    a.name AS artist_name,
    COUNT(ap.appointment_id) AS num_appointments,
    SUM(d.price_estimate) AS total_revenue,
    AVG(CAST(ap.duration_minutes AS FLOAT)) AS avg_duration_minutes
FROM TattooArtists a
JOIN Appointments ap ON ap.artist_id = a.artist_id
JOIN AppointmentDetails d ON d.appointment_id = ap.appointment_id
GROUP BY a.artist_id, a.name;
GO

IF OBJECT_ID('dbo.v_artist_review_summary', 'V') IS NOT NULL DROP VIEW dbo.v_artist_review_summary;
GO
CREATE VIEW dbo.v_artist_review_summary AS
SELECT
    a.artist_id,
    a.name AS artist_name,
    COUNT(r.review_id) AS num_reviews,
    AVG(CAST(r.rating AS FLOAT)) AS avg_rating
FROM TattooArtists a
LEFT JOIN Reviews r ON r.artist_id = a.artist_id
GROUP BY a.artist_id, a.name;
GO

IF OBJECT_ID('dbo.v_style_popularity', 'V') IS NOT NULL DROP VIEW dbo.v_style_popularity;
GO
CREATE VIEW dbo.v_style_popularity AS
SELECT
    s.style_id,
    s.name AS style_name,
    COUNT(x.appointment_id) AS num_appointments
FROM TattooStyles s
LEFT JOIN AppointmentStyles x ON x.style_id = s.style_id
GROUP BY s.style_id, s.name;
GO
