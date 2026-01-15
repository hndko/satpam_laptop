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

# ================= KONFIGURASI =================
TOKEN_BOT = 'xxxx'  # <--- JANGAN LUPA ISI INI
CHAT_ID = 'xxxx'      # <--- JANGAN LUPA ISI INI
# ===============================================

class SecurityApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("850x700")

        # 1. Inisialisasi Kamera (Coba index 0, jika gagal coba 1)
        self.video_source = 0
        self.vid = cv2.VideoCapture(self.video_source, cv2.CAP_DSHOW)

        # Paksa resolusi standar
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.vid.isOpened():
             self.vid = cv2.VideoCapture(0) # Fallback tanpa DSHOW
             if not self.vid.isOpened():
                messagebox.showerror("Error", "Kamera tidak ditemukan! Coba restart laptop.")
                self.window.destroy()
                return

        # Load OpenCV Haar Cascade untuk deteksi wajah
        # Menggunakan file bawaan OpenCV
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            messagebox.showerror("Error", "Gagal load Haar Cascade!")
            self.window.destroy()
            return

        # Status
        self.mode = "IDLE"
        self.owner_face_hist = None  # Histogram wajah pemilik
        self.owner_face_img = None   # Gambar wajah pemilik untuk LBPH
        self.last_sent_time = 0
        self.cooldown_seconds = 10

        # GUI Elements
        self.lbl_status = Label(window, text="Status: Menunggu Pendaftaran Wajah", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_status.pack(pady=10)

        self.canvas = Label(window)
        self.canvas.pack()

        self.btn_register = Button(window, text="📷 DAFTARKAN WAJAH SAYA", font=("Arial", 12, "bold"),
                                   command=self.register_face, bg="#4CAF50", fg="white", height=2, width=30)
        self.btn_register.pack(pady=20)

        self.lbl_debug = Label(window, text="Debug Info: -", font=("Consolas", 8), fg="gray")
        self.lbl_debug.pack()

        # Loop Update
        self.delay = 30
        self.update()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

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

    def get_face_histogram(self, gray_frame, face_rect):
        """Ambil histogram dari area wajah untuk perbandingan"""
        x, y, w, h = face_rect
        face_roi = gray_frame[y:y+h, x:x+w]
        # Resize untuk konsistensi
        face_roi = cv2.resize(face_roi, (100, 100))
        # Hitung histogram
        hist = cv2.calcHist([face_roi], [0], None, [256], [0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist, face_roi

    def compare_faces(self, hist1, hist2):
        """Bandingkan dua histogram wajah, return similarity score 0-1"""
        # Correlation method: 1 = identical, -1 = opposite
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        return score

    def register_face(self):
        frame = self.get_safe_frame()
        if frame is not None:
            # Deteksi wajah dengan OpenCV
            faces, gray = self.detect_faces(frame)

            print(f"Registering... Found {len(faces)} face(s)")
            self.lbl_debug.config(text=f"Detected: {len(faces)} face(s)")

            if len(faces) > 0:
                # Ambil wajah pertama (terbesar)
                # Sort by area (w*h) descending
                faces_sorted = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
                main_face = faces_sorted[0]

                # Simpan histogram dan gambar wajah pemilik
                self.owner_face_hist, self.owner_face_img = self.get_face_histogram(gray, main_face)

                self.mode = "MONITOR"
                self.lbl_status.config(text="🛡️ SISTEM AKTIF: Memantau...", fg="green")
                self.btn_register.config(state="disabled", text="Wajah Terdaftar (Aman)", bg="gray")

                # Gambar kotak di wajah yang terdaftar
                x, y, w, h = main_face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

                # Simpan foto wajah yang terdaftar
                cv2.imwrite("owner_face.jpg", frame)

                messagebox.showinfo("Sukses", f"Wajah berhasil didaftarkan!\nUkuran area: {w}x{h} pixels")
            else:
                messagebox.showwarning("Gagal", "Wajah tidak terdeteksi. Pastikan wajah terlihat jelas dan coba lagi.")

    def send_telegram_async(self, filename):
        def worker():
            try:
                url = f"https://api.telegram.org/bot{TOKEN_BOT}/sendPhoto"
                with open(filename, 'rb') as f:
                    files = {'photo': f}
                    caption = f"🚨 PENYUSUP TERDETEKSI!\n🕒 {datetime.now().strftime('%H:%M:%S')}"
                    data = {'chat_id': CHAT_ID, 'caption': caption}
                    requests.post(url, files=files, data=data)
                print(f"Foto terkirim: {filename}")
            except Exception as e:
                print(f"Gagal kirim: {e}")
        threading.Thread(target=worker, daemon=True).start()

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
                    # Bandingkan dengan wajah pemilik
                    current_hist, _ = self.get_face_histogram(gray, face)
                    similarity = self.compare_faces(self.owner_face_hist, current_hist)

                    # Threshold: > 0.7 = kemungkinan pemilik
                    if similarity > 0.7:
                        # Pemilik
                        owner_detected = True
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(display_frame, f"Owner ({similarity:.2f})", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        # Kemungkinan penyusup
                        intruder_detected = True
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(display_frame, f"INTRUDER ({similarity:.2f})", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Update status dan kirim alert
                if intruder_detected:
                    now = time.time()
                    if now - self.last_sent_time > self.cooldown_seconds:
                        self.lbl_status.config(text="🚨 PENYUSUP! MENGIRIM FOTO...", fg="red")
                        fname = f"maling_{int(now)}.jpg"
                        cv2.imwrite(fname, frame)
                        self.send_telegram_async(fname)
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

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SecurityApp(root, "Security Cam Anti-Maling")
        root.mainloop()
    except Exception as e:
        print(f"CRASH: {e}")
        input("Tekan Enter untuk keluar...")