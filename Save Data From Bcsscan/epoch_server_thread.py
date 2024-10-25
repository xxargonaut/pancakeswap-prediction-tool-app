import psycopg2
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2 import sql
from dbmanager.dbmanager import db_params, create_epoch_table, insert_epoch
from epoch.get_rounds import get_rounds
from epoch.get_current_epoch import get_current_epoch

def process_epoch(connection, index, current_epoch):
    flag = True
    while flag:
        try:
            rounds = get_rounds(index)
            oracle_called = rounds[13]
            if index + 5 < current_epoch or oracle_called:
                try:
                    insert_epoch(connection, rounds)
                    flag = False
                    print(f"Successfully inserted data for index: {index}")
                except Exception as e:
                    flag = True
                    print(f"Failed to insert data for index: {index}. Error: {e}")
            else:
                flag = True
                print(f"Skipping index {index} because conditions are not met.")
        except Exception as e:
            flag =  True
            print(f"Failed to fetch data for index {index}. Error: {e}")

def main():
    connection = psycopg2.connect(**db_params)
    print("Connected to the database successfully.")

    create_epoch_table(connection)

    # index = 298826
    index = 308831
    num_threads = 5

    while True:
        try:
            current_epoch = int(get_current_epoch())
            futures = []

            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                for i in range(num_threads):
                    futures.append(executor.submit(process_epoch, connection, index + i, current_epoch))

            index += num_threads

        except Exception as e:
            print(f"Failed to fetch current epoch: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()
