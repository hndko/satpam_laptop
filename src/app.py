"""
Main Application Class for Satpam Laptop
"""
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
import pickle

from .config import CONFIG, OWNER_DATA_FILE, OWNER_FACE_FILE
from .utils import get_face_histogram, compare_faces, get_capture_filename


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
             self.vid = cv2.VideoCapture(self.video_source)
             if not self.vid.isOpened():
                messagebox.showerror("Error", "Kamera tidak ditemukan! Coba restart laptop.")
                self.window.destroy()
                return

        # Load OpenCV Haar Cascade untuk deteksi wajah
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            messagebox.showerror("Error", "Gagal load Haar Cascade!")
            self.window.destroy()
            return

        # Status
        self.mode = "IDLE"
        self.owner_face_hist = None
        self.owner_face_img = None
        self.last_sent_time = 0
        self.cooldown_seconds = CONFIG['cooldown_seconds']
        self.similarity_threshold = CONFIG['similarity_threshold']

        # Coba load data wajah yang tersimpan
        self.load_owner_data()

        # GUI Elements
        status_text = "🛡️ SISTEM AKTIF: Memantau..." if self.owner_face_hist is not None else "Status: Menunggu Pendaftaran Wajah"
        status_color = "green" if self.owner_face_hist is not None else "blue"

        self.lbl_status = Label(window, text=status_text, font=("Arial", 14, "bold"), fg=status_color)
        self.lbl_status.pack(pady=10)

        self.canvas = Label(window)
        self.canvas.pack()

        btn_state = "disabled" if self.owner_face_hist is not None else "normal"
        btn_text = "Wajah Terdaftar ✅" if self.owner_face_hist is not None else "📷 DAFTARKAN WAJAH SAYA"
        btn_bg = "gray" if self.owner_face_hist is not None else "#4CAF50"

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

        # Update mode jika sudah ada data wajah
        if self.owner_face_hist is not None:
            self.mode = "MONITOR"

        # Loop Update
        self.delay = 30
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_owner_data(self):
        """Load data wajah pemilik dari file"""
        if os.path.exists(OWNER_DATA_FILE):
            try:
                with open(OWNER_DATA_FILE, 'rb') as f:
                    data = pickle.load(f)
                    self.owner_face_hist = data.get('histogram')
                    self.owner_face_img = data.get('image')
                print(f"✅ Owner data loaded from {OWNER_DATA_FILE}")
            except Exception as e:
                print(f"⚠️ Gagal load owner data: {e}")
                self.owner_face_hist = None
                self.owner_face_img = None

    def save_owner_data(self):
        """Simpan data wajah pemilik ke file"""
        try:
            data = {
                'histogram': self.owner_face_hist,
                'image': self.owner_face_img
            }
            with open(OWNER_DATA_FILE, 'wb') as f:
                pickle.dump(data, f)
            print(f"✅ Owner data saved to {OWNER_DATA_FILE}")
        except Exception as e:
            print(f"⚠️ Gagal simpan owner data: {e}")

    def reset_face(self):
        """Reset wajah yang terdaftar"""
        if messagebox.askyesno("Konfirmasi", "Yakin ingin reset wajah yang terdaftar?"):
            self.owner_face_hist = None
            self.owner_face_img = None
            if os.path.exists(OWNER_DATA_FILE):
                os.remove(OWNER_DATA_FILE)
            if os.path.exists(OWNER_FACE_FILE):
                os.remove(OWNER_FACE_FILE)

            self.mode = "IDLE"
            self.lbl_status.config(text="Status: Menunggu Pendaftaran Wajah", fg="blue")
            self.btn_register.config(state="normal", text="📷 DAFTARKAN WAJAH SAYA", bg="#4CAF50")
            messagebox.showinfo("Sukses", "Wajah berhasil di-reset!")

    def get_safe_frame(self):
        ret, frame = self.vid.read()
        if not ret or frame is None: return None
        if frame.shape[0] == 0 or frame.shape[1] == 0: return None
        return frame

    def detect_faces(self, frame):
        """Deteksi wajah menggunakan Haar Cascade"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )
        return faces, gray

    def register_face(self):
        frame = self.get_safe_frame()
        if frame is not None:
            faces, gray = self.detect_faces(frame)

            print(f"Registering... Found {len(faces)} face(s)")
            self.lbl_debug.config(text=f"Detected: {len(faces)} face(s)")

            if len(faces) > 0:
                faces_sorted = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                main_face = faces_sorted[0]

                self.owner_face_hist, self.owner_face_img = get_face_histogram(gray, main_face)

                # Simpan data wajah ke file
                self.save_owner_data()

                self.mode = "MONITOR"
                self.lbl_status.config(text="🛡️ SISTEM AKTIF: Memantau...", fg="green")
                self.btn_register.config(state="disabled", text="Wajah Terdaftar ✅", bg="gray")

                x, y, w, h = main_face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.imwrite(OWNER_FACE_FILE, frame)

                messagebox.showinfo("Sukses", f"Wajah berhasil didaftarkan!\nUkuran area: {w}x{h} pixels")
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
                faces, gray = self.detect_faces(frame)

                intruder_detected = False
                owner_detected = False

                for face in faces:
                    x, y, w, h = face
                    current_hist, _ = get_face_histogram(gray, face)
                    similarity = compare_faces(self.owner_face_hist, current_hist)

                    if similarity > self.similarity_threshold:
                        owner_detected = True
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Owner ({similarity:.2f})", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        intruder_detected = True
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(display_frame, f"INTRUDER ({similarity:.2f})", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Update status dan kirim alert
                if intruder_detected:
                    now = time.time()
                    if now - self.last_sent_time > self.cooldown_seconds:
                        self.lbl_status.config(text="🚨 PENYUSUP! MENGIRIM FOTO...", fg="red")
                        fname = get_capture_filename()
                        cv2.imwrite(fname, frame)
                        self.send_telegram_async(fname)
                        self.auto_lock_windows()
                        self.last_sent_time = now
                    else:
                        remaining = int(self.cooldown_seconds - (now - self.last_sent_time))
                        self.lbl_status.config(text=f"🚨 PENYUSUP! (Cooldown: {remaining}s)", fg="red")
                elif owner_detected:
                    self.lbl_status.config(text="✅ Aman (Pemilik Terdeteksi)", fg="green")
                elif len(faces) == 0:
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
