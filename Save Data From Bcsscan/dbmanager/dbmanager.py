import psycopg2
from psycopg2 import sql

db_params = {
    'dbname': 'bcsscandata',
    'user': 'postgres',
    'password': '12345678',
    'host': 'localhost',
    'port': '5432'
}

def create_epoch_table(connection):
    with connection.cursor() as cursor:
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS Epoch (
            epoch NUMERIC(78, 0) PRIMARY KEY,
            startTimestamp BIGINT,
            lockTimestamp BIGINT,
            closeTimestamp BIGINT,
            lockPrice NUMERIC(78, 0),
            closePrice NUMERIC(78, 0),
            lockOracleId NUMERIC(78, 0),
            closeOracleId NUMERIC(78, 0),
            totalAmount NUMERIC(78, 0),
            bullAmount NUMERIC(78, 0),
            bearAmount NUMERIC(78, 0),
            rewardBaseCalAmount NUMERIC(78, 0),
            rewardAmount NUMERIC(78, 0),
            oracleCalled BOOLEAN
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Epoch table checked/created successfully.")

def create_answer_table(connection):
    with connection.cursor() as cursor:
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS Answer (
            roundId NUMERIC(78, 0) PRIMARY KEY,
            answer NUMERIC(78, 0),
            startedAt BIGINT,
            updatedAt BIGINT,
            answeredInRound NUMERIC(78, 0)
        );
        '''
        cursor.execute(create_table_query)
        connection.commit()
        print("Answer table checked/created successfully.")
        
def insert_epoch(connection, epochData):
    with connection.cursor() as cursor:
        insert_query = '''
        INSERT INTO Epoch (epoch, startTimestamp, lockTimestamp, closeTimestamp, lockPrice, closePrice, lockOracleId, closeOracleId, totalAmount, bullAmount, bearAmount, rewardBaseCalAmount, rewardAmount, oracleCalled)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (epoch) DO NOTHING;
        '''
        cursor.execute(insert_query, (epochData[0], epochData[1], epochData[2], epochData[3], epochData[4], epochData[5], epochData[6], epochData[7], epochData[8], epochData[9], epochData[10], epochData[11], epochData[12], epochData[13]))
        connection.commit()

def insert_answer(connection, roundData):
    with connection.cursor() as cursor:
        insert_query = '''
        INSERT INTO Answer (roundId, answer, startedAt, updatedAt, answeredInRound)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (roundId) DO NOTHING;
        '''
        cursor.execute(insert_query, (roundData[0], roundData[1], roundData[2], roundData[3], roundData[4]))
        connection.commit()
        
def get_current_epoch_fromSQL(connection):
    with connection.cursor() as cursor:
        insert_query = "SELECT * FROM Epoch ORDER BY epoch DESC LIMIT 1;"
        cursor.execute(insert_query)
        current_epoch_result = cursor.fetchone()
        current_epoch_startedat = int(current_epoch_result[0])
        return current_epoch_startedat
         
def get_current_answer_fromSQL(connection):
    with connection.cursor() as cursor:
        insert_query = "SELECT * FROM Answer ORDER BY roundid DESC LIMIT 1;"
        cursor.execute(insert_query)
        current_answer_result = cursor.fetchone()
        current_answer_startedat = int(current_answer_result[0])
        return current_answer_startedat