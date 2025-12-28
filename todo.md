
# TODO List Backend - Guruku.AI (Django)

### 1. Pengaturan Autentikasi Pengguna dan Role
- [ ] **Custom User Model**:  
  - Implementasikan model **Custom User** yang memiliki atribut `role` (admin, teacher, student) dan `is_verified` untuk guru.
  - Pastikan penggunaan **`AbstractBaseUser`** untuk custom user.

- [ ] **JWT Authentication**:  
  - Gunakan **`djangorestframework-simplejwt`** untuk implementasi login menggunakan JWT.
  - Implementasi **token expiration** dan **refresh token**.

- [ ] **Register API Endpoint**:  
  - Endpoint untuk **pendaftaran pengguna** baru (`POST /api/users/register/`).
  - Validasi email dan password dengan aturan yang sesuai.

- [ ] **Login API Endpoint**:  
  - Endpoint untuk **autentikasi** pengguna dan menghasilkan token JWT (`POST /api/users/login/`).

- [ ] **Role-based Access Control**:  
  - Implementasi **role-based access control** (misalnya, hanya guru yang dapat membuat materi dan kuis).

- [ ] **Middleware untuk Verifikasi Guru**:  
  - Implementasikan **middleware** yang memeriksa apakah guru telah diverifikasi (`is_verified=True`).

---

### 2. Manajemen Kelas dan Materi
- [ ] **Model untuk Kelas (Class)**:  
  - Buat model `Class` yang mencakup informasi seperti nama kelas, deskripsi, dan guru pengampu.
  - Tautkan model `Class` dengan model **User** (guru).

- [ ] **Model untuk Materi (Material)**:  
  - Buat model `Material` yang mencakup materi pelajaran (judul, deskripsi, file pendukung, dll).
  - Model `Material` dapat memiliki relasi **many-to-one** dengan `Class`.

- [ ] **Model untuk Kuis (Quiz)**:  
  - Buat model `Quiz` yang mencakup soal, jawaban, dan nilai.
  - Pastikan ada relasi **many-to-one** dengan `Class` dan `Material`.

- [ ] **Endpoint CRUD untuk Kelas**:  
  - Implementasikan endpoint untuk membuat, mengedit, menghapus, dan melihat kelas (`GET`, `POST`, `PUT`, `DELETE` untuk `/api/classes/`).

- [ ] **Endpoint CRUD untuk Materi**:  
  - Implementasikan endpoint untuk membuat, mengedit, menghapus, dan melihat materi pelajaran (`GET`, `POST`, `PUT`, `DELETE` untuk `/api/materials/`).

- [ ] **Endpoint CRUD untuk Kuis**:  
  - Implementasikan endpoint untuk membuat, mengedit, menghapus, dan melihat kuis (`GET`, `POST`, `PUT`, `DELETE` untuk `/api/quizzes/`).

---

### 3. Integrasi Chatbot AI
- [ ] **Integrasi OpenAI API untuk Chatbot**:  
  - Gunakan **OpenAI API** untuk chatbot berbasis **GPT-3** atau **GPT-4** untuk menjawab pertanyaan terkait materi.
  - Buat endpoint yang menerima input dan mengirimkan response dari chatbot.

- [ ] **Model untuk Percakapan Chatbot**:  
  - Buat model untuk menyimpan percakapan antara pengguna (siswa atau guru) dan chatbot, misalnya `ChatHistory`.

- [ ] **Endpoint Chatbot**:  
  - Implementasikan endpoint untuk berinteraksi dengan chatbot menggunakan query/response (`POST /api/chatbot/`).

---

### 4. Pengujian dan Dokumentasi
- [ ] **Testing Unit untuk Model, Serializer, dan Views**:  
  - Gunakan **`pytest`** atau **`unittest`** untuk melakukan pengujian unit pada model dan serializer.
  - Uji endpoint API dengan menggunakan **Postman** untuk memastikan setiap endpoint berfungsi dengan baik.

- [ ] **Dokumentasi API**:  
  - Gunakan **Swagger** atau **DRF Spectacular** untuk mendokumentasikan endpoint API.
  - Pastikan dokumentasi API jelas dan dapat digunakan oleh tim frontend.

- [ ] **Menulis Test untuk Endpoint CRUD**:  
  - Tulis pengujian untuk endpoint CRUD (kelas, materi, kuis) dan pastikan validasi dan hak akses berjalan dengan baik.

---

### 5. Pengaturan dan Keamanan
- [ ] **Setup CORS**:  
  - Pastikan CORS (Cross-Origin Resource Sharing) diatur dengan benar di `settings.py` agar frontend bisa mengakses API.
  - Gunakan **`django-cors-headers`** untuk mengatur CORS dengan lebih fleksibel.

- [ ] **Pengaturan Environment Variables**:  
  - Gunakan **`python-dotenv`** atau **`.env`** untuk menyimpan variabel lingkungan seperti **`SECRET_KEY`**, **`DATABASE_PASSWORD`**, dan kunci **API key** untuk chatbot.

- [ ] **Logger dan Error Handling**:  
  - Setup logging untuk aplikasi menggunakan **`logging`** module untuk menangani error dan logging aktivitas aplikasi.
  - Buat penanganan error yang baik untuk memastikan respon error yang informatif dan standar.

- [ ] **Penyimpanan File**:  
  - Implementasi penyimpanan file materi (misalnya PDF, gambar, dll) menggunakan **`django-storages`** atau server lokal, sesuai dengan kebutuhan.

---

### 6. Deployment
- [ ] **Deployment ke Server**:  
  - Siapkan aplikasi untuk deployment ke **Heroku**, **AWS**, atau **DigitalOcean**.
  - Gunakan **Docker** untuk membungkus aplikasi backend dalam kontainer, agar lebih mudah di-deploy dan dikelola.

- [ ] **CI/CD Pipeline**:  
  - Buat pipeline CI/CD menggunakan **GitHub Actions**, **GitLab CI**, atau **Jenkins** untuk otomatisasi build dan deployment backend.

- [ ] **Testing di Production**:  
  - Setelah deployment, lakukan pengujian di server produksi dan pastikan semua berjalan dengan lancar.

---

### 7. Refactor dan Pemeliharaan Kode
- [ ] **Refactor Kode untuk Keterbacaan dan Efisiensi**:  
  - Refactor kode yang sudah ditulis, optimalkan query database, dan pastikan tidak ada kode yang redundan.

- [ ] **Update Dependencies**:  
  - Perbarui semua dependensi dan pastikan bahwa tidak ada masalah keamanan yang terdeteksi pada package yang digunakan.

- [ ] **Menambah Fitur Baru Berdasarkan Feedback**:  
  - Berdasarkan feedback dari tim atau pengguna, tambahkan fitur tambahan, seperti pencarian materi, pencarian kuis, atau filter kelas.

---

### 8. Dokumentasi dan Laporan
- [ ] **Menyusun Dokumentasi Backend**:  
  - Tulis dokumentasi pengaturan backend untuk developer lain dan tim yang akan mengelola aplikasi ke depannya.
  - Sertakan cara setup project, menjalankan server, dan menguji API.

- [ ] **Laporan Akhir**:  
  - Buat laporan proyek yang menjelaskan proses pengembangan, teknologi yang digunakan, dan fitur-fitur utama yang telah dikembangkan.