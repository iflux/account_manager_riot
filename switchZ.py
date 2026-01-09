import customtkinter as ctk
import subprocess
import os
import shutil
import time
import threading
import json
import base64
import requests
import urllib3
import psutil
from tkinter import messagebox, Menu

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

APP_NAME = "switchZ"
VERSION = "2.5 (Rank Fix)"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SAVES_DIR = os.path.join(BASE_DIR, "saved_sessions")
DB_FILE = os.path.join(BASE_DIR, "accounts_db.json")

C_BG = "#0a0a0a"
C_CARD = "#141414"
C_ACCENT = "#6200ea"
C_ACCENT_HOVER = "#7c4dff"
C_HOVER = "#292929"
C_TEXT_MAIN = "#ffffff"
C_RANK = "#00e5ff"      
C_NAME = "#ffffff"

POSSIBLE_PATHS = [
    r"C:\Riot Games\Riot Client\RiotClientServices.exe",
    r"D:\Riot Games\Riot Client\RiotClientServices.exe",
    r"E:\Riot Games\Riot Client\RiotClientServices.exe"
]
RIOT_CLIENT_PATH = next((p for p in POSSIBLE_PATHS if os.path.exists(p)), None)
LOCAL_APP_DATA = os.getenv('LOCALAPPDATA')
RIOT_DATA_DIR = os.path.join(LOCAL_APP_DATA, r"Riot Games\Riot Client\Data")
PRIVATE_SETTINGS_FILE = os.path.join(RIOT_DATA_DIR, "RiotGamesPrivateSettings.yaml")

if not os.path.exists(SAVES_DIR): os.makedirs(SAVES_DIR)

class LCUHandler:
    @staticmethod
    def get_auth():
        """Récupère le port et le token du client LoL"""
        for proc in psutil.process_iter(['name', 'cmdline']):
            if proc.info['name'] == 'LeagueClientUx.exe':
                args = proc.info['cmdline']
                port = next((a.split('=')[1] for a in args if '--app-port=' in a), None)
                token = next((a.split('=')[1] for a in args if '--remoting-auth-token=' in a), None)
                if port and token:
                    return port, base64.b64encode(f'riot:{token}'.encode()).decode()
        return None, None

    @staticmethod
    def fetch_rank_data():
        """Récupère le rang ET le pseudo actuel"""
        port, auth = LCUHandler.get_auth()
        if not port: return None

        headers = {"Authorization": f"Basic {auth}"}
        base_url = f"https://127.0.0.1:{port}"

        try:
            r_summoner = requests.get(f"{base_url}/lol-summoner/v1/current-summoner", headers=headers, verify=False, timeout=2)
            if r_summoner.status_code == 200:
                sum_data = r_summoner.json()
                game_name = f"{sum_data['gameName']}#{sum_data['tagLine']}"
            else:
                game_name = "Inconnu"

            r_rank = requests.get(f"{base_url}/lol-ranked/v1/current-ranked-stats", headers=headers, verify=False, timeout=2)
            rank_display = "UNRANKED"
            tier = "UNRANKED"

            if r_rank.status_code == 200:
                data = r_rank.json()
                queues = data.get('queues', [])
                solo = next((q for q in queues if q['queueType'] == 'RANKED_SOLO_5x5'), None)
                
                if solo and solo['tier'] != "":
                    tier = solo['tier']
                    division = solo['division']
                    lp = solo['leaguePoints']
                    rank_display = f"{tier} {division} - {lp} LP"
                else:
                    rank_display = "UNRANKED"

            return {"name": game_name, "rank": rank_display, "tier": tier}
            
        except Exception as e:
            print(f"API Error: {e}")
            return None

class Database:
    @staticmethod
    def load():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f: return json.load(f)
        return {}

    @staticmethod
    def save(data):
        with open(DB_FILE, 'w') as f: json.dump(data, f, indent=4)

    @staticmethod
    def update_entry(filename, **kwargs):
        data = Database.load()
        if filename not in data:
            data[filename] = {"display_name": filename.replace(".yaml", ""), "rank_text": "...", "tier": "UNRANKED"}
        
        for key, value in kwargs.items():
            data[filename][key] = value
        
        Database.save(data)
        return data

    @staticmethod
    def delete(filename):
        data = Database.load()
        if filename in data:
            del data[filename]
            Database.save(data)

class AccountCard(ctk.CTkFrame):
    def __init__(self, master, filename, data, load_cb, edit_cb, delete_cb):
        super().__init__(master, fg_color=C_CARD, corner_radius=10, border_width=0)
        
        self.filename = filename
        
        self.bar = ctk.CTkFrame(self, width=6, height=65, fg_color=C_ACCENT, corner_radius=6)
        self.bar.pack(side="left", padx=(10, 10), pady=10)

        self.info_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_frame.pack(side="left", fill="both", expand=True, pady=10)

        display = data.get("display_name", filename.replace(".yaml", ""))
        self.lbl_name = ctk.CTkLabel(self.info_frame, text=display, font=("Segoe UI", 16, "bold"), text_color=C_NAME, anchor="w")
        self.lbl_name.pack(fill="x")

        rank_txt = data.get("rank_text", "...")
        self.lbl_rank = ctk.CTkLabel(self.info_frame, text=rank_txt, font=("Consolas", 11, "bold"), text_color=C_RANK, anchor="w")
        self.lbl_rank.pack(fill="x")

        real_name = data.get("riot_id", "")
        if real_name:
            self.lbl_id = ctk.CTkLabel(self.info_frame, text=real_name, font=("Arial", 9), text_color="gray", anchor="w")
            self.lbl_id.pack(fill="x")

        self.btn_load = ctk.CTkButton(self, text="LOAD", width=70, height=30, 
                                      fg_color="transparent", border_width=1, border_color=C_ACCENT, text_color=C_ACCENT,
                                      hover_color=C_ACCENT, command=lambda: load_cb(filename))
        self.btn_load.pack(side="right", padx=15)

        self.bind("<Button-3>", self.show_menu)
        self.lbl_name.bind("<Button-3>", self.show_menu)

        self.menu = Menu(self, tearoff=0, bg="#222", fg="white", activebackground=C_ACCENT)
        self.menu.add_command(label="Renommer", command=lambda: edit_cb(filename))
        self.menu.add_command(label="Supprimer", command=lambda: delete_cb(filename))

    def show_menu(self, e): self.menu.tk_popup(e.x_root, e.y_root)

class SwitchZApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} {VERSION}")
        self.geometry("450x700")
        self.configure(fg_color=C_BG)
        ctk.set_appearance_mode("Dark")

        self.head = ctk.CTkFrame(self, fg_color="transparent")
        self.head.pack(pady=20)
        ctk.CTkLabel(self.head, text="switch", font=("Montserrat", 28, "bold"), text_color="white").pack(side="left")
        ctk.CTkLabel(self.head, text="Z", font=("Montserrat", 28, "bold"), text_color=C_ACCENT).pack(side="left")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", width=420)
        self.scroll.pack(expand=True, fill="both", padx=10)

        self.controls = ctk.CTkFrame(self, fg_color="#111", corner_radius=15)
        self.controls.pack(pady=15, padx=20, fill="x")

        self.entry_name = ctk.CTkEntry(self.controls, placeholder_text="Nom (ex: Smurf)", fg_color="#222", border_width=0, text_color="white")
        self.entry_name.pack(pady=10, padx=10, fill="x")

        self.btn_save = ctk.CTkButton(self.controls, text="SAUVEGARDER (Session Active)", fg_color=C_ACCENT, hover_color=C_ACCENT_HOVER, command=self.save_session)
        self.btn_save.pack(pady=(0,10), padx=10, fill="x")
        
        self.btn_logout = ctk.CTkButton(self.controls, text="Safe Logout (Ajouter compte)", fg_color="transparent", border_color="#e53935", border_width=1, text_color="#e53935", hover_color="#2b0b0b", command=self.safe_logout)
        self.btn_logout.pack(pady=(0,10), padx=10, fill="x")

        self.refresh_ui()

    def refresh_ui(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        if not os.path.exists(SAVES_DIR): return
        files = [f for f in os.listdir(SAVES_DIR) if f.endswith(".yaml")]
        db = Database.load()

        for f in files:
            if f not in db: db = Database.update_entry(f)
            AccountCard(self.scroll, f, db[f], self.load_session, self.rename_account, self.delete_account).pack(fill="x", pady=4)


    def kill_riot(self):
        targets = ["RiotClientServices.exe", "LeagueClient.exe", "LeagueClientUx.exe"]
        for t in targets:
            subprocess.run(f"taskkill /F /IM {t}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

    def save_session(self):
        name = self.entry_name.get()
        if not name: return messagebox.showwarning("Info", "Donne un nom !")

        if not os.path.exists(PRIVATE_SETTINGS_FILE) or os.path.getsize(PRIVATE_SETTINGS_FILE) < 150:
            return messagebox.showerror("Erreur", "Connecte-toi à LoL et coche 'Rester connecté' d'abord.")

        info = LCUHandler.fetch_rank_data()
        
        filename = f"{name}.yaml"
        shutil.copy2(PRIVATE_SETTINGS_FILE, os.path.join(SAVES_DIR, filename))
        
        if info:
            Database.update_entry(filename, display_name=name, rank_text=info['rank'], tier=info['tier'], riot_id=info['name'])
        else:
            Database.update_entry(filename, display_name=name)
            
        self.entry_name.delete(0, "end")
        self.refresh_ui()

    def load_session(self, filename):
        def run():
            self.kill_riot()
            src = os.path.join(SAVES_DIR, filename)
            try:
                if os.path.exists(PRIVATE_SETTINGS_FILE): os.remove(PRIVATE_SETTINGS_FILE)
                shutil.copy2(src, PRIVATE_SETTINGS_FILE)
            except Exception as e:
                print(e)
            
            if RIOT_CLIENT_PATH:
                subprocess.Popen([RIOT_CLIENT_PATH, "--launch-product=league_of_legends", "--launch-patchline=live"])
                threading.Thread(target=self.rank_tracker, args=(filename,), daemon=True).start()

        threading.Thread(target=run).start()

    def rank_tracker(self, filename):
        """Surveille le client pour mettre à jour UNIQUEMENT ce compte"""
        print(f"Tracker armé pour : {filename}")
        
        for _ in range(36):
            if LCUHandler.get_auth()[0]: break
            time.sleep(5)
        else:
            return 

        
        while True:
            time.sleep(10) 
            info = LCUHandler.fetch_rank_data()
            
            if not info: 
                print("Jeu fermé. Arrêt tracker.")
                break 
            
            
            current_db = Database.load().get(filename, {})
            if current_db.get("rank_text") != info['rank']:
                Database.update_entry(filename, rank_text=info['rank'], tier=info['tier'], riot_id=info['name'])
                print(f"Mise à jour Rank détectée pour {filename}: {info['rank']}")
               
                self.after(100, self.refresh_ui)

    def safe_logout(self):
        threading.Thread(target=lambda: (self.kill_riot(), 
                                         os.remove(PRIVATE_SETTINGS_FILE) if os.path.exists(PRIVATE_SETTINGS_FILE) else None,
                                         subprocess.Popen([RIOT_CLIENT_PATH, "--launch-product=league_of_legends", "--launch-patchline=live"]))).start()

    def rename_account(self, filename):
        d = ctk.CTkInputDialog(text="Nouveau nom:", title="Edit")
        new = d.get_input()
        if new:
            Database.update_entry(filename, display_name=new)
            self.refresh_ui()

    def delete_account(self, filename):
        if messagebox.askyesno("Supprimer", "Sûr ?"):
            try:
                os.remove(os.path.join(SAVES_DIR, filename))
                Database.delete(filename)
                self.refresh_ui()
            except: pass

if __name__ == "__main__":
    app = SwitchZApp()
    app.mainloop()
