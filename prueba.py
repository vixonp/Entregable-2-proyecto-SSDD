import pandas as pd

df = pd.read_csv("data/eventos.csv")
print(df.head())
print("Registros totales:", len(df))
print("Filtrados válidos tipo + calle:", df[(df["tipo"].notna()) & (df["tipo"] != "") & (df["calle"].notna())].shape[0])
print("Filtrados válidos con hora:", df[(df["fecha_extraccion"].notna()) & (df["fecha_extraccion"] != "")].shape[0])
