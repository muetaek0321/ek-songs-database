"""
参考サイト：https://zenn.dev/robes/articles/00e86185677fb5
"""
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pandas as pd


OUTPUT_PATH = Path("./resource/")

# 歌ネットのURL
BASE_URL = 'https://www.uta-net.com'
# 楽曲リストのページのURL
URL_LIST = [
    'https://www.uta-net.com/artist/1232/',
    'https://www.uta-net.com/artist/1232/0/2/'
]
# usr_agentに先ほど取得したUserAgent情報を入力します
# https://testpage.jp/tool/ip_user_agent.php
HEADER = {'User-Agent': ''}


def main():
    # 既にある場合は読み込み
    output_file_path = OUTPUT_PATH.joinpath("lyrics_list.csv")
    if output_file_path.exists():
        lyric_df = pd.read_csv(output_file_path, encoding="cp932")
    else:
        lyric_df = None
    
    for url in URL_LIST:
        response = requests.get(url, headers=HEADER)

        soup = BeautifulSoup(response.text, 'lxml')

        #引数として、class_='sp-w-100'を与えます
        links = soup.find_all('td', class_='sp-w-100')

        #歌詞情報を取得します
        lyric_dict ={key: [] for key in ['曲名','歌詞']}
        for link in links:
            a = BASE_URL + (link.a.get('href'))
            response = requests.get(a, headers=HEADER)
            soup = BeautifulSoup(response.text, 'lxml')
            
            song_name = soup.find('h2').text
                
            song_kashi = soup.find('div', id="kashi_area")
            song_kashi = song_kashi.text
            
            lyric_dict['曲名'].append(song_name)
            lyric_dict['歌詞'].append(song_kashi)

        if lyric_df is None:
            lyric_df = pd.DataFrame(lyric_dict)
        else:
            lyric_df = pd.concat([lyric_df, pd.DataFrame(lyric_dict)], ignore_index=True)
    
    # 歌詞データをまとめたcsvを作成
    lyric_df.to_csv(OUTPUT_PATH.joinpath("lyrics_list.csv"), encoding="cp932", index=False)


if __name__ == "__main__":
    main()

