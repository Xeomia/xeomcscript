from mysql.connector import connect, Error
import time


def create_db(player_name, connection_info):
    """
    Creates player database
    Returns True if successfull or already existing, otherwise returns False and prints error

    :param player_name: <str> Player IGN
    :param connection_info: <dict> Format expected (example) {'host' : 'localhost', 'user' : 'root', 'password' : '12345'}
    """

    with connect(host=connection_info['host'],\
                 user=connection_info['user'], \
                 password=connection_info['password']) as connection:

        with connection.cursor() as cursor:
            try:
                cursor.execute(f'CREATE DATABASE {player_name};')
                return True

            except Error as e:

                if 'database exists' in e.args[1]:
                    return True
                else:
                    print(e)
                    return False


def add_null(amount, table_name, column_name, connection_info):
    """
    Adds the asked amount of null entries to table_name to all given column_name

    :param amount: <int>
    :param table_name: <str>
    :param column_name: <str> Column Name
    :param connection_info: <dict> Format expected (example) {'host' : 'localhost', 'user' : 'root', 'password' : '12345', 'database' : 'RandomIGN'}
    """

    add_null_entry_query = f'INSERT INTO {table_name} ({column_name}) VALUES (null);'.replace("'", "")

    with connect(host=connection_info['host'],\
                 user=connection_info['user'], \
                 password=connection_info['password'], \
                 database=connection_info['database']) as connection:

        with connection.cursor() as cursor:

            for _ in range(amount):
                cursor.execute(add_null_entry_query)
            connection.commit()


def create_reset_table(player_name, table_name, connection_info):
    """
    Creates inventory and hotbar tables in the given player database, 
    calls add_null() to fill them with null entries.
    Returns True if successfull or already exists, otherwise returns False and prints error

    :param player_name: <str> Player IGN
    :param table_name: <str> Specific table created for a specific server
    :param connection_info: <dict> Format expected (example) {'host' : 'localhost', 'user' : 'root', 'password' : '12345'}
    """

    create_inv_table_query = f"""CREATE TABLE {table_name}_inventory(
        slot TINYINT AUTO_INCREMENT PRIMARY KEY,
        item_name VARCHAR(50),
        amount TINYINT);""".replace("'", "")

    create_hotbar_table_query = f"""CREATE TABLE {table_name}_hotbar(
        slot TINYINT AUTO_INCREMENT PRIMARY KEY,
        amount TINYINT);""".replace("'", "")

    auto_increment_inv_query = f"ALTER TABLE {table_name}_inventory AUTO_INCREMENT = 1;".replace("'", "")

    auto_increment_htbar_query = f"ALTER TABLE {table_name}_hotbar AUTO_INCREMENT = 1;".replace("'", "")

    if not create_db(player_name, connection_info):

        print('Database not created successfully')
        return False

    with connect(host=connection_info['host'],\
                 user=connection_info['user'], \
                 password=connection_info['password'], \
                 database=player_name) as connection:

        with connection.cursor() as cursor:
            
            #--- Delete existing table ---#
            try:
                cursor.execute(f"DROP TABLE {table_name}_hotbar;".replace("'", ""))
                cursor.execute(f"DROP TABLE {table_name}_inventory;".replace("'", ""))
                connection.commit()
            
            except Error as e:
                if not "Unknown table" in e.args[1]: #Other error than non existing table
                    print(e)
                    return False

            try:
                cursor.execute(create_inv_table_query)
                cursor.execute(auto_increment_inv_query)
                cursor.execute(create_hotbar_table_query)
                cursor.execute(auto_increment_htbar_query)
            
            except Error as e:

                if not 'already exists' in e.args[1]: #Other errors than already existing table
                    print(e)
                    return False
            
            co_info = {'host' : 'localhost', \
                       'user' : 'root', \
                       'password' : 'SQL222ptD222', \
                       'database' : player_name}

            #-- Add Null To show used slots ---#
            add_null(9, f'{table_name}_hotbar', 'amount', co_info)
            add_null(41, f'{table_name}_inventory', 'amount', co_info) #By default, adds null values in other non-specified columns
            connection.commit()
    
    return True #Everything worked
