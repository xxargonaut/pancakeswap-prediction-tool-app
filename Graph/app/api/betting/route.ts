import { Client } from 'pg';

const dbParams = {
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: parseInt(process.env.DB_PORT || '5432'),
};

export async function POST(request: Request) {
    const client = new Client(dbParams);
    const { to, length, option, value } = await request.json();

    try {
        await client.connect();
        console.log('Connected to the database successfully.');

        const epoch_query = `
            SELECT epoch FROM Epoch
            WHERE lockTimestamp BETWEEN $1 AND $2
            ORDER BY lockTimestamp ASC;
        `;
        const epoch_result = await client.query(epoch_query, [to - length, to]);
        const rows = epoch_result.rows || [];

        const epoch = Number(rows[rows.length - option - 1].epoch) + 1;

        try {
            const check_query = `SELECT 1 FROM Betting WHERE epoch = $1;`;
            const insert_bet_query = `
                INSERT INTO Betting (epoch, betting_flag)
                VALUES ($1, $2);
            `;
            
            const check_result = await client.query(check_query, [epoch]);
            if (check_result.rowCount === 0) {
                await client.query(insert_bet_query, [epoch, value]);

                return new Response(JSON.stringify({ message: 'Betting data saved successfully.' }), {
                    status: 200,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
            } else {
                console.log('Betting data for this epoch already exists.');
                return new Response(JSON.stringify({ error: 'Betting data for this epoch already exists.' }), {
                    status: 409,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
            }

        } catch (error) {
            console.error('Error saving betting data:', error);
            return new Response(JSON.stringify({ error: 'Failed to save betting data' }), {
                status: 500,
                headers: {
                    'Content-Type': 'application/json',
                },
            });
        }

    } catch (error) {
        console.error("Error loading data from database:", error);
        return new Response(JSON.stringify({ error: 'Failed to load data' }), {
            status: 500,
            headers: {
                'Content-Type': 'application/json',
            },
        });
    } finally {
        await client.end();
        console.log('Closed the database connection successfully.');
    }
}
