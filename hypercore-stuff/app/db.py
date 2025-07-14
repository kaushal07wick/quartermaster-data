import psycopg2
from psycopg2.extras import execute_values
from app.logger import get_logger
from app.config import DB_CONFIG

logger = get_logger(__name__)

def get_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG["NAME"],
        user=DB_CONFIG["USER"],
        password=DB_CONFIG["PASSWORD"],
        host=DB_CONFIG["HOST"],
        port=DB_CONFIG["PORT"]
    )

def reset_wallet_analysis_table():
    """
    Drops the wallet_analysis table if it exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DROP TABLE IF EXISTS wallet_analysis;')
        conn.commit()
        logger.info("✅ Dropped wallet_analysis table.")
    except Exception as e:
        logger.error(f"❌ Error dropping wallet_analysis table: {e}")
    finally:
        cursor.close()
        conn.close()

def setup_database():
    """
    Creates the wallet_analysis table with the latest schema.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallet_analysis (
                id SERIAL PRIMARY KEY,
                wallet_address TEXT UNIQUE,
                total_aum REAL,
                hype REAL,
                usdc REAL,
                memecoins REAL,
                average_txn_amount REAL
            );
        ''')
        conn.commit()
        logger.info("✅ Database setup completed with updated schema.")
    except Exception as e:
        logger.error(f"❌ Error setting up database: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_wallet_analysis(data: dict):
    """
    Inserts parsed wallet analysis data into the database.
    Updates existing wallet if already present.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        required_fields = ["wallet", "total_aum", "hype_amount", "usdc_amount", "memecoin_amount", "average_txn_amount"]
        if not all(field in data for field in required_fields):
            logger.error(f"❌ Data for wallet {data.get('wallet', 'Unknown')} is missing required fields.")
            return

        # Prepare the data as a tuple
        values = (
            data["wallet"],
            data["total_aum"],
            data["hype_amount"],
            data["usdc_amount"],
            data["memecoin_amount"],
            data["average_txn_amount"]
        )

        cursor.execute('''
            INSERT INTO wallet_analysis (
                wallet_address, total_aum, hype, usdc, memecoins, average_txn_amount
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (wallet_address) DO UPDATE SET
                total_aum = EXCLUDED.total_aum,
                hype = EXCLUDED.hype,
                usdc = EXCLUDED.usdc,
                memecoins = EXCLUDED.memecoins,
                average_txn_amount = EXCLUDED.average_txn_amount;
        ''', values)

        conn.commit()
        logger.info(f"✅ Inserted/Updated data for wallet {data['wallet']}")
    except Exception as e:
        logger.error(f"❌ Error inserting data for wallet {data.get('wallet', 'Unknown')}: {e} | Data: {data}")
    finally:
        cursor.close()
        conn.close()