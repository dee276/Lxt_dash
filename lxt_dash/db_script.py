import pandas as pd
import sqlite3
conn = sqlite3.connect("employee.db")
cursor = conn.cursor()
commit = conn.commit()
roll = conn.rollback()

conn.execute("""drop table transcripteurs""")

table_transcripteur = """ CREATE TABLE IF NOT EXISTS transcripteurs(
                    id INTEGER PRIMARY KEY,
                    nom TEXT NOT NULL UNIQUE,
                    page_id INTEGER,
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

# FOREIGN KEY (transcripteur_id) REFERENCES transcripteurs(id)
#Cette ligne signifie qu'un transcripteur_id doit obligatoirement correspondre à un id de la table transcripteur pour qu'une insertion soit valide


cursor.execute(table_transcripteur)

df = pd.read_csv("transcripteur.csv")
#print(df)
df.columns = df.columns.str.lower()
df_transcripteurs = df[['id','nom','page_id','actif']]
df_transcripteurs.to_sql('transcripteurs',conn, if_exists='replace', index=False)
#conn.execute(table_resultat_hebdo)

cursor.execute("SELECT *FROM transcripteurs")
for line in cursor.fetchall():
    print(line)


conn.close()
