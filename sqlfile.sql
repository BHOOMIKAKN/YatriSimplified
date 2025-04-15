CREATE TABLE users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  phone_number VARCHAR(15),
  age INT,
  password VARCHAR(255),
  nationality VARCHAR(100) DEFAULT NULL,
  adhar_number VARCHAR(20) DEFAULT NULL,
  passport_number VARCHAR(20) DEFAULT NULL,
  document TEXT DEFAULT NULL,
  wallet_balance decimal(10,2) default 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE trains (
    train_id INT PRIMARY KEY AUTO_INCREMENT,
    train_number VARCHAR(10) UNIQUE NOT NULL,
    train_name VARCHAR(100) NOT NULL,
    train_type VARCHAR(50),
    operator VARCHAR(100)
);


CREATE TABLE train_routes (
    route_id INT PRIMARY KEY AUTO_INCREMENT,
    train_id INT NOT NULL,
    station_name VARCHAR(100) NOT NULL,
    station_code VARCHAR(10),
    stop_number INT NOT NULL,
    arrival_time TIME,
    departure_time TIME,
    halt_time INT, -- in minutes
    distance_from_start INT, -- in kilometers

    FOREIGN KEY (train_id) REFERENCES trains(train_id)
        ON DELETE CASCADE
);

CREATE TABLE fares (
    fare_id INT PRIMARY KEY AUTO_INCREMENT,
    train_id INT NOT NULL,
    from_station VARCHAR(100),
    to_station VARCHAR(100),
    travel_class VARCHAR(50), -- e.g., Sleeper, AC
    fare DECIMAL(10,2),

    FOREIGN KEY (train_id) REFERENCES trains(train_id)
);

CREATE TABLE buses (
    bus_id INT PRIMARY KEY AUTO_INCREMENT,
    bus_number VARCHAR(20) UNIQUE NOT NULL,
    bus_name VARCHAR(100),
    bus_type VARCHAR(50),         -- e.g., AC, Non-AC, Sleeper
    operator VARCHAR(100)         -- e.g., KSRTC, Private Operator
);


CREATE TABLE bus_routes (
    route_id INT PRIMARY KEY AUTO_INCREMENT,
    bus_id INT NOT NULL,
    station_name VARCHAR(100) NOT NULL,
    station_code VARCHAR(10),
    stop_number INT NOT NULL,         -- order of stop
    arrival_time TIME,
    departure_time TIME,
    halt_time INT,                    -- in minutes
    distance_from_start INT,          -- in kilometers

    FOREIGN KEY (bus_id) REFERENCES buses(bus_id)
        ON DELETE CASCADE
);

CREATE TABLE unified_locations (
    location_id INT PRIMARY KEY AUTO_INCREMENT,
    location_name VARCHAR(100),
    bus_station_code VARCHAR(10),
    train_station_code VARCHAR(10)
);
CREATE TABLE bus_seats (
  bus_id INT,
  travel_date DATE,
  available_seats INT,
  max_seats INT,
  PRIMARY KEY (bus_id, travel_date),
  FOREIGN KEY (bus_id) REFERENCES buses(bus_id)
);
CREATE TABLE train_seats (
  train_id INT,
  travel_date DATE,
  available_seats INT,
  max_seats INT,
  PRIMARY KEY (train_id, travel_date),
  FOREIGN KEY (train_id) REFERENCES trains(train_id)
);

CREATE TABLE flight_seats (
  flight_id INT,
  travel_date DATE,
  available_seats INT,
  max_seats INT,
  PRIMARY KEY (flight_id, travel_date),
  FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
);
-- Insert flights
INSERT INTO flights (flight_number, flight_name, airline_name, aircraft_type, operator)
VALUES 
  ('AI202', 'Bangalore to Mumbai Express', 'Air India', 'Airbus A320', 'Air India Ltd.'),
  ('6E305', 'Bangalore to Delhi Shuttle', 'IndiGo', 'Airbus A320neo', 'InterGlobe Aviation'),
  ('SG421', 'Bangalore to Hyderabad Flyer', 'SpiceJet', 'Boeing 737', 'SpiceJet Ltd.');

-- AI202 (Bangalore -> Mumbai)
INSERT INTO flight_routes (flight_id, airport_name, airport_code, stop_number, arrival_time, departure_time, halt_time, distance_from_start)
VALUES
  (1, 'Kempegowda International Airport', 'BLR', 1, NULL, '08:00:00', 0, 0),
  (1, 'Chhatrapati Shivaji Maharaj International Airport', 'BOM', 2, '10:00:00', NULL, 0, 850);

-- 6E305 (Bangalore -> Delhi)
INSERT INTO flight_routes (flight_id, airport_name, airport_code, stop_number, arrival_time, departure_time, halt_time, distance_from_start)
VALUES
  (2, 'Kempegowda International Airport', 'BLR', 1, NULL, '09:00:00', 0, 0),
  (2, 'Indira Gandhi International Airport', 'DEL', 2, '11:30:00', NULL, 0, 1700);

-- SG421 (Bangalore -> Hyderabad)
INSERT INTO flight_routes (flight_id, airport_name, airport_code, stop_number, arrival_time, departure_time, halt_time, distance_from_start)
VALUES
  (3, 'Kempegowda International Airport', 'BLR', 1, NULL, '12:00:00', 0, 0),
  (3, 'Rajiv Gandhi International Airport', 'HYD', 2, '13:00:00', NULL, 0, 500);

INSERT INTO unified_locations (location_name, bus_station_code, train_station_code) VALUES
('Chitradurga', 'CTA', 'CTA'),             -- Same code for both modes
('Tumkur', 'TKB', 'TK'),                   -- Different bus/train codes
('Nelamangala', 'NMG', 'NMG'),             -- Optional transfer point
('Bangalore', 'MJC', 'SBC'),               -- Hub: Majestic for bus, SBC for train
('Bangarapet', 'BBG', 'BWT'),              -- Destination: different codes
('Arakkonam', 'ARK', 'AJJ');               -- For future route expansion

CREATE TABLE fares (
    fare_id INT PRIMARY KEY AUTO_INCREMENT,
    mode ENUM('bus', 'train') NOT NULL,
    from_station_code VARCHAR(10) NOT NULL,
    to_station_code VARCHAR(10) NOT NULL,
    fare DECIMAL(10,2) NOT NULL
);
ALTER TABLE bus_routes ADD arrived_time TIME AFTER departure_time;
ALTER TABLE train_routes ADD arrived_time TIME AFTER departure_time;
UPDATE bus_routes AS br1
JOIN bus_routes AS br2
  ON br1.bus_id = br2.bus_id AND br1.stop_number + 1 = br2.stop_number
SET br1.arrived_time = br2.arrival_time;
UPDATE train_routes AS tr1
JOIN train_routes AS tr2
  ON tr1.train_id = tr2.train_id AND tr1.stop_number + 1 = tr2.stop_number
SET tr1.arrived_time = tr2.arrival_time;

-- Bus fares
INSERT INTO fares (mode, from_station_code, to_station_code, fare) VALUES
('bus', 'DVG', 'CTA', 80.00),
('bus', 'CTA', 'TK', 100.00),
('bus', 'CTA', 'NMG', 150.00),
('bus', 'CTA', 'MJC', 180.00),
('bus', 'TK', 'NMG', 70.00),
('bus', 'TK', 'MJC', 90.00);

-- Train fares
INSERT INTO fares (mode, from_station_code, to_station_code, fare) VALUES
('train', 'SBC', 'BWT', 40.00),
('train', 'NMG', 'BWT', 50.00),
('train', 'TK', 'BWT', 60.00),
('train', 'ARK', 'BWT', 80.00),
('train', 'AJJ', 'BWT', 70.00);


CREATE TABLE cabs (
  cab_id INT PRIMARY KEY AUTO_INCREMENT,
  cab_number VARCHAR(20) UNIQUE,
  driver_name VARCHAR(100),
  cab_type VARCHAR(20), 
  seater INT, 
  email VARCHAR(100),
  phone_number VARCHAR(15),
  region VARCHAR(100),
  password VARCHAR(255),
  from_location VARCHAR(100),
  to_location VARCHAR(100),
  price DECIMAL(10,2),
  mode VARCHAR(20)
);
CREATE TABLE passengers (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    mode VARCHAR(20),
    name VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    journey_date DATE,
    source VARCHAR(100),
    destination VARCHAR(100),
    price DECIMAL(10, 2),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

create table journey_segments(
  segment_id INT PRIMARY KEY AUTO_INCREMENT,
  booking_id INT,
  transport_type VARCHAR(20), -- Train, Bus, Cab
  transport_id INT, -- train_id, bus_id, cab_id
  segment_source VARCHAR(100),
  segment_destination VARCHAR(100),
  departure_time TIME,
  arrival_time TIME,
  price DECIMAL(10,2),
  is_paid BOOLEAN DEFAULT FALSE
);

CREATE TABLE payment (
  payment_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  booking_id INT,
  service_type VARCHAR(20),             
  transport_id INT,                     
  amount DECIMAL(10, 2),
  payment_method VARCHAR(50),          
  payment_status VARCHAR(20),          
  payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (booking_id) REFERENCES passengers(booking_id)
);

CREATE TABLE flights (
    flight_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_number VARCHAR(20) UNIQUE NOT NULL,
    flight_name VARCHAR(100) NOT NULL,
    airline_name VARCHAR(100) NOT NULL,
    aircraft_type VARCHAR(100),
    operator VARCHAR(100)
);


CREATE TABLE flight_routes (
    route_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_id INT NOT NULL,
    airport_name VARCHAR(100) NOT NULL,
    airport_code VARCHAR(10),
    stop_number INT NOT NULL,
    arrival_time TIME,
    departure_time TIME,
    halt_time INT,  -- in minutes
    distance_from_start INT, -- in kilometers

    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
        ON DELETE CASCADE
);

CREATE TABLE flight_fares (
    fare_id INT PRIMARY KEY AUTO_INCREMENT,
    flight_id INT NOT NULL,
    from_airport VARCHAR(100),
    to_airport VARCHAR(100),
    travel_class VARCHAR(50), -- e.g., Economy, Business
    fare DECIMAL(10,2),

    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
        ON DELETE CASCADE
);
ALTER TABLE unified_locations ADD COLUMN airport_code VARCHAR(20) DEFAULT null;  -- values: 'train', 'flight', 'bus'

-- AI202: Bangalore (BLR) to Mumbai (BOM)
INSERT INTO flight_fares (flight_id, from_airport, to_airport, travel_class, fare)
VALUES 
  (1, 'Kempegowda International Airport', 'Chhatrapati Shivaji Maharaj International Airport', 'Economy', 4500.00),
  (1, 'Kempegowda International Airport', 'Chhatrapati Shivaji Maharaj International Airport', 'Business', 8500.00);

-- 6E305: Bangalore (BLR) to Delhi (DEL)
INSERT INTO flight_fares (flight_id, from_airport, to_airport, travel_class, fare)
VALUES 
  (2, 'Kempegowda International Airport', 'Indira Gandhi International Airport', 'Economy', 5500.00),
  (2, 'Kempegowda International Airport', 'Indira Gandhi International Airport', 'Business', 10500.00);

-- SG421: Bangalore (BLR) to Hyderabad (HYD)
INSERT INTO flight_fares (flight_id, from_airport, to_airport, travel_class, fare)
VALUES 
  (3, 'Kempegowda International Airport', 'Rajiv Gandhi International Airport', 'Economy', 3200.00),
  (3, 'Kempegowda International Airport', 'Rajiv Gandhi International Airport', 'Business', 7200.00);

INSERT INTO unified_locations (location_name, bus_station_code, train_station_code) VALUES
('Davanagere', 'DVG', 'DVG_T'),
('Chitradurga', 'CTA', 'CTA_T'),
('Tumkur', 'TK', 'TK_T'),
('Bangalore', 'MJC', 'SBC'),
('Nelamangala', 'NMG', 'NMG_T'),
('Kengeri', 'KGR', 'KGI'),
('Bangalore Cantt', 'MJC', 'BNC'),
('Bangalore City', 'MJC', 'SBC');
INSERT INTO bus_routes (bus_id, station_name, station_code, stop_number, arrival_time, departure_time, halt_time, distance_from_start) VALUES
(1, 'Davanagere', 'DVG', 1, '06:00:00', '06:10:00', 10, 0),
(1, 'Chitradurga', 'CTA', 2, '07:30:00', '07:35:00', 5, 65),
(1, 'Tumkur', 'TK', 3, '09:15:00', '09:20:00', 5, 180),
(1, 'Nelamangala', 'NMG', 4, '10:00:00', '10:05:00', 5, 230),
(1, 'Bangalore', 'MJC', 5, '10:30:00', NULL, 0, 250),
(2, 'Davanagere', 'DVG', 1, '06:15:00', '06:20:00', 5, 0),
(2, 'Tumkur', 'TK', 2, '08:30:00', '08:35:00', 5, 180),
(2, 'Bangalore', 'MJC', 3, '10:00:00', NULL, 0, 250);
INSERT INTO train_routes (train_id, station_name, station_code, stop_number, arrival_time, departure_time, halt_time, distance_from_start) VALUES
(101, 'Bangalore', 'SBC', 1, '09:00:00', '09:15:00', 15, 0),
(101, 'Tumkur', 'TK_T', 2, '10:45:00', '10:50:00', 5, 70),
(101, 'Chitradurga', 'CTA_T', 3, '12:00:00', NULL, 0, 150),
(102, 'Bangalore Cantt', 'BNC', 1, '08:45:00', '09:00:00', 15, 0),
(102, 'Tumkur', 'TK_T', 2, '10:30:00', '10:35:00', 5, 70);
INSERT INTO buses (bus_id, bus_number, bus_name) VALUES
(1, 'KA01AB1234', 'Express Deluxe'),
(2, 'KA01XY5678', 'Morning Star');
INSERT INTO trains (train_id, train_number, train_name) VALUES
(101, '12345', 'Superfast Express'),
(102, '67890', 'Jan Shatabdi');

INSERT INTO fares (mode, from_station_code, to_station_code, fare) VALUES
('bus', 'DVG', 'MJC', 180.00),
('bus', 'DVG', 'CTA', 60.00),
('bus', 'DVG', 'TK', 140.00),
('train', 'SBC', 'TK_T', 40.00),
('train', 'BNC', 'TK_T', 35.00);
-- Bus seat info
INSERT INTO bus_seats (bus_id, travel_date, available_seats, max_seats)
VALUES (1, '2025-04-15', 32, 40),(2,'2025-04-12',12,50);

-- Train seat info
INSERT INTO train_seats (train_id, travel_date, available_seats, max_seats)
VALUES (101, '2025-04-15', 100, 120),(102, '2025-04-12', 50, 100);
-- AI202: Bangalore to Mumbai
INSERT INTO flight_seats (flight_id, travel_date, available_seats, max_seats)
VALUES
  (1, '2025-04-15', 40, 180),
  (1, '2025-04-16', 75, 180),
  (1, '2025-04-17', 0, 180); -- fully booked
INSERT INTO flight_seats (flight_id, travel_date, available_seats, max_seats)
VALUES
  (3, '2025-04-15', 25, 180),
  (3, '2025-04-16', 50, 180),
  (3, '2025-04-17', 5, 180);
-- 6E305: Bangalore to Delhi
INSERT INTO flight_seats (flight_id, travel_date, available_seats, max_seats)
VALUES
  (2, '2025-04-15', 60, 180),
  (2, '2025-04-16', 90, 180),
  (2, '2025-04-17', 10, 180);
update train_seats set travel_date='2025-04-15' where train_id = 102;
select * from users;
select * from trains;
select * from train_routes;
select * from buses;
select * from bus_seats;
select * from bus_routes;
select * from flight_routes;
select * from flight_fares;
select * from flights;
select * from flight_seats;
select * from cabs;
select * from fares;
select * from passengers;
select * from journey_segments;
select * from payment;
select * from unified_locations;
update unified_locations set airport_code = 'BLR' where location_id =14;
select train_number, train_id, price, password from trains;
SHOW TABLES;
drop table flights;
SET SQL_SAFE_UPDATES = 0;
delete from fares;

SET FOREIGN_KEY_CHECKS = 0;
DELETE FROM unified_stations;
SET FOREIGN_KEY_CHECKS = 1;
