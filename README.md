# 🛡️ Satpam Laptop - Face Recognition Security System

> Sistem keamanan laptop berbasis pengenalan wajah dengan notifikasi real-time ke Telegram

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Haar_Cascade-green?style=flat&logo=opencv)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-blue?style=flat&logo=telegram)

## 📝 Deskripsi

**Satpam Laptop** adalah aplikasi keamanan desktop yang memanfaatkan kamera laptop untuk mendeteksi dan membedakan pemilik laptop dari penyusup. Ketika wajah asing terdeteksi, sistem akan mengambil foto dan mengirimkannya ke Telegram sebagai notifikasi keamanan.

## ✨ Fitur

- 🧠 **Deep Learning Face Recognition** - Deteksi wajah akurat dengan `face_recognition` library
- 👤 **Persistent Face Registration** - Wajah tersimpan, tidak perlu daftar ulang
- 🔍 **Owner Recognition** - Identifikasi pemilik vs penyusup
- 📱 **Telegram Alerts** - Kirim foto penyusup ke Telegram secara otomatis
- ⏱️ **Cooldown System** - Mencegah spam notifikasi
- 🔒 **Auto-Lock Windows** - Kunci laptop otomatis saat penyusup terdeteksi (opsional)
- 🔧 **External Config** - Konfigurasi lewat file JSON, tidak perlu edit code
- 🖥️ **Desktop GUI** - Interface user-friendly dengan Tkinter

## 🛠️ Tech Stack

| Technology       | Purpose                        |
| ---------------- | ------------------------------ |
| Python 3.11+     | Core Language                  |
| face_recognition | Deep Learning Face Recognition |
| dlib             | Face Detection Backend         |
| OpenCV           | Image Processing               |
| Tkinter          | Desktop GUI Framework          |
| Pillow (PIL)     | Image Handling                 |
| Telegram Bot API | Real-time Notifications        |

## 🚀 Instalasi

1. **Clone repository**

   ```bash
   git clone https://github.com/yourusername/satpam-laptop.git
   cd satpam-laptop
   ```

2. **Install dlib** (sudah tersedia wheel file)

   ```bash
   pip install dlib-19.24.1-cp311-cp311-win_amd64.whl
   ```

3. **Install dependencies**

   ```bash
   pip install opencv-python pillow requests numpy face_recognition
   ```

4. **Konfigurasi** - Copy template dan edit:

   ```bash
   cp config.example.json config.json
   ```

   Lalu edit `config.json` dengan token Telegram Anda:

   ```json
   {
     "telegram_token": "YOUR_BOT_TOKEN_HERE",
     "chat_id": "YOUR_CHAT_ID_HERE",
     "cooldown_seconds": 10,
     "similarity_threshold": 0.6,
     "camera_index": 0,
     "auto_lock_on_intruder": false
   }
   ```

   > ⚠️ **Note:** `config.json` sudah di-ignore oleh `.gitignore` untuk keamanan credential.

5. **Jalankan aplikasi**
   ```bash
   python main.py
   ```

## ⚙️ Konfigurasi

| Parameter               | Deskripsi                           | Default |
| ----------------------- | ----------------------------------- | ------- |
| `telegram_token`        | Token bot Telegram dari @BotFather  | -       |
| `chat_id`               | Chat ID untuk menerima notifikasi   | -       |
| `cooldown_seconds`      | Interval antar notifikasi           | 10      |
| `similarity_threshold`  | Toleransi pencocokan wajah (0-1)    | 0.6     |
| `camera_index`          | Index kamera (0, 1, dll)            | 0       |
| `auto_lock_on_intruder` | Auto lock Windows jika ada penyusup | false   |

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
