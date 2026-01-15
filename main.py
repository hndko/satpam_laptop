#!/usr/bin/env python3
"""
Satpam Laptop - Face Recognition Security System
Entry point for the application
"""
import tkinter as tk
from src.app import SecurityApp

def main():
    try:
        root = tk.Tk()
        app = SecurityApp(root, "Security Cam Anti-Maling v2.0")
        root.mainloop()
    except Exception as e:
        print(f"CRASH: {e}")
        input("Tekan Enter untuk keluar...")

if __name__ == "__main__":
    main()