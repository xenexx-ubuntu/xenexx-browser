import sqlite3
import os

class PasswordManager:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.create_table()
        
    def fill_credentials(self):
        passwords = self.password_manager.get_passwords()
        for _, site, username, password in passwords:
            if site in self.url().toString():
                js_code = f"""
                const usernameInput = document.querySelector('input[name="username"]');  // Замените на правильный селектор
                const passwordInput = document.querySelector('input[name="password"]');  // Замените на правильный селектор
                if (usernameInput && passwordInput) {{
                    usernameInput.value = '{username}';
                    passwordInput.value = '{password}';
                    // Опционально, отправка формы
                    // document.querySelector('form').submit();
                }}
                """
                self.page().runJavaScript(js_code)
                break

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """
        self.connection.execute(query)
        self.connection.commit()

    def add_password(self, site, username, password):
        with self.conn:
            try:
                self.conn.execute("""
                INSERT INTO passwords (site, username, password)
                VALUES (?, ?, ?)
                """, (site, username, password))
                self.save_to_key_access(site, username, password)
            except sqlite3.IntegrityError:
                print("Пароль для этого сайта уже существует")

    def get_passwords(self):
        query = "SELECT * FROM passwords"
        cursor = self.connection.execute(query)
        return cursor.fetchall()

    def delete_password(self, password_id):
        query = "DELETE FROM passwords WHERE id = ?"
        self.connection.execute(query, (password_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()
