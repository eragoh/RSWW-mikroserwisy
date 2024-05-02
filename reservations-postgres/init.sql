CREATE TABLE RESERVATIONS (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    trip VARCHAR(255) UNIQUE,
    price FLOAT,
    paid BOOLEAN
);
