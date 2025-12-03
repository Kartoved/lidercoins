import sqlite3

connection = sqlite3.connect("lidercoins.db")
c = connection.cursor()

# c.execute(
#     """CREATE TABLE IF NOT EXISTS lidercoins (
#     full_name TEXT,
#     number_of_coins INTEGER
#     )
# """
# )

# удалить ученика
# c.execute("Delete from lidercoins where full_name = 'Волков Михаил'")

# добавить ученика
# c.execute(
#     """INSERT INTO lidercoins (full_name, number_of_coins) VALUES ('Чеча Георгий', 50) """
# )

# c.execute("ALTER TABLE lidercoins ADD days TUPLE")
c.execute(
    "UPDATE lidercoins SET days = ? WHERE full_name = ?",
    ([0, 3], "Саша Уланова"),
)
connection.commit()
connection.close()
