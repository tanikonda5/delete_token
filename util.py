import configparser
import sys

import cx_Oracle
import pandas as pd


def collect_property_file_contents(property_file, account_name=None):
    """

     This method will attempt to open and load the property file to a property file object (onboardingPropertiesObject)

    :param property_file: The file which contains all the properties to be loaded
    :param account_name: The Snowflake Account instance. EG. ciscodev
    :return:
    """

    def as_dict(config):
        d = dict(config._sections)
        for k in d:
            d[k] = dict(config._defaults, **d[k])
            d[k].pop('__name__', None)
        return d

    try:
        config = configparser.ConfigParser()
        config.read(property_file)

        config_dict = as_dict(config)[account_name]

        return config_dict
    except Exception as e:
        print(
            'ERROR: Unable to open and collect property file contents for (property file: ' + property_file +
            ' account: ' + account_name + ')')
        print('ERROR: ' + str(e))
        exit(1)


def create_oracle_connection():
    """
    Create Oracle connection and return conn
    Calls open_oracle_connection

    :return: The oracle connection
    """

    try:
        property_file_contents = collect_property_file_contents('config.ini', 'ORACLE')
        conn = open_oracle_connection(property_file_contents)
        return conn
    except Exception as e:
        print('ERROR: Unable to connect to ORACLE account. Will be unable to write output.')
        print('ERROR: ' + str(e))
        exit(1)


def open_oracle_connection(config_properties):
    """
    Establish a database connection with Oracle

    :param config_properties: This is the properties obtained from the utl pull of config.ini
    :return: The database connection object
    """

    try:
        dsn_tns = cx_Oracle.makedsn(config_properties['host'], config_properties['port'],
                                    service_name=config_properties['service_name'])
        conn = cx_Oracle.connect(user=config_properties['db_username'],
                                 password=config_properties['db_password'], dsn=dsn_tns)

    except Exception as e:
        print(f"Unable to connect to {config_properties['host']}@{config_properties['service_name']} " + \
              f"due to {str(e).strip()}")
        sys.exit(1)

    return conn


def close_connection(conn):
    """
    Close a SF connection 

    :param conn: this is the conn object when creating the connection
    """
    conn.commit()
    conn.close()


#
def execute_oracle_df_qry(conn, qry):
    """
    Execute given query on Oracle

    :param qry: This is the qry to be executed on Oracle
    :return: Given dataframe with output of requested query
    """
    cursor = conn.cursor()
    curOpen = cursor.execute(qry)
    oraCols = [row[0] for row in curOpen.description]
    df_oraData = pd.DataFrame(curOpen.fetchall(), columns=(oraCols))
    df_oraData.columns = [x.lower() for x in df_oraData.columns.tolist()]
    cursor.close()
    return df_oraData


def execute_oracle_qry(conn, qry):
    """
    Execute given query on Oracle without any return value
    
    :param conn: This is thevonnection to Oracle
    :param qry: This is the qry to be executed on Oracle
    """
    cursor = conn.cursor()
    curOpen = cursor.execute(qry)
    cursor.close()
