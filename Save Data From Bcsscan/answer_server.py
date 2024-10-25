import psycopg2
import time
from psycopg2 import sql
from dbmanager.dbmanager import db_params, create_answer_table, insert_answer, get_current_answer_fromSQL
from answer.get_round_data import get_round_data

def main():
    connection = psycopg2.connect(**db_params)
    print("Connected to the database successfully.")

    create_answer_table(connection)

    # roundId = 55340232221128654849
    roundId = get_current_answer_fromSQL(connection) + 1
    while True:
        try:
            roundData = get_round_data(roundId)
            if(roundData[2] != 0):
                try:
                    insert_answer(connection, roundData)
                    print(f"Successfully inserted data for roundId: {roundId}")
                    roundId += 1
                except Exception as e:
                    print(f"Failed to insert the data to answer table: {e}")
            else:
                print(f"Start counting down 10 seconds")
                time.sleep(9)
        except Exception as e:
            print(f"Failed to fetch getRoundData: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    main()