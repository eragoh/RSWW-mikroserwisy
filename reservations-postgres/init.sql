CREATE TABLE RESERVATIONS (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    trip VARCHAR(255),
    price FLOAT,
    room VARCHAR(255),
    paid BOOLEAN,
    adults INTEGER,
    ch3 INTEGER,
    ch10 INTEGER,
    ch18 INTEGER,
    CONSTRAINT unique_trip_room UNIQUE(trip, room)
);
