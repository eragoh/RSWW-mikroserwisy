CREATE TABLE OPERATION (
    id SERIAL PRIMARY KEY,
    trip VARCHAR(255),
    room_is_standard INTEGER,
    room_is_family INTEGER,
    room_is_apartment INTEGER,
    room_is_studio INTEGER,
    price INTEGER,
    adults INTEGER,
    children_under_3 INTEGER,
    children_under_10 INTEGER,
    children_under_18 INTEGER
);
