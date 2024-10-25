import psycopg2
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from psycopg2 import sql
from dbmanager.dbmanager import db_params, create_answer_table, insert_answer, get_current_answer_fromSQL
from answer.get_round_data import get_round_data

def fetch_and_insert(connection, roundId):
    flag = True
    while flag:
        try:
            roundData = get_round_data(roundId)
            if roundData[2] != 0:
                try:
                    insert_answer(connection, roundData)
                    flag = False
                    print(f"Successfully inserted data for roundId: {roundId}")
                except Exception as e:
                    flag = True
                    print(f"Failed to insert data for roundId: {roundId}. Error: {e}")
        except Exception as e:
            flag = True
            print(f"Failed to fetch data for roundId: {roundId}. Error: {e}")

def main():
    connection = psycopg2.connect(**db_params)
    print("Connected to the database successfully.")

    create_answer_table(connection)

    # roundId = 55340232221128654849
    # roundId = 55340232221129180749
    roundId = get_current_answer_fromSQL(connection) - 10
    num_threads = 50

    while True:
        futures = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for i in range(num_threads):
                futures.append(executor.submit(fetch_and_insert, connection, roundId + i))
            # for future in as_completed(futures):
            #     print(future.result())
        roundId += num_threads
        time.sleep(5)

if __name__ == "__main__":
    main()
