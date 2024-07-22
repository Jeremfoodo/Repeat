import sqlite3

def init_db():
    conn = sqlite3.connect('objectifs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS objectifs (
            id INTEGER PRIMARY KEY,
            pays TEXT,
            segment TEXT,
            objectif INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_objectif(pays, segment, objectif):
    conn = sqlite3.connect('objectifs.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO objectifs (pays, segment, objectif)
        VALUES (?, ?, ?)
    ''', (pays, segment, objectif))
    conn.commit()
    conn.close()

def get_objectifs():
    conn = sqlite3.connect('objectifs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM objectifs')
    data = c.fetchall()
    conn.close()
    return data

def update_objectif(pays, segment, objectif):
    conn = sqlite3.connect('objectifs.db')
    c = conn.cursor()
    c.execute('''
        UPDATE objectifs
        SET objectif = ?
        WHERE pays = ? AND segment = ?
    ''', (objectif, pays, segment))
    conn.commit()
    conn.close()
