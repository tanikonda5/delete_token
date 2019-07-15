import datetime
from datetime import datetime

from util import *


def delete_invalid_token():
    conn = create_oracle_connection()
    query = "Select token, token_expiration_date, secret_key_path from vault where active_flag=1"
    df = execute_oracle_df_qry(conn, query)
    for i in range(0, len(df)):
        token = df.iat[i, 0]
        token_expiration_date = df.iat[i, 1]
        today = datetime.now()
        delta = (token_expiration_date - today).days
        if delta <= 0:
            update_query = "update vault set ACTIVE_FLAG=0 where token='{}' ".format(token)
            execute_oracle_qry(conn, update_query)

            print(token, token_expiration_date, delta)

    close_connection(conn)


delete_invalid_token()
