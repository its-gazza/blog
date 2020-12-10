#%%
import re
import os
import praw
import requests
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from itertools import product

# Load .env 
load_dotenv()

# Initialize praw
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLNT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent="test"
)

# Get anime data
def get_anime_data(anime, year, season):
    df = pd.DataFrame(columns=['title', 'episode', 'karma', 'coins'])
    for submission in reddit.subreddit("anime").search(f'title:{anime} Episode'):
        coins = 0
        episode = re.findall('Episode (\d+) discussion', submission.title)
        if len(episode) == 0:
            continue
        else:
            episode = episode[0]

        for award in submission.all_awardings:
            coins += award['coin_price']
        submission_dict = {
            'title': anime,
            'episode': episode,
            'karma': submission.score,
            'coins': coins
        }
        # Append data to df
        df = df.append(submission_dict, ignore_index=True)
    df['year'] = year
    df['season'] = season
    return df

# Loop over each season for the last two years
seasons = ['summer', 'spring', 'winter', 'fall']
years = ['2018', '2019', '2020']

output = pd.DataFrame()
for season, year in product(seasons, years):
    print(f"==== {season} {year} ==== ")
    url = f'https://raw.githubusercontent.com/r-anime/holo/master/season_configs/{season}_{year}.yaml'
    data = requests.get(url).content
    anime_titles = re.findall(r'title: (.*)', data.decode('utf-8'), re.MULTILINE)
    pbar = tqdm(total = len(anime_titles))
    for anime in anime_titles:
        df_tmp = get_anime_data(anime.replace('\'', ''), year, season)
        output = output.append(df_tmp)
        pbar.update(1)
    pbar.close()

output.to_csv('output.csv', index=False)

