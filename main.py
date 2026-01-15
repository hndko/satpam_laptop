import tkinter as tk
from tkinter import Label, Button, messagebox
import cv2
import requests
import threading
from datetime import datetime
from PIL import Image, ImageTk
import numpy as np
import time
import os
import json
import pickle
import face_recognition

# ================= KONFIGURASI =================
CONFIG_FILE = 'config.json'
OWNER_ENCODING_FILE = 'owner_encoding.pkl'

def load_config():
    """Load konfigurasi dari file JSON"""
    default_config = {
        "telegram_token": "YOUR_BOT_TOKEN_HERE",
        "chat_id": "YOUR_CHAT_ID_HERE",
        "cooldown_seconds": 10,
        "similarity_threshold": 0.6,
        "camera_index": 0,
        "auto_lock_on_intruder": False,
        "window_width": 850,
        "window_height": 700
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Merge dengan default config
                default_config.update(user_config)
                print(f"✅ Config loaded from {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠️ Gagal load config: {e}, menggunakan default")
    else:
        # Buat file config default
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        print(f"📝 Config file created: {CONFIG_FILE}")

    return default_config

# Load config
CONFIG = load_config()
# ===============================================

class SecurityApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry(f"{CONFIG['window_width']}x{CONFIG['window_height']}")

        # 1. Inisialisasi Kamera
        self.video_source = CONFIG['camera_index']
        self.vid = cv2.VideoCapture(self.video_source, cv2.CAP_DSHOW)

        # Paksa resolusi standar
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.vid.isOpened():
             self.vid = cv2.VideoCapture(self.video_source) # Fallback tanpa DSHOW
             if not self.vid.isOpened():
                messagebox.showerror("Error", "Kamera tidak ditemukan! Coba restart laptop.")
                self.window.destroy()
                return

        # Status
        self.mode = "IDLE"
        self.owner_face_encoding = None  # Face encoding pemilik (face_recognition)
        self.last_sent_time = 0
        self.cooldown_seconds = CONFIG['cooldown_seconds']
        self.similarity_threshold = CONFIG['similarity_threshold']

        # Coba load encoding yang tersimpan
        self.load_owner_encoding()

        # GUI Elements
        status_text = "🛡️ SISTEM AKTIF: Memantau..." if self.owner_face_encoding is not None else "Status: Menunggu Pendaftaran Wajah"
        status_color = "green" if self.owner_face_encoding is not None else "blue"

        self.lbl_status = Label(window, text=status_text, font=("Arial", 14, "bold"), fg=status_color)
        self.lbl_status.pack(pady=10)

        self.canvas = Label(window)
        self.canvas.pack()

        btn_state = "disabled" if self.owner_face_encoding is not None else "normal"
        btn_text = "Wajah Terdaftar ✅" if self.owner_face_encoding is not None else "📷 DAFTARKAN WAJAH SAYA"
        btn_bg = "gray" if self.owner_face_encoding is not None else "#4CAF50"

        self.btn_register = Button(window, text=btn_text, font=("Arial", 12, "bold"),
                                   command=self.register_face, bg=btn_bg, fg="white", height=2, width=30,
                                   state=btn_state)
        self.btn_register.pack(pady=10)

        # Tombol reset wajah
        self.btn_reset = Button(window, text="🔄 Reset Wajah", font=("Arial", 10),
                                command=self.reset_face, bg="#FF5722", fg="white", height=1, width=15)
        self.btn_reset.pack(pady=5)

        self.lbl_debug = Label(window, text="Debug Info: -", font=("Consolas", 8), fg="gray")
        self.lbl_debug.pack()

        # Update mode jika sudah ada encoding
        if self.owner_face_encoding is not None:
            self.mode = "MONITOR"

        # Loop Update
        self.delay = 30
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_owner_encoding(self):
        """Load face encoding pemilik dari file"""
        if os.path.exists(OWNER_ENCODING_FILE):
            try:
                with open(OWNER_ENCODING_FILE, 'rb') as f:
                    self.owner_face_encoding = pickle.load(f)
                print(f"✅ Owner encoding loaded from {OWNER_ENCODING_FILE}")
            except Exception as e:
                print(f"⚠️ Gagal load owner encoding: {e}")
                self.owner_face_encoding = None

    def save_owner_encoding(self):
        """Simpan face encoding pemilik ke file"""
        try:
            with open(OWNER_ENCODING_FILE, 'wb') as f:
                pickle.dump(self.owner_face_encoding, f)
            print(f"✅ Owner encoding saved to {OWNER_ENCODING_FILE}")
        except Exception as e:
            print(f"⚠️ Gagal simpan owner encoding: {e}")

    def reset_face(self):
        """Reset wajah yang terdaftar"""
        if messagebox.askyesno("Konfirmasi", "Yakin ingin reset wajah yang terdaftar?"):
            self.owner_face_encoding = None
            if os.path.exists(OWNER_ENCODING_FILE):
                os.remove(OWNER_ENCODING_FILE)
            if os.path.exists("owner_face.jpg"):
                os.remove("owner_face.jpg")

            self.mode = "IDLE"
            self.lbl_status.config(text="Status: Menunggu Pendaftaran Wajah", fg="blue")
            self.btn_register.config(state="normal", text="📷 DAFTARKAN WAJAH SAYA", bg="#4CAF50")
            messagebox.showinfo("Sukses", "Wajah berhasil di-reset!")

    def get_safe_frame(self):
        ret, frame = self.vid.read()
        if not ret or frame is None: return None
        if frame.shape[0] == 0 or frame.shape[1] == 0: return None
        return frame

    def register_face(self):
        frame = self.get_safe_frame()
        if frame is not None:
            # Konversi BGR ke RGB untuk face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Deteksi wajah dengan face_recognition
            face_locations = face_recognition.face_locations(rgb_frame)

            print(f"Registering... Found {len(face_locations)} face(s)")
            self.lbl_debug.config(text=f"Detected: {len(face_locations)} face(s)")

            if len(face_locations) > 0:
                # Ambil encoding wajah pertama
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                if len(face_encodings) > 0:
                    self.owner_face_encoding = face_encodings[0]

                    # Simpan encoding ke file
                    self.save_owner_encoding()

                    self.mode = "MONITOR"
                    self.lbl_status.config(text="🛡️ SISTEM AKTIF: Memantau...", fg="green")
                    self.btn_register.config(state="disabled", text="Wajah Terdaftar ✅", bg="gray")

                    # Gambar kotak di wajah yang terdaftar
                    top, right, bottom, left = face_locations[0]
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

                    # Simpan foto wajah yang terdaftar
                    cv2.imwrite("owner_face.jpg", frame)

                    messagebox.showinfo("Sukses", f"Wajah berhasil didaftarkan dengan face_recognition!")
                else:
                    messagebox.showwarning("Gagal", "Tidak dapat membuat encoding wajah. Coba lagi.")
            else:
                messagebox.showwarning("Gagal", "Wajah tidak terdeteksi. Pastikan wajah terlihat jelas dan coba lagi.")

    def send_telegram_async(self, filename):
        def worker():
            try:
                url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendPhoto"
                with open(filename, 'rb') as f:
                    files = {'photo': f}
                    caption = f"🚨 PENYUSUP TERDETEKSI!\n🕒 {datetime.now().strftime('%H:%M:%S')}"
                    data = {'chat_id': CONFIG['chat_id'], 'caption': caption}
                    requests.post(url, files=files, data=data)
                print(f"Foto terkirim: {filename}")
            except Exception as e:
                print(f"Gagal kirim: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def auto_lock_windows(self):
        """Lock Windows jika diaktifkan di config"""
        if CONFIG.get('auto_lock_on_intruder', False):
            try:
                import ctypes
                ctypes.windll.user32.LockWorkStation()
                print("🔒 Windows locked!")
            except Exception as e:
                print(f"Gagal lock Windows: {e}")

    def update(self):
        frame = self.get_safe_frame()

        if frame is not None:
            display_frame = frame.copy()

            # Logika Monitoring
            if self.mode == "MONITOR":
                # Konversi BGR ke RGB untuk face_recognition
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Deteksi wajah
                face_locations = face_recognition.face_locations(rgb_frame)

                intruder_detected = False
                owner_detected = False

                if len(face_locations) > 0:
                    # Dapatkan encoding semua wajah yang terdeteksi
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                        # Bandingkan dengan wajah pemilik
                        matches = face_recognition.compare_faces([self.owner_face_encoding], face_encoding,
                                                                  tolerance=self.similarity_threshold)
                        face_distance = face_recognition.face_distance([self.owner_face_encoding], face_encoding)[0]

                        # Hitung similarity (1 - distance)
                        similarity = 1 - face_distance

                        if matches[0]:
                            # Pemilik
                            owner_detected = True
                            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.putText(display_frame, f"Owner ({similarity:.2f})", (left, top-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        else:
                            # Penyusup
                            intruder_detected = True
                            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            cv2.putText(display_frame, f"INTRUDER ({similarity:.2f})", (left, top-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Update status dan kirim alert
                if intruder_detected:
                    now = time.time()
                    if now - self.last_sent_time > self.cooldown_seconds:
                        self.lbl_status.config(text="🚨 PENYUSUP! MENGIRIM FOTO...", fg="red")
                        fname = f"maling_{int(now)}.jpg"
                        cv2.imwrite(fname, frame)
                        self.send_telegram_async(fname)
                        self.auto_lock_windows()
                        self.last_sent_time = now
                    else:
                        remaining = int(self.cooldown_seconds - (now - self.last_sent_time))
                        self.lbl_status.config(text=f"🚨 PENYUSUP! (Cooldown: {remaining}s)", fg="red")
                elif owner_detected:
                    self.lbl_status.config(text="✅ Aman (Pemilik Terdeteksi)", fg="green")
                elif len(face_locations) == 0:
                    self.lbl_status.config(text="👀 Memantau... (Tidak ada wajah)", fg="orange")

            # Tampilkan di GUI
            display_frame = cv2.resize(display_frame, (640, 480))
            img = Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.imgtk = imgtk
            self.canvas.configure(image=imgtk)

        self.window.after(self.delay, self.update)

    def on_closing(self):
        if self.vid.isOpened(): self.vid.release()
        self.window.destroy()

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SecurityApp(root, "Security Cam Anti-Maling v2.0")
        root.mainloop()
    except Exception as e:
        print(f"CRASH: {e}")
        input("Tekan Enter untuk keluar...")