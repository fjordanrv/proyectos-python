import os
import glob
import pandas as pd
import re

def clean_comparison_stats(path):
    df = pd.read_csv(path, header=1)
    df = df.copy()
    if re.search(r"passing", path):
        df = df[['Player','90s','Att', 'Cmp%']]
        for col in df.columns:
            if col != '90s' and col == 'Att':
                df[col] = round(pd.to_numeric(df[col])/pd.to_numeric(df['90s']),2)
    elif re.search(r"standard", path):
        df = df[['Player','90s','PrgC', 'PrgP', 'PrgR']]
        for col in df.columns:
            if col != '90s' and col != 'Player':
                df[col] = round(pd.to_numeric(df[col])/pd.to_numeric(df['90s']),2)
    elif re.search("defense", path):
        df = df[['Player','90s', 'Tkl', 'TklW', 'Int', 'Blocks', 'Clr']]
        for col in df.columns:
            if col != '90s' and col != 'Player':
                df[col] = round(df[col]/df['90s'],2)

    df = df.drop(columns=['90s'])
    return df

