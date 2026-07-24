import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_parquet('input.parquet')
plt.hexbin(df['bprp0'], df['mg0'], gridsize=512, mincnt=1)
plt.gca().invert_yaxis()
plt.xlabel('bprp0')
plt.ylabel('mg0')
plt.tight_layout()
plt.savefig('cmd.png', dpi=200)
