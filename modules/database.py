import sqlite3
import config


def select(cmd, one=False):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(cmd)
    if not one:
        data_list = cursor.fetchall()
    else:
        data_list = cursor.fetchone()
    return data_list

def insert_delete(cmd):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(cmd)
    conn.commit()
