import sqlite3
import json
import unicodedata
from pathlib import Path

import pandas as pd


# 定数
RESOUECE_PATH = Path("./resource/")
DATABASE_PATH = Path("./database/")

def main() -> None:
    
    # 歌詞リストを読み込む
    lyric_list_path = RESOUECE_PATH.joinpath("lyrics_list.csv")
    if lyric_list_path.exists():
        lyric_list_df = pd.read_csv(lyric_list_path, encoding="cp932")
        lyric_list_df["曲名"] = [unicodedata.normalize('NFKC', name) for name in lyric_list_df["曲名"].tolist()]
    else:
        lyric_list_df = None

    # SQLiteに接続
    sqlite_path = DATABASE_PATH.joinpath("songs.sqlite")
    # 既に存在する場合は削除
    if sqlite_path.exists():
        sqlite_path.unlink()
    # 新規作成扱いで接続
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    # テーブル作成
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        release_date TEXT,
        lyricist TEXT,
        composer TEXT,
        lyric TEXT
    );

    CREATE TABLE IF NOT EXISTS song_details (
        song_id INTEGER PRIMARY KEY,
        background TEXT,
        artist_comment TEXT,
        musical_features TEXT,
        reception TEXT,
        related_information TEXT,
        FOREIGN KEY(song_id) REFERENCES songs(id)
    );
    """)

    # データ登録
    for song_data_path in RESOUECE_PATH.glob("*.json"):
        
        # JSON読み込み
        with open(song_data_path, "r", encoding="utf-8") as f:
            song_data = json.load(f)
            
        # 歌詞を取得
        song_title = unicodedata.normalize('NFKC', song_data["title"])
        if lyric_list_df is not None:
            lyric = lyric_list_df.loc[lyric_list_df["曲名"]==song_title, "歌詞"].item()
        else:
            lyric = None

        # songs登録
        cursor.execute(
            """
            INSERT INTO songs
            (title, artist, release_date, lyricist, composer, lyric)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                song_title,
                song_data["artist"],
                song_data["release_date"],
                ",".join(song_data.get("lyrics", None)),
                ",".join(song_data.get("music", None)),
                lyric
            )
        )

        song_id = cursor.lastrowid

        # 詳細情報登録
        details = song_data.get("details", {})

        cursor.execute(
            """
            INSERT INTO song_details
            (
                song_id,
                background,
                artist_comment,
                musical_features,
                reception,
                related_information
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                song_id,
                details.get("background", {}).get("description"),
                details.get("background", {}).get("artist_comment"),
                json.dumps(
                    details.get("musical_features", {}),
                    ensure_ascii=False
                ),
                details.get("reception", {}).get("description"),
                json.dumps(
                    details.get("related_information", []),
                    ensure_ascii=False
                )
            )
        )

    conn.commit()
    conn.close()

    print("SQLiteへの変換完了")


if __name__ == "__main__":
    main()
