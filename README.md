# 🛡️ Satpam Laptop - Face Recognition Security System

> Sistem keamanan laptop berbasis pengenalan wajah dengan notifikasi real-time ke Telegram

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Haar_Cascade-green?style=flat&logo=opencv)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-blue?style=flat&logo=telegram)

## 📝 Deskripsi

**Satpam Laptop** adalah aplikasi keamanan desktop yang memanfaatkan kamera laptop untuk mendeteksi dan membedakan pemilik laptop dari penyusup. Ketika wajah asing terdeteksi, sistem akan mengambil foto dan mengirimkannya ke Telegram sebagai notifikasi keamanan.

## ✨ Fitur

- 🎥 **Real-time Face Detection** - Deteksi wajah menggunakan Haar Cascade
- 👤 **Face Registration** - Daftarkan wajah pemilik sebagai referensi
- 🔍 **Owner Recognition** - Identifikasi pemilik vs penyusup menggunakan histogram comparison
- 📱 **Telegram Alerts** - Kirim foto penyusup ke Telegram secara otomatis
- ⏱️ **Cooldown System** - Mencegah spam notifikasi (10 detik interval)
- 🖥️ **Desktop GUI** - Interface user-friendly dengan Tkinter

## 🛠️ Tech Stack

| Technology       | Purpose                                          |
| ---------------- | ------------------------------------------------ |
| Python 3.11+     | Core Language                                    |
| OpenCV           | Face Detection (Haar Cascade) & Image Processing |
| Tkinter          | Desktop GUI Framework                            |
| Pillow (PIL)     | Image Handling                                   |
| Telegram Bot API | Real-time Notifications                          |

## 🚀 Instalasi

1. **Clone repository**

   ```bash
   git clone https://github.com/yourusername/satpam-laptop.git
   cd satpam-laptop
   ```

2. **Install dependencies**

   ```bash
   pip install opencv-python pillow requests numpy
   ```

3. **Konfigurasi Telegram Bot**

   - Buat bot di [@BotFather](https://t.me/botfather)
   - Edit `main.py` dan isi `TOKEN_BOT` dan `CHAT_ID`

4. **Jalankan aplikasi**
   ```bash
   python main.py
   ```

## 📖 Cara Penggunaan

1. **Buka Aplikasi** - Jalankan `main.py`
2. **Daftarkan Wajah** - Klik tombol "DAFTARKAN WAJAH SAYA"
3. **Monitoring Aktif** - Sistem akan otomatis memantau
4. **Alert Penyusup** - Jika wajah asing terdeteksi, foto akan dikirim ke Telegram

## 📊 Alur Kerja

```
┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
│ Buka Kamera │───▶│ Daftar Wajah │───▶│ Mode Monitoring │
└─────────────┘    └──────────────┘    └────────┬────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          ▼                     ▼                     ▼
                   ┌────────────┐        ┌────────────┐        ┌────────────┐
                   │  Pemilik   │        │ Penyusup   │        │ Tidak Ada  │
                   │ (Aman ✅)  │        │ (Alert 🚨) │        │   Wajah    │
                   └────────────┘        └─────┬──────┘        └────────────┘
                                               │
                                               ▼
                                        ┌────────────┐
                                        │  Telegram  │
                                        │ Notification│
                                        └────────────┘
```

## 🎯 Roadmap

- [ ] Tambah opsi simpan riwayat deteksi ke database
- [ ] Multiple face registration
- [ ] Integrasi dengan WhatsApp
- [ ] Mode stealth (minimize to tray)

## 📄 License

MIT License - Feel free to use and modify!

---

<p align="center">Made with ❤️ for laptop security</p>
