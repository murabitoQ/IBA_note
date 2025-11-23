import sqlite3
import datetime

class BaseDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()


# -----------------------------
# IC 資料庫
# -----------------------------
class IC_DB(BaseDB):

    def save_cast(self, cast_id, jp_name, en_name, caption, img_path):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO cast 
                (id, jp_name, en_name, caption, img_path)
                VALUES (?, ?, ?, ?, ?)
            """, (cast_id, jp_name, en_name, caption, img_path))
            self.conn.commit()
            cur.close()

        except sqlite3.Error as e:
            print(f"[DB ERROR] 儲存 {cast_id} 時錯誤：{e}")

    def get_data_by_image(self, image_src):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT id, jp_name, en_name, caption, img_path 
                FROM cast 
                WHERE jp_name = ?
            """, (image_src,))
            row = cur.fetchone()
            cur.close()

            if row:
                return {
                    "id": row[0],
                    "jp_name": row[1],
                    "en_name": row[2],
                    "caption": row[3],
                    "img_path": row[4]
                }
            else:
                return None

        except sqlite3.Error as e:
            print(f"[DB ERROR] 查詢 '{image_src}' 時錯誤：{e}")
            return None


# -----------------------------
# RC 資料庫
# -----------------------------
class RC_DB(BaseDB):

    def get_data_by_image(self, image_src):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM rc_data WHERE image_src=?", (image_src,))
            row = cur.fetchone()
            cur.close()

            if row:
                return dict(row)
            return {"info": "無資料"}

        except sqlite3.Error as e:
            print(f"[DB ERROR] 查詢 RC '{image_src}' 時錯誤：{e}")
            return {"info": "DB 發生錯誤"}


# -----------------------------
# ChatLog 資料庫
# -----------------------------
class ChatLogDB(BaseDB):

    def get_chat_by_image(self, image_src):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT content, timestamp
                FROM logs
                WHERE jp_name = ?
                ORDER BY timestamp ASC
            """, (image_src,))
            rows = cur.fetchall()
            cur.close()

            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            print(f"[DB ERROR] 查詢留言 '{image_src}' 時錯誤：{e}")
            return []

    def add_entry(self, image_src, text):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO logs (jp_name, content, timestamp)
                VALUES (?, ?, ?)
            """, (image_src, text, timestamp))
            self.conn.commit()
            cur.close()

        except sqlite3.Error as e:
            print(f"[DB ERROR] 新增留言錯誤：{e}")

    def update_entry(self, jp_name, original_timestamp, new_content):
        try:
            new_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cur = self.conn.cursor()
            cur.execute("""
                UPDATE logs
                SET content = ?, timestamp = ?
                WHERE jp_name = ? AND timestamp = ?
            """, (new_content, new_timestamp, jp_name, original_timestamp))
            self.conn.commit()
            cur.close()

        except sqlite3.Error as e:
            print(f"[DB ERROR] 編輯留言錯誤：{e}")

    def delete_entry(self, jp_name, timestamp):
        try:
            cur = self.conn.cursor()
            cur.execute("""
                DELETE FROM logs 
                WHERE jp_name=? AND timestamp=?
            """, (jp_name, timestamp))
            self.conn.commit()
            cur.close()

        except sqlite3.Error as e:
            print(f"[DB ERROR] 刪除留言錯誤：{e}")
