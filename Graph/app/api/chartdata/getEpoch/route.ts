// app/api/chartdata/getEpoch/route.ts
import { Client } from 'pg';

const dbParams = {
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: parseInt(process.env.DB_PORT || '5432'),
};

export async function GET(request: Request) {
    // Create a new PostgreSQL client
  const client = new Client(dbParams);

  try {
    // Parse query parameters
    const url = new URL(request.url);
    const dateLength = parseInt(url.searchParams.get('dateLength') || '0');
    const numberOfPrevPage = parseInt(url.searchParams.get('numberOfPrevPage') || '0');

    // Connect to the database
    await client.connect();

    console.log('Connected to the database successfully.');

    const get_current_answer_query = 'SELECT * FROM Answer ORDER BY startedat DESC LIMIT 1;';
    const current_answer_result = await client.query(get_current_answer_query);

    // Check if the result contains any data
    if (current_answer_result.rows.length === 0) {
      return new Response(JSON.stringify({ error: 'No data found' }), {
        status: 404,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    }

    const current_epoch_locktime = current_answer_result.rows[0].startedat

    const epoch_query = `SELECT lockTimestamp, lockPrice FROM Epoch WHERE lockTimestamp BETWEEN ${current_epoch_locktime - (numberOfPrevPage + 1) * dateLength} AND ${current_epoch_locktime - numberOfPrevPage * dateLength} ORDER BY lockTimestamp ASC;`;

    const epoch_result = await client.query(epoch_query);
    const rows = epoch_result.rows || [];
    const return_data = rows.map((row) => ({
        colC: row.locktimestamp,
        colD: row.lockprice,
    }));
    
    return new Response(JSON.stringify(return_data), {
        status: 200,
        headers: {
            'Content-Type': 'application/json',
        },
    });
  } catch (error) {
        console.error("Error fetching Google Sheets data:", error);
        return new Response(JSON.stringify({ error: 'Failed to load data' }), {
            status: 500,
            headers: {
                'Content-Type': 'application/json',
            },
        });
  } finally {
    await client.end(); // Close the connection
    console.log('Closed to the database successfully.');
  }
}
