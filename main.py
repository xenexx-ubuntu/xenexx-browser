# hi, this was made by me, testers was: @dar, @winning_smile
# coded by me & chatgpt / deepseek

# run loader.bat to set-up this browser, this is my 1st project ever made.

# if something does not work, meet me on Discord:
# https://github.com/Isaki12/Xenexx-Browser

# CODE_START

import json
import sys
import os
import time
import getpass
import sqlite3
import ctypes
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for
import vlc
from password_manager import PasswordManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PySide6.QtCore import QUrl, QSize, Qt, Slot
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QWidget, QToolBar, QTabWidget, QListWidgetItem, QPushButton, QFileDialog, QMessageBox, QTextEdit, QHBoxLayout, QComboBox, QDialog, QTabBar, QFormLayout, 
    QCheckBox, QMenu, QStatusBar, QLabel, QDialogButtonBox, QInputDialog, QListWidget
)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineCookieStore, QWebEngineProfile, QWebEngineDownloadRequest
from PySide6.QtWebEngineWidgets import QWebEngineView
from tkinter import Tk, messagebox
import webview
from stem import Signal
from stem.control import Controller
from pathlib import Path

# DIRS

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"
SITE_CHECKER = TEMPLATES_DIR / "sitechecker" / "site_test.py"
BOOKMARKS_FILE = TEMPLATES_DIR / "xenexx-bookmarks.txt"
Prosya = TEMPLATES_DIR / "image.jpg"
Deka = TEMPLATES_DIR / "image2.jpg"
GDZ_PATH = BASE_DIR / "GDZ"
FILE_PATH = BASE_DIR
VPN_PATH = BASE_DIR / "PlanetVPN"
TOR_PATH = BASE_DIR / "TorBrowser"
TORRC_PATH = TOR_PATH / "Browser" / "TorBrowser" / "Data" / "Tor" / "torrc"
HISTORY_FILE = TEMPLATES_DIR / "xenexx-history.txt"
HOMEPAGE = "http://xenexx-browser.fwh.is"
DOWNLOADS_FOLDER = TEMPLATES_DIR / "xenexx-downloads.txt"

os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

app = QApplication(sys.argv)

# PASSWORD_MANAGER

class PasswordManager:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.create_table()
        
    def create_table(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY,
                site TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
            """)

    def add_password(self, site, username, password):
        with self.conn:
            self.conn.execute("""
            INSERT INTO passwords (site, username, password)
            VALUES (?, ?, ?)
            """, (site, username, password))

    def get_passwords(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM passwords")
        return cursor.fetchall()

    def delete_password(self, password_id):
        with self.conn:
            self.conn.execute("DELETE FROM passwords WHERE id = ?", (password_id,))

# DOWNLOAD_MANAGER

class DownloadManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Download Manager")
        self.setGeometry(100, 100, 400, 200)

        self.download_list = QListWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.download_list)
        self.setLayout(layout)

    def add_download(self, file_name):
        self.download_list.addItem(f"Load: {file_name}")

    def complete_download(self, file_name):
        for index in range(self.download_list.count()):
            item = self.download_list.item(index)
            if item.text().startswith(f"Download: {file_name}"):
                item.setText(f"Download: {file_name} - Ended")
                break

    def fail_download(self, file_name):
        for index in range(self.download_list.count()):
            item = self.download_list.item(index)
            if item.text().startswith(f":Load: {file_name}"):
                item.setText(f"Download: {file_name} - Error")
                break
    
# WEB_ENGINE

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url, _type, is_main_frame):
        if is_main_frame:
            return True
        return False
        
# TAB_BAR

class CustomTabBar(QTabBar):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        add_action = context_menu.addAction("+")
        add_action.triggered.connect(self.open_new_tab)
        close_action = context_menu.addAction("-")
        close_action.triggered.connect(lambda: self.close_tab(self.tabAt(pos)))
        context_menu.exec(self.mapToGlobal(pos))
    
    def open_new_tab(self):
        self.browser.open_TAB()

    def close_tab(self, index):

        if self.count() > 1:  
            self.browser.close_tab(index)
        else:
            QMessageBox.warning(self.browser, "Error", "You cant close last tab.")

# COOKIE_MANAGER

class CookieManager:
    COOKIE_FILE_PATH = os.path.join(FILE_PATH, "cookies.json")
    def __init__(self, settings, category, setting):
        self.settings = settings
        self.category = category
        self.setting = setting
        self.cookie_store = QWebEngineProfile.defaultProfile().cookieStore()

        if self.settings[self.category][self.setting]:
            # Разрешить куки
            QWebEngineProfile.defaultProfile().setPersistentStoragePath("C:\\Users\\{USERNAME}\\OneDrive\\Desktop\\browser\\cookies.json")
            self.load_cookies()

    def load_cookies(self):
        try:
            with open(self.COOKIE_FILE_PATH, "r") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    self.cookie_store.setCookie(QNetworkCookie.fromRawForm(cookie.encode()))
        except FileNotFoundError:
            pass  # Файл не найден, куки не загружены

    def save_cookies(self):
        self.cookie_store.allCookies().then(lambda cookies: self._save_cookies(cookies))

    def _save_cookies(self, cookies):
        cookie_list = [cookie.toRawForm().decode() for cookie in cookies]
        with open(self.COOKIE_FILE_PATH, "w") as file:
            json.dump(cookie_list, file)

# Пример использования
settings = {
    'category1': {
        'allow_cookies': True
    }
}

cookie_manager = CookieManager(settings, 'category1', 'allow_cookies')

# SYS_ENGINE

class CustomWebEngineView(QWebEngineView):
    def __init__(self):
        super().__init__()

def on_load_finished(self, success):
    if success:
        self.fill_credentials()  # Вызов метода после успешной загрузки страницы

        self.profile = QWebEngineProfile.defaultProfile()
        self.download_manager = DownloadManager()
        self.loadFinished.connect(self.on_load_finished)
        self.profile = QWebEngineProfile.defaultProfile()

        self.download_manager = DownloadManager


        self.cookie_store = self.profile.cookieStore()

        self.cookie_store.setCookieFilter(lambda cookie: True)

        self.setUrl(QUrl("xenexx-browser.fwh.is"))

def open_download_manager(self):
    self.download_manager = DownloadManager()
    self.download_manager.show()

def open_TAB(self):
    os.startfile(SITE_CHECKER) 

def open_VPN_connection(self):
    os.startfile("PlanetVPN")

def fill_credentials(self):
    # Получите логин и пароль из вашего менеджера паролей
    passwords = self.password_manager.get_passwords()  # Предполагаем, что метод возвращает список паролей
    for _, site, username, password in passwords:
        if site in self.url().toString():  # Убедитесь, что это ваш сайт
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
            break  # Убедитесь, что вы заполнили только для первого совпавшего сайта

def apply_dark_theme(self, ok):
    if ok:  
        dark_theme_css = """
        body, html, div, span, a, input, button, textarea {
            background-color: #121212 !important; /* Темный фон */
            color: #ffffff !important;             /* Белый текст */
        }

        a {
            color: #bb86fc !important;             /* Цвет ссылок */
        }

        input, textarea {
            background-color: #333333 !important; /* Темный фон для полей ввода */
            color: #ffffff !important;             /* Белый текст в поле ввода */
            border: 1px solid #444444 !important;  /* Темная граница */
        }

        img, video, iframe {
            filter: brightness(0.85) !important; /* Затемнить изображения и видео */
        }

        .gb_xb, .gb_8b, .gb_Z, .gb_bb, .gb_Fb {
            background-color: #121212 !important;
            color: #ffffff !important;
        }

        /* Наблюдатель изменения DOM */
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                for (let addedNode of mutation.addedNodes) {
                    if (addedNode.nodeType === 1) { // только элементы
                        addedNode.style.backgroundColor = '#121212'; // Применяем темный фон
                        addedNode.style.color = '#ffffff'; // Применяем белый текст
                    }
                }
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
        // Запуск инъекции стилей
        const style = document.createElement('style');
        style.innerHTML = `{dark_theme_css}`;
        document.head.appendChild(style);
        """
        
        self.page().runJavaScript(dark_theme_css)


    def on_download_requested(self, download_item: QWebEngineDownloadItem):
        file_name = download_item.suggestedFileName()
        download_path = os.path.join(DOWNLOADS_FOLDER, file_name)
        
        print(f"Load requested: {file_name}")
        self.download_manager.add_download(file_name)

        download_item.accept()

        download_item.finished.connect(lambda: self.download_completed(file_name))
        download_item.errorOccurred.connect(lambda: self.download_failed(file_name))

    def download_completed(self, file_name):
        print(f"Load is done: {file_name}")
        self.download_manager.complete_download(file_name)

    def download_failed(self, file_name):
        print(f"Loading error: {file_name}")
        self.download_manager.fail_download(file_name)

    def open_VPN_connection(self):
        os.startfile(VPN_PATH)

# ABOUT_WINDOW

class about(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        self.image1_label = QLabel(self)
        self.image1_pixmap = QPixmap(Prosya) 
        self.image1_label.setPixmap(self.image1_pixmap.scaledToWidth(200))  
        left_layout.addWidget(self.image1_label)

        text_layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("v4.1, beta version")
        self.text_edit.setFixedWidth(200) 
        text_layout.addWidget(self.text_edit)

        right_layout = QVBoxLayout()
        self.image2_label = QLabel(self)
        self.image2_pixmap = QPixmap(Deka)
        self.image2_label.setPixmap(self.image2_pixmap.scaledToWidth(200))
        right_layout.addWidget(self.image2_label)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(text_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setWindowTitle('Info')
        self.setGeometry(100, 100, 600, 400)

    def play_media(self):
        self.media_player = vlc.MediaPlayer('mew.mp3')
        self.media_player.play()

# MAIN_CODE

class Browser(QMainWindow):
    ICON_PATH = BASE_DIR / "icons"

    def __init__(self):
        super().__init__()
        self.auto_fill_passwords_enabled = True
        self.password_manager = PasswordManager(os.path.expanduser("~") + "\\passwords.db")
        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(True)

        self.bookmark_list_widget = QListWidget(self)
        self.bookmark_list_widget.setWindowTitle("Bookmarks")
        self.bookmark_list_widget.itemDoubleClicked.connect(self.open_bookmark)  # Open bookmark on double-click

        self.bookmarks = []
        self.load_bookmarks()
        self.setWindowTitle("Xenexx Browser")
        self.setFixedSize(1100, 930)

        self.setStyleSheet("""
            background-color: #2E2E2E; 
            color: white; 
            font-family: Arial, sans-serif;
        """)

        self.settings = {
            "Security": {
                "➊ JavaScript": True,
                "➋ Popups": True,
                "➌ TrackingProtection": True,
                "➍ Cookies": True
            },
            "Multimedia": {
                "➊♪ Audio": True,
                "➋ Video": True
            }
        }

        self.cookie_manager = CookieManager(self.settings, "Security", "➍ Cookies")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #333;
            }
            QTabBar::tab {
                background-color: #444;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #555;
            }
        """)
        
        self.tabs.setTabBar(CustomTabBar(self))
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.addTab(self.create_new_tab(), "☽▶New tab")

        self.url_bar = QLineEdit(self)
        self.url_bar.setStyleSheet("""
            background-color: #444;
            color: white;
            border: 1px solid #666;
            padding: 5px;
            border-radius: 5px;
        """)
        self.url_bar.returnPressed.connect(self.handle_navigation_in_tab)

        self.toolbar = QToolBar(self)
        self.addToolBar(self.toolbar)
        self.setup_buttons()
        self.setup_menu()

        layout = QVBoxLayout()
        layout.addWidget(self.url_bar)
        layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def show_password_manager(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Password Manager")
        layout = QVBoxLayout(dialog)
        
        self.password_table = QListWidget(dialog)
        layout.addWidget(self.password_table)
        
        self.load_passwords()

        add_button = QPushButton("Add Password", dialog)
        add_button.clicked.connect(self.add_password)
        layout.addWidget(add_button)
        
        self.password_table.itemDoubleClicked.connect(self.edit_password)
        dialog.setLayout(layout)
        dialog.exec()

    def load_passwords(self):
        self.password_table.clear()
        passwords = self.password_manager.get_passwords()
        for id, site, username, _ in passwords:
            self.password_table.addItem(f"{site} - {username}")

    def add_password(self):
        site, ok1 = QInputDialog.getText(self, "Site", "Enter site name:")
        if ok1 and site:
            username, ok2 = QInputDialog.getText(self, "Username", "Enter username:")
            if ok2 and username:
                password, ok3 = QInputDialog.getText(self, "Password", "Enter password:")
                if ok3 and password:
                    self.password_manager.add_password(site, username, password)
                    self.load_passwords()

    def edit_password(self, item):
        index = self.password_table.row(item)
        passwords = self.password_manager.get_passwords()
        password_data = passwords[index]

        new_password, ok = QInputDialog.getText(self, "Edit Password", "Your password:", text=password_data[3])
        if ok and new_password:
            self.password_manager.delete_password(password_data[0])
            self.password_manager.add_password(password_data[1], password_data[2], new_password)  # Добавление нового
            self.load_passwords()

    def save_layout(self):
        layout_data = {
            "tabs": [self.tabs.tabText(i) for i in range(self.tabs.count())],
            "toolbar_position": self.toolbar.geometry().getRect(),
        }
        with open("layout_config.json", "w") as f:
            json.dump(layout_data, f)

    def load_layout(self):
        try:
            with open("layout_config.json", "r") as f:
                layout_data = json.load(f)
                
                for tab_name in layout_data["tabs"]:
                    self.tabs.addTab(self.create_new_tab(), tab_name)
                
                x, y, width, height = layout_data["toolbar_position"]
                self.toolbar.setGeometry(x, y, width, height)

        except FileNotFoundError:
            pass

    def closeEvent(self, event):
        self.save_layout()
        self.cookie_manager.save_cookies()
        event.accept()

    def download_favicon(self, icon_url):
        try:
            response = requests.get(icon_url, stream=True)
            if response.status_code == 200:
                return QIcon.fromTheme("web", QIcon(QPixmap.fromImage(QImage.fromData(response.content))))
        except Exception:
            pass
        return QIcon.fromTheme("web")

    def save_bookmark(self, url):
        try:
            bookmarks = self.get_bookmarks()
            if url not in bookmarks:
                bookmarks.append(url)
                with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
                    f.write("\n".join(bookmarks))
                self.update_bookmark_list()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cant load bookmarks: {e}")

    def load_bookmarks(self):
        try:
            if os.path.exists(BOOKMARKS_FILE):
                with open(BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                    self.bookmarks = [line.strip() for line in f if line.strip()]
                self.update_bookmark_list()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cant load bookmarks: {e}")

    def get_bookmarks(self):
        return self.bookmarks

    def show_bookmarks(self):
        self.bookmark_list_widget.clear()
        self.update_bookmark_list()
        self.bookmark_list_widget.show()

    def get_favicon_url(self, url):
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
            if icon_link:
                icon_url = icon_link["href"]
                if not icon_url.startswith("http"):
                    icon_url = url.rstrip("/") + "/" + icon_url.lstrip("/")
                return icon_url
        except Exception:
            pass
        return ""

    def update_bookmark_list(self):
        self.toolbar.clear()
        for bookmark in self.bookmarks:
            url = bookmark
            title = url
            icon_url = self.get_favicon_url(url)
            icon = self.download_favicon(icon_url)
            
            action = QAction(icon, title, self.toolbar)
            action.setToolTip(url)
            action.triggered.connect(lambda checked, u=url: self.open_url(u))
            self.toolbar.addAction(action)

    def open_url(self, url):
        # Логика открытия URL в браузере
        print(f"Opening URL: {url}")

    def open_url(self, url):
        print(f"Opening URL: {url}")  # Для отладки
        self.tabs.addTab(self.create_new_tab(), "☽▶New tab")
        self.tabs.currentWidget().findChild(QWebEngineView).setUrl(QUrl(url))  # Переход на закладку
        self.tabs.currentWidget().findChild(CustomWebEngineView).setUrl(QUrl(url))
    
    def open_bookmark(self, item):
        url = "http://xenexx-browser.fwh.is"
        print(f"Opening URL: {url}")  # Для отладки
        self.tabs.addTab(self.create_new_tab(), "☽▶New tab")
        self.tabs.currentWidget().findChild(QWebEngineView).setUrl(QUrl(url))  # Переход на закладку
        self.tabs.currentWidget().findChild(CustomWebEngineView).setUrl(QUrl(url))

    def add_current_page_to_bookmarks(self):
        current_url = self.tabs.currentWidget().findChild(QWebEngineView).url().toString()
        self.save_bookmark(current_url)
        QMessageBox.information(self, "Done", f"Bookmark was added: {current_url}")

    def on_download_requested(self, download_item):
        download_path = os.path.join(DOWNLOADS_FOLDER, download_item.suggestedFileName())
        download_item.setPath(download_path)
        self.download_manager.add_download(download_item.suggestedFileName())  
        download_item.accept()

        download_item.finished.connect(lambda: self.download_completed(download_item.suggestedFileName()))
    
    def download_completed(self, file_name):
        self.download_manager.complete_download(file_name)

    def create_torrc_file(self):
        torrc_content = """\
DataDirectory C:\\Users\\{}\\AppData\\Roaming\\tor

SocksPort 9050

ControlPort 9051
""" 
        try:
            with open(TORRC_PATH, "w", encoding="utf-8") as torrc_file:
                torrc_file.write(torrc_content.format(USERNAME))
            QMessageBox.information(self, "Done!", "File conf torrc was created.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cant create torrc file: {e}")

    def open_tor_connection(self):
        QMessageBox.information(self, "Starting Tor", "Starting Tor...")

        try:
            os.startfile(os.path.join(TOR_PATH))
            time.sleep(10)
            self.connect_to_tor()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cant start Tor: {e}")

    def connect_to_tor(self):
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()  
                controller.signal(Signal.NEWNYM)  
                QMessageBox.information(self, "Done", "Loading via Tor was initialized.")
                
                if not self.check_tor_connection():
                    QMessageBox.warning(self, "Error", "Cant load via Tor")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cant take connection with Tor: {e}")

    def check_tor_connection(self):
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()  
                version = controller.get_version()
                print(f"Tor version: {version}")
                return True
        except Exception as e:
            print(f"Cant connect to Tor: {e}")
            return False

        
    def show_about(self):
        self.about = about()  
        self.about.show()
        
    def open_GDZ(self):
        self.tabs.addTab(self.create_new_tab(), "☽▶New tab")
        self.tabs.currentWidget().findChild(CustomWebEngineView).setUrl(QUrl("https://budu5.com/gdz/taggroup/2064"))  # Открыть budu5.com/gdz/taggroup/2064

    def open_TAB(self):
        new_tab_index = self.tabs.addTab(self.create_new_tab(), "☽▶New tab")
        self.tabs.setCurrentIndex(new_tab_index)


    def show_context_menu_TAB(self, pos):
        context_menu = QMenu(self)
        add_action = context_menu.addAction("+")
        add_action.triggered.connect(lambda: self.open_TAB(pos))
        close_action = context_menu.addAction("-")
        close_action.triggered.connect(lambda: self.close_tab(self.tabAt(pos)))
        context_menu.exec(self.mapToGlobal(pos))

    def close_tab(self, index):
        if self.tabs.count() > 1: 
            self.tabs.removeTab(index)
        else:
            QMessageBox.warning(self, "Information", "Cant close last tab.")


    def create_new_tab(self):
        new_tab = QWidget()
        tab_layout = QVBoxLayout()
        webview = CustomWebEngineView()
        webview.setUrl(QUrl(HOMEPAGE))
        tab_layout.addWidget(webview)
        new_tab.setLayout(tab_layout)

        return new_tab


    def open_link_in_new_tab(self, url):
        new_tab = self.create_new_tab()
        self.tabs.addTab(new_tab, "☽▶New tab")
        new_tab.findChild(CustomWebEngineView).setUrl(url)

    def handle_navigation_in_tab(self):
        input_text = self.url_bar.text().strip()
        if self.is_url(input_text):
            self.tabs.currentWidget().findChild(QWebEngineView).setUrl(QUrl(input_text))
        elif input_text:
            self.perform_search(input_text)

    def is_url(self, text):
        return text.startswith("http://") or text.startswith("https://")

    def perform_search(self, query):
        search_url = f"https://duckduckgo.com/html/?q={query}"
        self.fetch_and_display_results(search_url)

    def fetch_and_display_results(self, search_url):
        try:
            response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all("a", class_="result__a")

            html_content = "<html><head><style>"
            html_content += "body { font-family: Arial, sans-serif; color: #333; padding: 20px; }"
            html_content += "h3 { color: #1a0dab; }"
            html_content += "a { text-decoration: none; color: #1a0dab; }"
            html_content += "a:hover { text-decoration: underline; }"
            html_content += "</style></head><body><h2>Results of Xenexx Browser:</h2>"

            for result in search_results:
                title = result.text
                link = result["href"]
                if link.startswith("//"):
                    link = "https:" + link
                html_content += f'<div><h3><a href="{link}" target="_blank" onclick="window.location=\'{link}\'">{title}</a></h3><p>{link}</p></div><br>'
            html_content += "</body></html>"

            self.tabs.currentWidget().findChild(QWebEngineView).setHtml(html_content)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cant load results: {e}")

# ICONS

    def setup_buttons(self):
        icon_paths = {
            "Back": os.path.join(Browser.ICON_PATH, "back.png"),
            "Forward": os.path.join(Browser.ICON_PATH, "forward.png"),
            "Reload": os.path.join(Browser.ICON_PATH, "reload.png"),
            "Load": os.path.join(Browser.ICON_PATH, "download.png"),
            "Info": os.path.join(Browser.ICON_PATH, "info.png"),
            "Extensions": os.path.join(Browser.ICON_PATH, "extensions.png"),
            "VPN": os.path.join(Browser.ICON_PATH, "vpn.png"),
            "GDZ": os.path.join(Browser.ICON_PATH, "gdz.png"),
            "Tor": os.path.join(Browser.ICON_PATH, "tor.png"), 
            "TAB": os.path.join(Browser.ICON_PATH, "tab.png")
        }

        for action_name, ICON_PATH in icon_paths.items():
            button = QPushButton()
            button.setIcon(QIcon(str(ICON_PATH)))
            button.setIconSize(QSize(24, 24))
            button.clicked.connect(lambda _, x=action_name: self.action_triggered(x))
            button.setStyleSheet("""
                background-color: #444;
                border: none;
                color: white;
                padding: 8px;
                border-radius: 5px;
            """)
            button.setStyleSheet("QPushButton:hover {background-color: #555;}")
            button.setFixedSize(40, 40)

            if action_name == "Tor":
                button.clicked.connect(self.open_tor_connection)
            self.toolbar.addWidget(button)
            if action_name == "GDZ":
                button.clicked.connect(self.open_GDZ)

    def manage_extensions(self):
        QMessageBox.information(self, "Extension Manager", "In-dev")

# BUTTON_ENGINE

    def action_triggered(self, action_name):
        current_webview = self.tabs.currentWidget().findChild(QWebEngineView)
        if action_name == "Back":
            current_webview.back()
        elif action_name == "Forward":
            current_webview.forward()
        elif action_name == "Reload":
            current_webview.reload()
        elif action_name == "Load":
            self.open_download_manager()
        elif action_name == "VPN":
            self.open_VPN_connection()
        elif action_name == "TAB":
            self.open_new_tab()
        elif action_name == "Info":
            self.show_about()

    def open_download_manager(self):
        self.download_manager = DownloadManager()
        self.download_manager.show()
        
    def open_VPN_connection(self):
        os.startfile("PlanetVPN")

# BUTTONS

    def setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('⎙')

        save_page_action = QAction('⎘ Save page as..', self)
        save_page_action.triggered.connect(self.save_page)
        file_menu.addAction(save_page_action)

        bookmarks_menu = self.menuBar().addMenu("🕮")
        show_bookmarks_action = QAction("🕮 Show bookmarks", self)
        show_bookmarks_action.triggered.connect(self.show_bookmarks)
        bookmarks_menu.addAction(show_bookmarks_action)

        add_bookmark_action = QAction("🕮 Add current page in bookmarks", self)
        add_bookmark_action.triggered.connect(self.add_current_page_to_bookmarks)
        bookmarks_menu.addAction(add_bookmark_action)

        clear_bookmarks_action = QAction("🕮 Clear bookmarks", self)
        clear_bookmarks_action.triggered.connect(self.clear_bookmarks)  # Подключение к функции очистки закладок
        bookmarks_menu.addAction(clear_bookmarks_action)

        settings_menu = menubar.addMenu('☼')
        change_language_action = QAction('⚑⚐ Change language', self)
        change_language_action.triggered.connect(self.change_language)
        settings_menu.addAction(change_language_action)

        security_menu = QMenu("☰ Security", self)
        multimedia_menu = QMenu("☰ Multimedia", self)

        password_menu = menubar.addMenu("⚿")
        show_passwords_action = QAction("⚿ Show Passwords", self)
        show_passwords_action.triggered.connect(self.show_password_manager)
        password_menu.addAction(show_passwords_action)

        auto_fill_passwords_action = QAction("⚿ Toggle Auto Fill Passwords", self)
        auto_fill_passwords_action.triggered.connect(self.toggle_auto_fill_passwords)  # Подключаем к функции
        password_menu.addAction(auto_fill_passwords_action)

        for setting in self.settings["Security"]:
            setting_action = QAction(f"{setting} {'✔' if self.settings['Security'][setting] else '❌'}", self)
            setting_action.triggered.connect(lambda _, s=setting: self.toggle_setting(s, "Security"))
            security_menu.addAction(setting_action)

        for setting in self.settings["Multimedia"]:
            setting_action = QAction(f"{setting} {'✔' if self.settings['Multimedia'][setting] else '❌'}", self)
            setting_action.triggered.connect(lambda _, s=setting: self.toggle_setting(s, "Multimedia"))
            multimedia_menu.addAction(setting_action)

        settings_menu.addMenu(security_menu)
        settings_menu.addMenu(multimedia_menu)

        functions_menu = menubar.addMenu("↹")

        video_view_action = QAction("▶■ Video-watcher", self)
        video_view_action.triggered.connect(self.open_video_view)
        functions_menu.addAction(video_view_action)

        browser_method_action = QAction("♣︎♦︎ Browser method", self)
        browser_method_action.triggered.connect(self.open_browser_method)
        functions_menu.addAction(browser_method_action)

        proxy_action = QAction("❁ Proxy", self)
        proxy_action.triggered.connect(self.open_proxy_settings)
        functions_menu.addAction(proxy_action)

    if os.path.exists(ICON_PATH):
        button = QPushButton()
        button.setIcon(QIcon(str(ICON_PATH)))
    else:
        print(f"Icon wasnt found for path: {ICON_PATH}")

    def clear_bookmarks(self):
        self.bookmarks = []  
        with open(BOOKMARKS_FILE, "w", encoding="utf-8") as f:
            f.write("")
        self.update_bookmark_list()

    def toggle_auto_fill_passwords(self):
        self.auto_fill_passwords_enabled = not self.auto_fill_passwords_enabled  # Переключаем состояние
        state = "enabled" if self.auto_fill_passwords_enabled else "disabled"
        QMessageBox.information(self, "Autofill Passwords", f"Auto fill passwords is now {state}.")



    def toggle_setting(self, setting, category):
        current_state = self.settings[category][setting]
        self.settings[category][setting] = not current_state
        self.update_menu()

    def update_menu(self):
        for action in self.menuBar().actions():
            if isinstance(action, QMenu):
                for setting_action in action.actions():
                    setting_name = setting_action.text().split(" ")[0]
                    setting_action.setText(f"{setting_name} {'✔' if self.settings['Security'][setting_name] else '❌'}")

    def save_page(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save page as..", "", "HTML Files (*.html);;All Files (*)")
        if filename:
            current_webview = self.tabs.currentWidget().findChild(QWebEngineView)
            current_webview.page().toHtml(lambda html: self.save_html(html, filename))

    def save_html(self, html, filename):
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(html)
            QMessageBox.information(self, "Done", f"Page was saves as: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cant save page: {e}")

    def change_language(self):
        print("In dev")
        pass

    def open_video_view(self):
        url, ok = QInputDialog.getText(self, "Video-watcher", "Enter your URL to open it as default browser (without https)")
        if ok and url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url  
            self.create_video_window(url)

    def create_video_window(self, url):
        webview.create_window("Video-watcher", url, width=800, height=600, resizable=True)
        webview.start()
        
        
# BROWSER_METHOD

    def open_browser_method(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Browser Method")
        layout = QVBoxLayout(dialog)

        label = QLabel("Choose your Browser Method Agent:")
        layout.addWidget(label)
        user_agent_combo = QComboBox()
        user_agent_combo.addItems(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7; rv:132.0) Gecko/20100101 Firefox/132.0", "Mozilla/5.0 (X11; Linux i686; rv:132.0) Gecko/20100101 Firefox/132.0", "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0", "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:132.0) Gecko/20100101 Firefox/132.0", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0", "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)", "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)", "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)", "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko", "Mozilla/5.0 (Windows NT 6.2; Trident/7.0; rv:11.0) like Gecko", "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko", "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/130.0.2849.80", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/130.0.2849.80", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/114.0.0.0", "Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/114.0.0.0", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/114.0.0.0", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/114.0.0.0", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Vivaldi/7.0.3495.14", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Vivaldi/7.0.3495.14", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Vivaldi/7.0.3495.14", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Vivaldi/7.0.3495.14", "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Vivaldi/7.0.3495.14", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 YaBrowser/24.10.1.669 Yowser/2.5 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 YaBrowser/24.10.1.669 Yowser/2.5 Safari/537.36"])
        layout.addWidget(user_agent_combo)

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(dialog_buttons)
        dialog_buttons.accepted.connect(lambda: self.set_user_agent(user_agent_combo.currentText()))
        dialog_buttons.accepted.connect(dialog.accept)
        dialog_buttons.rejected.connect(dialog.reject)
        
        dialog.exec()

    def set_user_agent(self, user_agent):
        QWebEngineProfile.defaultProfile().setHttpUserAgent(user_agent)

    def open_proxy_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Proxy settings")
        layout = QFormLayout(dialog)

        proxy_ip = QLineEdit()
        proxy_port = QLineEdit()
        proxy_ip.setPlaceholderText("IP address")
        proxy_port.setPlaceholderText("Port")

        layout.addRow("IP address:", proxy_ip)
        layout.addRow("Port:", proxy_port)

        dialog_buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(dialog_buttons)
        dialog_buttons.accepted.connect(lambda: self.set_proxy(proxy_ip.text(), proxy_port.text()))
        dialog_buttons.accepted.connect(dialog.accept)
        dialog_buttons.rejected.connect(dialog.reject)

        dialog.exec()

    def set_proxy(self, ip, port):
        proxy_url = f"http://{ip}:{port}"
        QWebEngineProfile.defaultProfile().setHttpProxy(QUrl(proxy_url))

# MAIN_LOADER

if __name__ == "__main__":
    browser = Browser()
    browser.show()
    print("""
 Hi, this was made by me, testers were: "@dar", "@winning_smile";
 Coded by Xenexx (me) & ChatGPT + DeepSeek
 Sorry, because the code is kinda one 1k+ strokes
 I'll post upgraded versions still
 Also, autofill passwords made by "Windows Hello Pincode System" (not a guy)

 If something doesn't work, meet me at GitHub:
 https://github.com/Isaki12/Xenexx-Browser
    """)

    print("BASE_DIR:", BASE_DIR)
    print("SITE_CHECKER:", SITE_CHECKER)
    print("BOOKMARKS_FILE:", BOOKMARKS_FILE)
    print("Prosya:", Prosya)
    print("Deka:", Deka)
    print("GDZ_PATH:", GDZ_PATH)
    print("FILE_PATH:", FILE_PATH)
    print("VPN_PATH:", VPN_PATH)
    print("TOR_PATH:", TOR_PATH)
    print("TORRC_PATH:", TORRC_PATH)
    print("HISTORY_FILE:", HISTORY_FILE)
    print("HOMEPAGE:", HOMEPAGE)
    print("DOWNLOADS_FOLDER:", DOWNLOADS_FOLDER)
    sys.exit(app.exec())







# CODE_END




