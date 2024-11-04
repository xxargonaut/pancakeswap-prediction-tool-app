import { Client } from 'pg';

const dbParams = {
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: parseInt(process.env.DB_PORT || '5432'),
};

export async function POST() {
  const client = new Client(dbParams);
  try{
    // Connect to the database
    await client.connect();
    console.log('Connected to the database successfully.');

    const get_current_epoch_query = "SELECT * FROM Epoch ORDER BY epoch DESC LIMIT 1;";
    const current_epoch_result = await client.query(get_current_epoch_query);
    const current_epoch = current_epoch_result.rows[0].epoch;

    const get_states_query = `SELECT epoch, value FROM Betting WHERE state IS NULL AND epoch <= ${current_epoch} ORDER BY epoch ASC;`;
    const get_states_result = await client.query(get_states_query);
    const get_states = get_states_result.rows;

    if(get_states.length == 0)
        return new Response(JSON.stringify({ notice: 'There is no epoch data to check betting results!' }), {
            status: 201,
            headers: {
                'Content-Type': 'application/json',
            },
        });
    for(var i = 0; i < get_states.length; i++){
        const get_epoch_data_query = `SELECT lockPrice FROM Epoch WHERE epoch IN (${get_states[i].epoch - 1}, ${get_states[i].epoch}) ORDER BY epoch ASC;`;
        const get_epoch_data_result = await client.query(get_epoch_data_query);
        const epoch_data = get_epoch_data_result.rows;

        const verify = ((epoch_data[1].lockprice > epoch_data[0].lockprice) == get_states[i].value);

        const update_query = `UPDATE Betting SET state = ${verify} WHERE epoch = ${get_states[i].epoch};`

        await client.query(update_query);
    }

    return new Response(JSON.stringify({ message: 'Betting result verification has been successfully completed.' }), {
        status: 200,
        headers: {
            'Content-Type': 'application/json',
        },
    });
  } catch (error) {
    console.error("Error fetching current answer data from database:", error);
    return new Response(JSON.stringify({ error: 'Failed to verify betting data' }), {
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
