-- CineplexxDB Sample Data for PostgreSQL

-- Cinema
INSERT INTO cinema (cinema_id, location, name) VALUES
(1, 'Tirana', 'Cineplexx TEG'),
(2, 'Tirana', 'Cineplexx City Park'),
(3, 'Durres', 'Cineplexx Durres')
ON CONFLICT DO NOTHING;

-- Department
INSERT INTO department (department_id, department_name) VALUES
(1, 'Management'),
(2, 'Box Office'),
(3, 'Concessions'),
(4, 'Projection'),
(5, 'Maintenance'),
(6, 'Security')
ON CONFLICT DO NOTHING;

-- Customer
INSERT INTO customer (customer_id, full_name, phone_number, email, date_of_birth, gender) VALUES
(1, 'Arben Hoxha', '+355691234567', 'arben.hoxha@email.com', '1990-05-15', 'Male'),
(2, 'Maria Koci', '+355692345678', 'maria.koci@email.com', '1985-08-22', 'Female'),
(3, 'Dritan Leka', '+355693456789', 'dritan.leka@email.com', '1992-03-10', 'Male'),
(4, 'Elena Brahimi', '+355694567890', 'elena.brahimi@email.com', '1988-12-01', 'Female'),
(5, 'Besnik Shehu', '+355695678901', 'besnik.shehu@email.com', '1995-07-25', 'Male')
ON CONFLICT DO NOTHING;

-- Genre
INSERT INTO genre (genre_id, genre_name) VALUES
(1, 'Action'),
(2, 'Comedy'),
(3, 'Drama'),
(4, 'Horror'),
(5, 'Science Fiction'),
(6, 'Romance'),
(7, 'Thriller'),
(8, 'Animation'),
(9, 'Adventure'),
(10, 'Fantasy')
ON CONFLICT DO NOTHING;

-- Hall
INSERT INTO hall (hall_id, hall_name, capacity, cinema_id) VALUES
(1, 'Hall A - IMAX', 200, 1),
(2, 'Hall B - Premium', 150, 1),
(3, 'Hall C - Standard', 120, 1),
(4, 'Hall D - Standard', 120, 2),
(5, 'Hall E - VIP', 50, 2)
ON CONFLICT DO NOTHING;

-- Food
INSERT INTO food (food_id, food_name, price) VALUES
(1, 'Small Popcorn', 350.00),
(2, 'Medium Popcorn', 500.00),
(3, 'Large Popcorn', 650.00),
(4, 'Small Soda', 200.00),
(5, 'Medium Soda', 300.00),
(6, 'Large Soda', 400.00),
(7, 'Hot Dog', 450.00),
(8, 'Nachos', 550.00)
ON CONFLICT DO NOTHING;

-- Movie
INSERT INTO movie (movie_id, title, duration, release_date, language, age_rating, adult_price, kids_price) VALUES
(1, 'The Dark Knight Returns', 152, '2025-06-15', 'English', 13, 800.00, 500.00),
(2, 'Love in Paris', 118, '2025-07-20', 'English', 12, 700.00, 450.00),
(3, 'Alien Invasion 3', 135, '2025-08-10', 'English', 16, 850.00, 550.00),
(4, 'Comedy Night', 95, '2025-09-01', 'English', 7, 600.00, 400.00),
(5, 'Frozen Dreams', 105, '2025-10-01', 'English', 0, 650.00, 450.00)
ON CONFLICT DO NOTHING;

-- Employee
INSERT INTO employee (employee_id, full_name, role, phone_number, email, date_of_birth, department_id, cinema_id) VALUES
(1, 'Robert Pasha', 'General Manager', '+355681111111', 'robert.p@cineplexx.al', '1975-03-15', 1, 1),
(2, 'Sara Kelmendi', 'Operations Manager', '+355682222222', 'sara.k@cineplexx.al', '1980-07-22', 1, 1),
(3, 'Tom Berisha', 'Floor Manager', '+355683333333', 'tom.b@cineplexx.al', '1985-11-10', 1, 2),
(4, 'Alba Hoti', 'Senior Cashier', '+355684444444', 'alba.h@cineplexx.al', '1992-05-18', 2, 1),
(5, 'Bujar Duka', 'Cashier', '+355685555555', 'bujar.d@cineplexx.al', '1995-08-25', 2, 1)
ON CONFLICT DO NOTHING;

-- Seat (Hall 1)
INSERT INTO seat (hall_id, seat_number, seat_row, seat_type) VALUES
(1, 1, 'A', 'Regular'), (1, 2, 'A', 'Regular'), (1, 3, 'A', 'Regular'), (1, 4, 'A', 'Regular'), (1, 5, 'A', 'Regular'),
(1, 1, 'B', 'Regular'), (1, 2, 'B', 'Regular'), (1, 3, 'B', 'Regular'), (1, 4, 'B', 'Regular'), (1, 5, 'B', 'Regular'),
(1, 1, 'C', 'VIP'), (1, 2, 'C', 'VIP'), (1, 3, 'C', 'VIP'), (1, 4, 'C', 'VIP'), (1, 5, 'C', 'VIP')
ON CONFLICT DO NOTHING;

-- Seat (Hall 2)
INSERT INTO seat (hall_id, seat_number, seat_row, seat_type) VALUES
(2, 1, 'A', 'VIP'), (2, 2, 'A', 'VIP'), (2, 3, 'A', 'VIP'), (2, 4, 'A', 'VIP'), (2, 5, 'A', 'VIP')
ON CONFLICT DO NOTHING;

-- Movie Genre
INSERT INTO movie_genre (movie_id, genre_id) VALUES
(1, 1), (1, 7),
(2, 6), (2, 2),
(3, 5), (3, 1),
(4, 2),
(5, 8), (5, 10)
ON CONFLICT DO NOTHING;

-- Showtime
INSERT INTO showtime (showtime_id, movie_id, hall_id, show_date, start_time, end_time) VALUES
(1, 1, 1, '2026-03-01', '10:00:00', '12:32:00'),
(2, 1, 1, '2026-03-01', '14:00:00', '16:32:00'),
(3, 2, 2, '2026-03-01', '11:00:00', '12:58:00'),
(4, 3, 1, '2026-03-02', '18:00:00', '20:15:00')
ON CONFLICT DO NOTHING;

-- Manager
INSERT INTO manager (employee_id, management_level, contract_type, hire_date) VALUES
(1, 1, 'Full-time', '2015-01-10'),
(2, 2, 'Full-time', '2017-03-15'),
(3, 3, 'Full-time', '2019-06-20')
ON CONFLICT DO NOTHING;

-- Cashier
INSERT INTO cashier (employee_id, shift_type, hire_date, employment_status) VALUES
(4, 'Morning', '2020-02-01', 'Active'),
(5, 'Afternoon', '2021-05-15', 'Active')
ON CONFLICT DO NOTHING;

-- Booking
INSERT INTO booking (booking_id, customer_id, showtime_id, booking_date, adult_seat, child_seat) VALUES
(1, 1, 1, '2026-02-28', 2, 0),
(2, 2, 3, '2026-02-28', 2, 1)
ON CONFLICT DO NOTHING;

-- Ticket
INSERT INTO ticket (ticket_id, booking_id, showtime_id, hall_id, seat_number, seat_row, ticket_price) VALUES
(1, 1, 1, 1, 1, 'A', 800.00),
(2, 1, 1, 1, 2, 'A', 800.00),
(3, 2, 3, 2, 1, 'A', 700.00),
(4, 2, 3, 2, 2, 'A', 700.00),
(5, 2, 3, 2, 3, 'A', 450.00)
ON CONFLICT DO NOTHING;

-- Food Order
INSERT INTO food_order (order_id, customer_id, order_date, order_time, order_amount) VALUES
(1, 1, '2026-03-01', '09:45:00', 1200.00),
(2, 2, '2026-03-01', '10:30:00', 950.00)
ON CONFLICT DO NOTHING;

-- Order Food
INSERT INTO order_food (order_id, food_id, quantity) VALUES
(1, 3, 1), (1, 6, 2),
(2, 2, 1), (2, 5, 1)
ON CONFLICT DO NOTHING;

-- Payment
INSERT INTO payment (payment_id, booking_id, order_id, payment_date, payment_time, amount, status, payment_method) VALUES
(1, 1, 1, '2026-03-01', '09:50:00', 2800.00, 'Completed', 'Card'),
(2, 2, 2, '2026-03-01', '10:35:00', 2800.00, 'Completed', 'Cash')
ON CONFLICT DO NOTHING;

-- Card Payment
INSERT INTO card_payment (payment_id, card_number, card_type, expiry_date, cardholder_name) VALUES
(1, '4532XXXXXXXX1234', 'Visa', '2028-05-01', 'Arben Hoxha')
ON CONFLICT DO NOTHING;

-- Cash Payment
INSERT INTO cash_payment (payment_id, change_amount) VALUES
(2, 200.00)
ON CONFLICT DO NOTHING;
