import psycopg2
from psycopg2 import sql

def get_connection():
    connection = psycopg2.connect(
        dbname="travel",
        user="postgres",
        password="postgres",
        host="180140_postgres-db-reservations"
    )
    return connection

def add_reservation(username, trip, price, paid):
    try:
        # Ustanów połączenie z bazą danych
        connection = get_connection()
        cursor = connection.cursor()

        # Wykonaj zapytanie SQL do dodania rezerwacji
        cursor.execute(
            """
            INSERT INTO RESERVATIONS (username, trip, price, paid) 
            VALUES (%s, %s, %s, %s)
            """,
            (username, trip, price, paid)
        )

        # Zatwierdź zmiany
        connection.commit()
        print("Rezerwacja dodana pomyślnie!")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Błąd podczas dodawania rezerwacji:", error)

    finally:
        # Zamknij połączenie
        if connection:
            cursor.close()
            connection.close()

def remove_reservation(trip):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM RESERVATIONS 
            WHERE trip = %s
            """,
            (trip,)
        )
        connection.commit()
        print("Rezerwacje dla wycieczki {} usunięte pomyślnie!".format(trip))

    except (Exception, psycopg2.DatabaseError) as error:
        print("Błąd podczas usuwania rezerwacji:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

def select_reservations_by_username(username):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM reservations WHERE username = %s;", (username,))
        results = cursor.fetchall()
        return results

    except (Exception, psycopg2.DatabaseError) as error:
        print("Błąd podczas wykonywania zapytania SQL:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()

def delete_unpaid_reservations():
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM reservations WHERE paid = false;")
        connection.commit()
        print("Usunięto wszystkie nieopłacone rezerwacje.")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Błąd podczas usuwania nieopłaconych rezerwacji:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()


add_reservation("jan_kowalski", "Wakacje w Egipcie", 1500.10, True)
add_reservation("jan_kowalski", "WakaDDcje w Egipcie", 1300.14, True)
add_reservation("usernfnsdf", "dfsfsdfsdfsdfsdf", 3500.0, False)

remove_reservation("usernfnsdf")

delete_unpaid_reservations()

reservations = select_reservations_by_username('jan_kowalski')
if reservations:
    for reservation in reservations:
        print(reservation)
