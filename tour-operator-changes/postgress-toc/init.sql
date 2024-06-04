CREATE TABLE OPERATION (
    id SERIAL PRIMARY KEY,
    trip VARCHAR(255),
    room VARCHAR(255),
    CONSTRAINT unique_trip_room UNIQUE(trip, room)
);
