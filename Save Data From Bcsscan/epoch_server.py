import psycopg2
import time
from psycopg2 import sql
from dbmanager.dbmanager import db_params, create_epoch_table, insert_epoch, get_current_epoch_fromSQL
from epoch.get_rounds import get_rounds
from epoch.get_current_epoch import get_current_epoch

def main():
    connection = psycopg2.connect(**db_params)
    print("Connected to the database successfully.")

    create_epoch_table(connection)

    # index = 298826
    index = get_current_epoch_fromSQL(connection) + 1

    while True:
        try:
            current_epoch = int(get_current_epoch())
            try:
                rounds = get_rounds(index)
                lock_price = rounds[4]
                oracle_called = rounds[13]
                if index < current_epoch:
                    if lock_price > 0 and oracle_called:
                        try:
                            insert_epoch(connection, rounds)
                            print(f"Successfully inserted data for index: {index}")
                            index += 1
                        except Exception as e:
                            print(f"Failed to insert the data to epoch table: {e}")
                    else:
                        print(f"Start counting down 2.5 minutes")
                        time.sleep(149)
                else:
                    print(f"Start counting down 2.5 minutes")
                    time.sleep(149)
            except Exception as e:
                print(f"Failed to fetch index'th round data: {e}")
        except Exception as e:
            print(f"Failed to fetch currentEpoch: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
