import sqlite3

import pandas as pd

df = pd.read_csv('../data/ingredients.csv', names=['name', 'measurement_unit'])

connection = sqlite3.connect('../backend/db.sqlite3')

df.to_sql('recipes_ingredient', connection, if_exists='replace', index='id')

connection.close()

#df = pd.read_json('../data/ingredients.json', orient='records')