import argparse
import io
import os
import pathlib
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

parser = argparse.ArgumentParser()

parser.add_argument('gamedata_dir', action='store',
                    help='Specifiy the game data directory')

args = parser.parse_args()


def exclude_query_params(url: str, params: list[str]):
  parsed_url = urlparse(url)
  query_params = parse_qs(parsed_url.query)
  filtered_params = {key: value for key, value in query_params.items() if key in params}
  updated_query_string = urlencode(filtered_params, doseq=True)
  updated_url = urlunparse(parsed_url._replace(query=updated_query_string))
  return updated_url
  
  
data_dir = pathlib.Path(args.gamedata_dir, 'webCaches')
if not data_dir.is_dir():
  print(f'${data_dir} is not a directory')
version = sorted(os.listdir(data_dir)).pop()
  
with io.open(pathlib.Path(args.gamedata_dir, f'webCaches/{version}/Cache/Cache_Data/data_2'), encoding='utf-8', errors='ignore') as f:
  content = f.read()
  splited = content.split('1/0/')
  extracted = False
  for segment in splited:
    if segment.startswith('https://') and 'getGachaLog' in segment:
      url = segment.split('{')[0]
      url = url.split('#')[0]
      # Extracted URL
      trimmed = exclude_query_params(url, ['authkey', 'authkey_ver', 'sign_type', 'game_biz', 'lang'])
      # Test URL
      try:
        res = requests.get(trimmed)
        if res.ok:
          result: dict = res.json()
          if result['retcode'] == 0:
            print('Warp URL found')
            print(trimmed)
            extracted = True
            break
          
      except requests.exceptions.RequestException as e:
        print(e)
  
  if not extracted:
    print('No valid warp URL found. Please restart your game and open the Gacha page again')
