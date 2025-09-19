#!/usr/bin/env python3
"""
Database Setup Script
Initializes PostgreSQL database for the fraud detection system
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create the fraud detection database"""
    
    # Database connection parameters
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', 'fraud_detection_db')
    db_user = os.getenv('DATABASE_USER', 'postgres')
    db_password = os.getenv('DATABASE_PASSWORD', 'password')
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        logger.info(f"Connecting to PostgreSQL server at {db_host}:{db_port}")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if exists:
            logger.info(f"Database '{db_name}' already exists")
        else:
            # Create the database
            logger.info(f"Creating database '{db_name}'")
            cursor.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Database '{db_name}' created successfully")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Error creating database: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def run_sql_script():
    """Run the database setup SQL script"""
    
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', 'fraud_detection_db')
    db_user = os.getenv('DATABASE_USER', 'postgres')
    db_password = os.getenv('DATABASE_PASSWORD', 'password')
    
    try:
        # Connect to the fraud detection database
        logger.info(f"Connecting to database '{db_name}'")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Read and execute the SQL setup script
        sql_file_path = os.path.join(os.path.dirname(__file__), 'database_setup.sql')
        
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL setup file not found: {sql_file_path}")
            return False
        
        logger.info("Executing database setup script...")
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
            
            # Split script into individual statements
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        cursor.execute(statement)
                        conn.commit()
                    except psycopg2.Error as e:
                        if "already exists" in str(e):
                            logger.info(f"Skipping existing object: {str(e)}")
                            conn.rollback()
                        else:
                            logger.error(f"Error executing statement: {e}")
                            conn.rollback()
                            raise
        
        logger.info("Database setup completed successfully")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def verify_setup():
    """Verify that the database setup is correct"""
    
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', 'fraud_detection_db')
    db_user = os.getenv('DATABASE_USER', 'postgres')
    db_password = os.getenv('DATABASE_PASSWORD', 'password')
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Check if tables exist
        required_tables = ['users', 'transactions', 'fraud_assessments', 'fraud_rules']
        
        for table in required_tables:
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                )
            """)
            exists = cursor.fetchone()[0]
            
            if exists:
                # Count records in table
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"✓ Table '{table}' exists with {count} records")
            else:
                logger.error(f"✗ Table '{table}' does not exist")
                return False
        
        cursor.close()
        conn.close()
        
        logger.info("Database verification completed successfully")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Database verification error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}")
        return False

def main():
    """Main setup function"""
    
    logger.info("=== Fraud Detection System Database Setup ===")
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        logger.warning("No .env file found. Please copy .env.example to .env and configure your database settings.")
        logger.info("Using default database settings...")
    
    # Step 1: Create database
    logger.info("Step 1: Creating database...")
    if not create_database():
        logger.error("Failed to create database. Please check your PostgreSQL connection settings.")
        sys.exit(1)
    
    # Step 2: Run SQL setup script
    logger.info("Step 2: Setting up database schema...")
    if not run_sql_script():
        logger.error("Failed to set up database schema.")
        sys.exit(1)
    
    # Step 3: Verify setup
    logger.info("Step 3: Verifying database setup...")
    if not verify_setup():
        logger.error("Database verification failed.")
        sys.exit(1)
    
    logger.info("=== Database setup completed successfully! ===")
    logger.info("You can now start the fraud detection system with: python main.py")

if __name__ == "__main__":
    main()
