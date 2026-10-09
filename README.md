# UTS Augmented Reality — Marker Based

Demo augmented reality berbasis marker Hiro menggunakan A-Frame dan AR.js. Saat marker terdeteksi, model 3D bebek dari `models/Duck.glb` tampil dan berputar di atas marker.

## Menjalankan di komputer

Kamera tidak dapat diakses dengan membuka `index.html` langsung melalui `file://`. Jalankan proyek melalui server lokal:

1. Buka terminal pada folder proyek.
2. Jalankan salah satu perintah berikut:

   ```powershell
   py -m http.server 8000
   ```

   Jika perintah `py` tidak tersedia, gunakan ekstensi **Live Server** di VS Code dan pilih **Open with Live Server**.
3. Buka <http://localhost:8000> di browser.
4. Izinkan akses kamera ketika browser meminta izin.
5. Klik **Perbesar layar** jika ingin tampilan fullscreen.
6. Tampilkan atau cetak `marker/Marker.jpg`, lalu arahkan kamera ke marker tersebut.

Jika tampilan kamera hitam, pastikan izin kamera untuk situs `localhost` diaktifkan pada browser dan tidak ada aplikasi lain yang sedang memakai kamera. Muat ulang halaman setelah mengubah izin. Tombol fullscreen di halaman menggunakan fullscreen browser biasa; mode VR tidak diperlukan.

Petunjuk pelacakan di bagian bawah layar menyarankan arah kamera dan jarak awal. Saat marker terdeteksi, petunjuk berubah menjadi konfirmasi; tahan kamera tetap stabil. Jika marker terlepas, luruskan kamera, pastikan seluruh marker terlihat, dan tambah pencahayaan.

Model bebek diarahkan ke luar dari permukaan marker dan berputar pada sumbu tengahnya.

Untuk menghentikan server Python, kembali ke terminal lalu tekan `Ctrl+C`.

## Deploy ke GitHub Pages

Proyek ini menggunakan workflow GitHub Actions di `.github/workflows/deploy-pages.yml`. Setiap push ke branch `main` akan menerbitkan halaman.

1. Buka **Settings → Pages** di repository, lalu pilih **GitHub Actions** pada bagian **Build and deployment → Source**.
2. Push file proyek ini ke branch `main` repository.
3. Buka tab **Actions** dan tunggu workflow **Deploy AR marker to GitHub Pages** selesai.
4. Buka URL `https://holanpasaribu12.github.io/UAS/`.
5. Izinkan akses kamera. Di perangkat lain, buka atau cetak `marker/Marker.jpg` untuk dipindai.

GitHub Pages menggunakan HTTPS, yang diperlukan browser untuk akses kamera. Pastikan perangkat memiliki kamera dan koneksi internet untuk memuat A-Frame serta AR.js dari CDN.

## Isi proyek

- `index.html` — halaman AR, scene A-Frame, deteksi marker Hiro, status, dan model.
- `models/Duck.glb` — model 3D yang muncul pada marker.
- `marker/Marker.jpg` — marker Hiro untuk dipindai.
