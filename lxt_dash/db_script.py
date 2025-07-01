import pandas as pd
import sqlite3
#breakpoint()
conn = sqlite3.connect("employee.db")
cursor = conn.cursor()
commit = conn.commit()
roll = conn.rollback()

#conn.execute("""drop table transcripteurs""")

table_transcripteur = """ CREATE TABLE IF NOT EXISTS transcripteurs(
                    id INTEGER PRIMARY KEY,
                    nom TEXT NOT NULL UNIQUE,
                    page_id INTEGER,
                    langue TEXT
                    actif CHAR(1)
                    );"""

table_resultat_hebdo = """ CREATE TABLE IF NOT EXISTS resultats(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       transcripteur_id INTEGER,
                       semaine DATE,
                       vitesse_h REAL,
                       qualite REAL,
                       productivite INTEGER,
                       FOREIGN KEY (transcripteur_id) REFERENCES transcripteurs(id)
                       );"""

table_resultat_quotidien = """ CREATE TABLE IF NOT EXISTS resultats_journaliers(
id INTEGER PRIMARY KEY AUTOINCREMENT,
transcripteur_id INTEGER NOT NULL,
jour DATE NOT NULL,
vitesse_h REAL,
qualite REAL,
productivite INTEGER,
FOREIGN KEY (transcripteur_id) REFERENCES transcripteurs(id),
UNIQUE(transcripteur_id, jour)
);"""

# FOREIGN KEY (transcripteur_id) REFERENCES transcripteurs(id)
#Cette ligne signifie qu'un transcripteur_id doit obligatoirement correspondre à un id de la table transcripteur pour qu'une insertion soit valide


#cursor.execute(table_transcripteur)
#cursor.execute(table_resultat_hebdo)
#cursor.execute(table_resultat_quotidien)
#df = pd.read_csv("transcripteur.csv")
#cursor.execute("""CREATE INDEX IF NOT EXISTS idx_transcripteur_jour
#ON resultats_journaliers (transcripteur_id, jour);""")

df_res = pd.read_sql_query("select *from resultats_journaliers", conn)
print(df_res.tail())
#df.columns = df.columns.str.lower()
#df_transcripteurs = df[['id','nom','page_id','langue','actif']]
#df_transcripteurs.to_sql('transcripteurs',conn, if_exists='replace', index=False)
#conn.execute(table_resultat_hebdo)

#cursor.execute("SELECT *FROM transcripteurs")
#for line in cursor.fetchall():
#    print(line)


conn.close()
