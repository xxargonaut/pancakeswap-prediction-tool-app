// app/api/currentAnswerTime/route.ts
import { Client } from 'pg';

// Database connection parameters using environment variables
const dbParams = {
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: parseInt(process.env.DB_PORT || '5432'),
};

export async function GET() {
  const client = new Client(dbParams);

  try {
    // Connect to the database
    await client.connect();
    console.log('Connected to the database successfully.');

    const get_bettingData_query = `SELECT * FROM Betting ORDER BY epoch ASC;`;
    const bettingData_result = await client.query(get_bettingData_query);
    const betting_rows = bettingData_result.rows || [];

    const get_states = `SELECT * FROM Betting WHERE state IS NULL;`;
    const states_result = await client.query(get_states);
    const states_rows = states_result.rows || [];

    const return_data = {
      bettingData: betting_rows,
      bettingStates: states_rows.length
    }
    return new Response(JSON.stringify(return_data), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error("Error fetching current answer data from database:", error);
    return new Response(JSON.stringify({ error: 'Failed to load data' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } finally {
    // Ensure the database connection is closed
    await client.end();
    console.log('Closed to the database successfully.');
  }
}
