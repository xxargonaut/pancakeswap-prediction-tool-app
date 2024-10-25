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

    const get_difference_query = `
      SELECT 
          MAX(startedat) AS max_startedat, 
          MIN(startedat) AS min_startedat 
      FROM Answer;
      `;
    const difference_result = await client.query(get_difference_query);

    // Check if the result contains any data
    if (difference_result.rows.length === 0) {
        return new Response(JSON.stringify({ error: 'No data found' }), {
            status: 404,
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }
    const { max_startedat, min_startedat } = difference_result.rows[0];
    const time_width = max_startedat - min_startedat;

    const return_data = {
      time_width: time_width,
      current_timestamp: max_startedat,
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
