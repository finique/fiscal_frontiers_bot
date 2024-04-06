import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float
from fmp_api import get_company_peers, get_stock_data, get_peers_multiples

from dotenv import load_dotenv
import os
load_dotenv()

def create_table_from_dataframe(df, table_name):
    """
    Function to create a SQLAlchemy table object based on the DataFrame columns.
    
    Args:
        df (DataFrame): The DataFrame containing the data.
        table_name (str): The name of the table to be created.
    
    Returns:
        Table: The SQLAlchemy Table object.
    """
    metadata = MetaData()
    columns = [Column(col, get_sqlalchemy_type(df[col])) for col in df.columns]
    table = Table(table_name, metadata, *columns)
    return table

def get_sqlalchemy_type(series):
    """
    Function to get the corresponding SQLAlchemy type based on the data type of the series.
    
    Args:
        series: A pandas Series.
    
    Returns:
        SQLAlchemy type: The corresponding SQLAlchemy type.
    """
    if series.dtype == 'int64':
        return Integer
    elif series.dtype == 'float64':
        return Float
    else:
        return String

from sqlalchemy import create_engine, MetaData
import pandas as pd

def create_stock_tables(ticker, add_historical_price = 0, delete_existing_tables=0, add_comp_table=0, add_multiple_table=0):
    """
    Function to create tables in the database for the given ticker symbol's stock data.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        delete_existing_tables (int): If set to 1, existing tables will be deleted.
        delete_comp_table (int): If set to 1, the comp table will be deleted.
    """
    # Your Neon connection details
    USERNAME = os.getenv('Neon_USERNAME')
    PASSWORD = os.getenv('Neon_PASSWORD')
    HOST = os.getenv('Neon_HOST')
    DATABASE = os.getenv('Neon_DATABASE')

    # Construct the connection string
    conn_str = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}?sslmode=require'
    
    # Create SQLAlchemy engine
    engine = create_engine(conn_str)
    
    # Reflect database schema to get existing table names
    metadata = MetaData()
    metadata.reflect(bind=engine)
    existing_tables = metadata.tables.keys()
    
    # Delete existing table if delete_existing_tables is set to 1
    if delete_existing_tables == 1:
        for table_name in existing_tables:
            if table_name in metadata.tables:
                print(f"Dropping table: {table_name}")
                metadata.tables[table_name].drop(engine)
            else:
                print(f"Table {table_name} does not exist and cannot be dropped.")
    

    if add_historical_price == 1:
        # Fetching stock data
        stock_data = get_stock_data(ticker)

        # Define table name
        table_name = ticker.lower()  # Using lowercase ticker symbol as table name
        
        # Create table dynamically
        table = create_table_from_dataframe(stock_data, table_name)

        # Create table in the database
        table.create(engine)
        
        # Commit the DataFrame to the database
        try:
            stock_data.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Table {table_name} created and data committed successfully!")
        except Exception as e:
            print(f"Error committing DataFrame to database: {e}")

    # Create a comp table if add_comp_table is set to 1
    if add_comp_table == 1:
        comp_data = get_company_peers(ticker)
        comp_data = pd.DataFrame(comp_data, columns=['Competitor Ticker'])

        # Define table name
        table_name = '{}_comp_list'.format(ticker.lower())  # Using lowercase ticker symbol as table name
        
        # Create table dynamically
        table = create_table_from_dataframe(comp_data, table_name)

        # Create table in the database
        table.create(engine)
        
        # Commit the DataFrame to the database
        try:
            comp_data.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Table {table_name} created and data committed successfully!")
        except Exception as e:
            print(f"Error committing DataFrame to database: {e}")


    # Create a multiples comparison table if add_multiple_table is set to 1
    if add_multiple_table == 1:
        comp_data = get_peers_multiples(ticker)

        # Define table name
        table_name = '{}_multiple_comp'.format(ticker.lower())  # Using lowercase ticker symbol as table name
        
        # Create table dynamically
        table = create_table_from_dataframe(comp_data, table_name)

        # Create table in the database
        table.create(engine)
        
        # Commit the DataFrame to the database
        try:
            comp_data.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"Table {table_name} created and data committed successfully!")
        except Exception as e:
            print(f"Error committing DataFrame to database: {e}")


def retrieve_stock_data(ticker, historical_price = 0, comps = 0, multiples = 0):
    """
    Function to retrieve data from the database table for the specified ticker symbol.
    
    Args:
        ticker (str): The ticker symbol of the stock.
    
    Returns:
        DataFrame: DataFrame containing the retrieved data.
    """
    # Your Neon connection details
    USERNAME = os.getenv('Neon_USERNAME')
    PASSWORD = os.getenv('Neon_PASSWORD')
    HOST = os.getenv('Neon_HOST')
    DATABASE = os.getenv('Neon_DATABASE')

    # Construct the connection string
    conn_str = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}?sslmode=require'
    
    # Create SQLAlchemy engine
    engine = create_engine(conn_str)

    # Define table name
    table_name = ticker.lower()  # Using lowercase ticker symbol as table name
    
    if historical_price == 1:    
        # Query to retrieve data from the table
        query = f"SELECT date, close FROM {table_name};"

    if comps == 1:   
    # Query to retrieve data from the table
        query = f"SELECT * FROM {table_name}{'_comp_list'};"
    # Execute the query and fetch data into a DataFrame
        
    if multiples == 1:   
    # Query to retrieve data from the table
        query = f"SELECT * FROM {table_name}{'_multiple_comp'};"
    # Execute the query and fetch data into a DataFrame
        
    try:
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        print(f"Error retrieving data from database: {e}")
        return pd.DataFrame()