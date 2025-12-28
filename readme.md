# Guruku.AI Backend

## Deskripsi
Backend aplikasi **Guruku.AI** menggunakan **Django** dan **Django REST Framework (DRF)**. Aplikasi ini berfungsi untuk menangani autentikasi, pembuatan materi, kuis, dan chatbot AI yang digunakan oleh siswa dan guru.

## Persyaratan
Sebelum memulai, pastikan sistem Anda sudah menginstal:
- **Python 3.x**
- **MySQL** (atau gunakan MariaDB yang kompatibel dengan MySQL)
- **virtualenv** (opsional, untuk menggunakan virtual environment)

## Instalasi Backend

### 1. Clone repository
```bash
git clone https://github.com/username/Guruku-AI.git
cd Guruku-AI/Backend
```

### 2. Buat Virtual Environment
``` bash
python3 -m venv venv
source venv/bin/activate  # di Linux/Mac
venv\Scripts\activate     # di Windows
```

### 3. Install dependensi
```bash
pip install -r requirements.txt
```

### 4. Setup Database
Buat database di MySQL
```bash
CREATE DATABASE guruku_db;
```

### 5. Update Konfigurasi di Config/settings.py
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'guruku_db',
        'USER': 'root',
        'PASSWORD': '',   # sesuaikan dengan password MySQL Anda
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 6. Jalankan Migrasi
```bash
python manage.py migrate
```

### 7. Jalankan Server
Untuk Jalankan server, cukup memakai command:
```bash
python manage.py runserver
```

### 8. Pengujian API bisa menggunakan Postman