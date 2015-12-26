import sqlite3

def getDBConnection(dbs):
    """Helper function to return a db connection"""
    conn = sqlite3.connect(dbs)    
    return conn

class dao:
    def __init__(self, dbs='C:/frank/mdata/mydb'):
        self.dbs = dbs
        self.conn = getDBConnection(dbs)
        self.cursor = self.conn.cursor()  
        
    def close(self):
        self.conn.close()  
        