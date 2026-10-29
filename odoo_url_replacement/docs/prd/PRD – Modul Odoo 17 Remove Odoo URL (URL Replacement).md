# PRD – Modul Odoo 18: Remove Odoo URL (remove\_odoo\_url)

Penulis: Arif N Ramadhan | Niits Inovasi Teknologi · Versi dokumen: 1.0 (Draft) · Target: Odoo 18.0 · Lisensi: OPL-1 · Harga: Free · Website: www.niits.id

## 1. Ringkasan

Modul ini **mengganti segmen `/odoo`** pada URL backend Odoo 18 dengan teks brand pilihan admin. Contoh: `https://bisnisanda.com/odoo/action-250` menjadi `https://bisnisanda.com/namabrand/action-250`, dan halaman utama `https://bisnisanda.com/odoo` menjadi `https://bisnisanda.com/namabrand`. Tujuannya white-labeling: pengguna melihat sistem ERP seolah-olah aplikasi internal perusahaan.

Pengaturan menyatu di **Settings → General Settings** tanpa menu terpisah, dapat diaktifkan/dinonaktifkan dengan satu klik, dan memakai *safe default* (nonaktif) bila konfigurasi belum ada atau hilang.

## 2. Referensi URL Odoo 18

Tabel berikut memetakan URL bawaan Odoo 18 ke URL bermerek, dengan asumsi brand = `namabrand`.

| URL bawaan Odoo 18 | Dengan modul | Keterangan |
| --- | --- | --- |
| `/odoo` | `/namabrand` | Halaman utama backend |
| `/odoo/action-250` | `/namabrand/action-250` | Action tertentu |
| `/odoo/action-250/12` | `/namabrand/action-250/12` | Record di dalam action |
| `/web` | `/namabrand` | Jalur legacy, diarahkan langsung ke URL bermerek |
| `/web/login` | `/web/login` | Tidak berubah, path tidak mengandung kata odoo |
| `/web/*`, `/mail/*`, `/websocket`, `/jsonrpc` | Tidak berubah | Endpoint teknis di luar cakupan |

Keputusan desain: nama teknis modul `remove_odoo_url`, cakupan hanya backend, pendekatan modul murni (route alias + override `ir.http` + patch JS), dan setelan di General Settings.

## 3. Latar Belakang dan Masalah

| Masalah | Dampak |
| --- | --- |
| Semua URL backend Odoo 18 diawali `/odoo` | Sistem langsung dikenali sebagai Odoo oleh siapa pun yang melihat address bar atau tautan yang dibagikan |
| Tautan yang dibagikan lewat chat atau email membawa kata `odoo` | Kesan white-label hilang di komunikasi eksternal |
| Tidak ada pengaturan bawaan untuk mengganti segmen ini | Perusahaan harus memakai rewrite di reverse proxy yang butuh akses server |

## 4. Tujuan dan Non-Tujuan

### 4.1 Tujuan

1. Segmen `/odoo` pada URL backend tampil sebagai brand pilihan admin.
2. Fitur dapat di-ON/OFF dari General Settings tanpa restart server.
3. Teks brand bebas ditentukan admin dengan validasi yang aman.
4. Tidak menimbulkan error bila konfigurasi kosong atau rusak.
5. Tidak merusak fungsi bawaan Odoo 18: login, deep link, tautan email, mode debug, RPC, dan navigasi web client.

### 4.2 Non-Tujuan (Out of Scope)

- URL website, e-commerce, dan portal (`/shop`, `/contactus`, `/my`).
- Halaman database selector/manager (`/web/database/*`).
- Alias untuk halaman login: `/web/login` tetap bawaan (lihat pertanyaan terbuka).
- Endpoint teknis dan aset: `/web/*`, `/mail/*`, `/websocket`, `/jsonrpc`, `/xmlrpc`, `/report/*`, `/scoped_app`. Endpoint ini **tidak diubah** agar stabil dan kompatibel dengan modul pihak ketiga.
- Mengubah tautan yang dibuat server (email, chatter) di titik pembuatannya. Tautan `/odoo/...` lama cukup diarahkan oleh redirect.
- Mengganti logo, judul tab, favicon, atau teks Powered by Odoo (modul terpisah).
- Brand berbeda per website atau per company (brand berlaku per database).
- Menyembunyikan total jejak Odoo di source code halaman atau header HTTP.

## 5. Persona Pengguna

| Persona | Kebutuhan |
| --- | --- |
| Administrator Odoo | Mengatur brand dan toggle dari UI tanpa akses server |
| Karyawan / pengguna internal | Mengakses dan membagikan tautan bermerek perusahaan |
| Implementator / partner Odoo | Modul ringan, stabil, mudah diinstal, tanpa konfigurasi proxy |

## 6. Fitur Utama

### F1 – Easy Toggle (On/Off)

- Sakelar **Enable URL Replacement** di General Settings.
- Nilai tersimpan di `ir.config_parameter`; efek berlaku segera setelah Save (cache di-refresh, tanpa restart).
- Saat OFF, perilaku Odoo 18 kembali 100% bawaan, termasuk tidak ada redirect.

### F2 – Custom Brand Text

- Field **Brand Text**, tampil dan wajib diisi hanya ketika toggle ON.
- Aturan validasi:
  - Hanya huruf kecil `a-z`, angka `0-9`, dan tanda hubung `-`; panjang 2–32 karakter; tidak diawali atau diakhiri `-`.
  - Input dinormalisasi otomatis: trim, lowercase, spasi menjadi `-`.
  - Brand berada di segmen pertama path, jadi **tidak boleh bentrok dengan route root** Odoo. Ditolak: `odoo`, `web`, `website`, `my`, `shop`, `mail`, `scoped_app`, `doc`, `report`, `static`, `base`, `longpolling`, `websocket`, `jsonrpc`, `xmlrpc`, `survey`, `calendar`, `payment`, serta setiap segmen pertama yang sudah ada di routing map aktif.
- Pesan error ditampilkan lewat `ValidationError` yang jelas dan dapat diterjemahkan.

### F3 – Settings Integration

- Blok baru **URL Replacement Settings** pada `res.config.settings`, ditempatkan lewat inherit view General Settings (`base_setup.res_config_settings_view_form`) di dekat blok Developer Tools.
- Field memakai `config_parameter`:
  - `remove_odoo_url.enabled` (Boolean, default `False`)
  - `remove_odoo_url.brand_text` (Char, default kosong)
- Hanya grup **Settings / Administration** (`base.group_system`) yang dapat mengubahnya.

### F4 – Secure & Safe (Safe Default)

- Jika parameter tidak ada, kosong, tidak valid, atau toggle OFF → modul **tidak melakukan apa pun** (mode bawaan Odoo).
- Pembacaan konfigurasi dibungkus penanganan error; kegagalan dicatat di log (warning) dan tidak pernah menghasilkan HTTP 500.
- Tidak mengubah autentikasi, hak akses, atau session.

## 7. Perilaku URL (Functional Requirements)

Misal brand = `namabrand` dan toggle ON.

| ID | Skenario | Perilaku yang diharapkan |
| --- | --- | --- |
| FR-01 | GET `/namabrand` | Menampilkan web client Odoo (setara `/odoo`) |
| FR-02 | GET `/namabrand/action-250` dan `/namabrand/action-250/12` | Membuka action dan record yang sama seperti `/odoo/action-250` dan `/odoo/action-250/12` |
| FR-03 | GET `/odoo` atau `/odoo/<path>` (URL lama, bookmark, tautan email) | Redirect 302 ke `/namabrand` atau `/namabrand/<path>`; query string dipertahankan |
| FR-04 | GET `/web` (jalur legacy, termasuk `/web#action=...`) | Redirect langsung ke `/namabrand`, tanpa rantai `/web` → `/odoo` → `/namabrand`; hash fragment dipertahankan browser |
| FR-05 | Login via `/web/login` sukses | Redirect ke `/namabrand`, atau ke parameter `redirect` yang aman (diubah ke bentuk bermerek bila berawalan `/odoo`) |
| FR-06 | Belum login membuka `/namabrand/action-250` | Diarahkan ke `/web/login?redirect=...`, lalu kembali ke `/namabrand/action-250` setelah login |
| FR-07 | Logout | Alur bawaan Odoo ke halaman login; tidak ada URL `/odoo` yang muncul |
| FR-08 | Navigasi di web client (ganti menu, aksi, record) | Address bar selalu berformat `/namabrand/...`; tidak pernah kembali ke `/odoo` |
| FR-09 | Mode debug `?debug=1` atau `?debug=assets` | Tetap berfungsi pada URL bermerek; parameter tidak hilang |
| FR-10 | Endpoint teknis (RPC, aset, websocket, report, `/mail/*`, `/scoped_app`) | Tidak terpengaruh dan tidak diberi prefix brand |
| FR-11 | Tautan notifikasi email (`/mail/view?...`) | Tetap sampai ke record tujuan; URL akhir di address bar bermerek |
| FR-12 | GET `/salah/action-250` (brand tidak cocok) | 404 standar Odoo |
| FR-13 | Toggle OFF | `/namabrand` menjadi 404; `/odoo` bekerja normal tanpa redirect |
| FR-14 | Brand diubah dari A ke B | `/B` aktif langsung; `/A` tidak lagi valid |
| FR-15 | Konfigurasi hilang atau rusak | Odoo berjalan normal seperti tanpa modul |

Catatan: redirect FR-03 dan FR-04 hanya berlaku untuk request navigasi `GET` yang menerima HTML. Request `POST`, JSON-RPC, dan request non-HTML tidak diredirect.

## 8. Rancangan Teknis

### 8.1 Informasi Modul

| Item | Nilai |
| --- | --- |
| Nama tampilan | Remove Odoo URL |
| Nama teknis | `remove_odoo_url` |
| Versi manifest | `18.0.1.0.0` |
| Depends | `web`, `base_setup` |
| Lisensi | OPL-1 |
| Author / Website | Arif N Ramadhan – Niits Inovasi Teknologi / https://www.niits.id |
| Price | Free |
| Application | False (modul utilitas) |

### 8.2 Struktur Direktori

```
remove_odoo_url/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── res_config_settings.py   # field toggle + brand, validasi, clear cache
│   └── ir_http.py               # alias route: /brand/... -> /odoo/..., session_info
├── controllers/
│   ├── __init__.py
│   └── main.py                  # redirect /odoo dan /web -> /brand, login redirect
├── views/
│   └── res_config_settings_views.xml
├── static/src/js/
│   └── router_brand_patch.js    # patch router web client
├── static/description/          # icon.png, index.html
└── i18n/                        # id.po (opsional)
```

### 8.3 Komponen

**a) Settings (`res.config.settings`)**

- `url_replacement_enabled = fields.Boolean(config_parameter='remove_odoo_url.enabled')`
- `url_replacement_brand_text = fields.Char(config_parameter='remove_odoo_url.brand_text')`
- Validasi dan normalisasi brand pada `set_values`; setelah simpan panggil `self.env.registry.clear_cache()` agar nilai terbaru dipakai.

**b) Override `ir.http` (route alias)**

- Override `_match` (atau titik setara pada `_pre_dispatch`) untuk: jika fitur aktif dan path sama dengan `/<brand>` atau diawali `/<brand>/`, tulis ulang path menjadi `/odoo` ditambah sisanya sebelum dicocokkan ke routing map. Dengan cara ini route `Home.web_client` bawaan (`/odoo` dan `/odoo/<path:subpath>`) dipakai ulang tanpa duplikasi.
- Nilai konfigurasi di-cache pada level registry (`ormcache`) agar tiap request tidak membebani database; cache di-invalidate saat Settings disimpan.
- Seluruh blok dibungkus `try/except` → fallback ke perilaku bawaan.
- Override `session_info` untuk mengirim brand ke front-end (kunci mis. `remove_odoo_url_brand`; hanya ada bila fitur aktif).

**c) Controller**

- Override `Home.web_client` agar GET `/odoo`, `/odoo/<path>`, dan `/web` diredirect 302 ke URL bermerek (FR-03, FR-04). Keputusan redirect memakai **path asli request** (`request.httprequest.path`), bukan path hasil tulis ulang, supaya request yang datang lewat `/<brand>` tidak masuk ke loop redirect.
- Override `_login_redirect` agar tujuan default setelah login adalah `/<brand>` (FR-05); parameter `redirect` berawalan `/odoo` dikonversi ke bentuk bermerek.
- Semua redirect hanya ke path relatif internal untuk mencegah open redirect.

**d) JavaScript (web client)**

- Patch router web client (`@web/core/browser/router`, fungsi pembangun dan pembaca URL seperti `stateToUrl` dan `urlToState`) agar prefix yang dipakai adalah brand dari session info, bukan `odoo`, baik saat membaca URL awal maupun saat `pushState`/`replaceState`.
- Ganti pengalihan hardcode ke `/odoo` pada web client (mis. setelah ganti company, kembali ke home) agar memakai brand.
- Bila brand tidak ada di session info, patch tidak aktif (safe default).
- Fallback: saat boot, jika `location.pathname` berawalan `/odoo` dan fitur aktif, jalankan `history.replaceState` ke URL bermerek.

### 8.4 Catatan Implementasi yang Perlu Diverifikasi (Technical Spike)

Sebelum coding penuh, verifikasi di Odoo 18.0 (build terbaru) karena nama fungsi internal bisa bergeser:

1. Titik override routing yang paling stabil (`ir.http._match` vs `_pre_dispatch`) dan perilaku converter `model`/`models` pada path `/odoo/<path:subpath>`.
2. Nama dan perilaku fungsi di `router.js` yang menangani prefix `odoo` (termasuk konversi hash legacy `/web#...`).
3. Seluruh hardcode `/odoo` di JS dan Python addon inti (`web`, `mail`, `portal`, `website`) lewat pencarian kode, untuk memastikan tidak ada yang lolos dari redirect.
4. Interaksi dengan multi-company switcher, fitur Login as, dan PWA manifest (`/scoped_app`, start\_url).
5. Penempatan blok setelan di view General Settings Odoo 18 (anchor id blok Developer Tools).

## 9. Alur Penggunaan

### 9.1 Aktivasi dan Konfigurasi

1. Masuk ke **Settings → General Settings**.
2. Gulir ke bagian **URL Replacement Settings**.
3. Aktifkan sakelar **Enable URL Replacement** (ON).
4. Isi **Brand Text** (contoh: `namaperusahaan`).
5. Klik **Save**. Segmen `/odoo` pada URL sistem langsung digantikan oleh brand yang diisi.

### 9.2 Pemecahan Masalah

| Gejala | Langkah |
| --- | --- |
| URL masih menampilkan `/odoo` atau tampilan tidak berubah | Buka Settings → Developer Tools → **Activate the developer mode (with assets)** agar aset frontend diregenerasi |
| Browser masih membaca URL atau cache lama | Buka via **Incognito**, atau Logout lalu Login kembali; bila perlu hard refresh (Ctrl+Shift+R) |
| Halaman 404 setelah mengganti brand | Pastikan brand baru yang dipakai di URL, bukan brand lama; perbarui bookmark |
| Brand ditolak saat Save | Periksa aturan karakter dan daftar kata reserved (fitur F2) |
| Terkunci dari sistem | Akses `/odoo` lama tetap diredirect; bila tetap gagal, nonaktifkan lewat database (bagian 9.3) |

### 9.3 Prosedur Darurat (Recovery)

Jika administrator tidak dapat mengakses sistem, nonaktifkan fitur lewat SQL:

```sql
UPDATE ir_config_parameter
SET value = 'False'
WHERE key = 'remove_odoo_url.enabled';
```

Lalu restart service Odoo atau clear cache registry. Prosedur ini dicantumkan di dokumentasi modul. Pada kondisi normal rute `/odoo` lama tidak dihapus (hanya diredirect), sehingga risiko terkunci sangat kecil.

## 10. Kebutuhan Non-Fungsional

| Aspek | Persyaratan |
| --- | --- |
| Kompatibilitas | Odoo 18.0 Community dan Enterprise; Python 3.10+ |
| Performa | Penambahan latensi routing 1 ms atau kurang per request (nilai di-cache) |
| Keamanan | Hanya `base.group_system` yang bisa mengubah setelan; tidak ada open redirect; tidak melewati autentikasi |
| Stabilitas | Tidak ada HTTP 500 akibat konfigurasi kosong atau rusak; fallback ke bawaan |
| Instalasi/uninstall | Install tanpa migrasi data; uninstall mengembalikan 100% perilaku bawaan (`uninstall_hook` menghapus parameter) |
| Multi-database | Konfigurasi per database (parameter disimpan di DB masing-masing) |
| Kompatibilitas modul lain | Endpoint teknis tidak diubah, sehingga aman bagi modul pihak ketiga |
| i18n | Teks UI siap terjemah; terjemahan Bahasa Indonesia opsional (`id.po`) |
| Reverse proxy | Tidak memerlukan perubahan Nginx/Apache; path brand ditangani di level aplikasi |

## 11. Kriteria Penerimaan dan Skenario Uji

| ID | Uji | Hasil yang diharapkan |
| --- | --- | --- |
| UT-01 | Install modul pada DB baru | Berhasil tanpa error; fitur default OFF; Odoo berjalan seperti biasa |
| UT-02 | Toggle ON + brand valid, Save | `/brand` dan `/brand/action-250` terbuka (FR-01, FR-02) |
| UT-03 | Buka `/odoo` dan `/odoo/action-250` saat ON | Redirect ke `/brand` dan `/brand/action-250`, query string terjaga (FR-03) |
| UT-04 | Buka `/web` dan `/web#action=250` saat ON | Redirect langsung ke `/brand` tanpa rantai redirect (FR-04) |
| UT-05 | Login dan logout | Alur sesuai FR-05, FR-06, FR-07 |
| UT-06 | Navigasi antar menu dan record, tombol Back/Forward browser | Address bar selalu `/brand/...`; Back/Forward berfungsi (FR-08) |
| UT-07 | `?debug=assets` pada URL bermerek | Mode debug aktif, URL tetap bermerek (FR-09) |
| UT-08 | Brand tidak valid (spasi, simbol, reserved, kurang dari 2 karakter) | Ditolak dengan pesan jelas |
| UT-09 | Hapus parameter config dari DB | Odoo normal, tanpa error (F4, FR-15) |
| UT-10 | Toggle OFF | `/odoo` normal, `/brand` 404 (FR-13) |
| UT-11 | Ganti brand A ke B | `/B` aktif, `/A` 404 (FR-14) |
| UT-12 | User non-admin mencoba mengubah setelan | Tidak dapat melihat atau menyimpan blok pengaturan |
| UT-13 | RPC, report PDF, upload/download attachment, websocket (Discuss) | Berfungsi normal (FR-10) |
| UT-14 | Klik tautan notifikasi email dan tautan chatter ke record | Sampai ke record tujuan di URL bermerek (FR-11) |
| UT-15 | Multi-company switcher dan Login as | Tidak memutus URL bermerek |
| UT-16 | Uninstall modul | URL kembali bawaan, parameter terhapus |

## 12. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Perubahan internal `router.js` antar-build Odoo 18 | Address bar kembali ke `/odoo` atau navigasi rusak | Fallback `replaceState`; spike teknis; uji pada beberapa build |
| Brand bentrok dengan route root yang ada | Halaman lain tidak bisa diakses | Validasi terhadap routing map dan daftar reserved |
| Hardcode `/odoo` di modul pihak ketiga | Tautan kembali ke URL lama | Redirect otomatis `/odoo/...` ke URL bermerek menjaga alur tetap jalan |
| Loop redirect antara `/odoo` dan `/brand` | Halaman tidak bisa dibuka | Keputusan redirect memakai path asli request; uji khusus UT-03 |
| Cache browser atau proxy menyimpan redirect lama | Pengguna melihat URL lama | Gunakan 302 (bukan 301); dokumentasi troubleshooting |
| Reverse proxy atau WAF membatasi path tertentu | `/brand` terblokir | Dokumentasikan bahwa path baru harus diizinkan |
| Salah konfigurasi mengunci admin | Tidak bisa login | Rute `/odoo` lama tetap aktif sebagai redirect; prosedur recovery SQL |

## 13. Metrik Keberhasilan

- 100% skenario uji UT-01 sampai UT-16 lulus.
- Nol HTTP 500 terkait modul pada uji regresi login, logout, dan navigasi.
- Waktu konfigurasi oleh admin tidak lebih dari 1 menit (maksimal 5 langkah di General Settings).
- Tidak ada fungsi bawaan Odoo 18 yang rusak setelah modul terpasang (regresi = 0).

## 14. Rencana Rilis (Usulan)

| Fase | Aktivitas | Estimasi |
| --- | --- | --- |
| 1 | Technical spike (routing `ir.http` dan `router.js` Odoo 18) | 1–2 hari |
| 2 | Settings, validasi, safe default | 1 hari |
| 3 | Override routing dan controller redirect | 2 hari |
| 4 | Patch JS web client (router, hardcode `/odoo`) | 2 hari |
| 5 | Pengujian (UT-01 sampai UT-16) dan perbaikan | 2 hari |
| 6 | Dokumentasi, ikon, halaman deskripsi, rilis OPL-1 | 1 hari |

## 15. Pertanyaan Terbuka

1. Apakah `/web/login` perlu alias bermerek (mis. `/brand/login`)? Default PRD ini: tidak, karena path login tidak mengandung kata odoo.
2. Apakah URL lama `/odoo` selalu diredirect, atau ada opsi soft mode yang membiarkannya tetap bisa diakses tanpa redirect?
3. Apakah cakupan diperluas ke portal (`/my`) dan website pada versi 18.0.2?
4. Apakah brand perlu dibedakan per company atau per website pada rilis berikutnya?

## 16. Lampiran – Teks Deskripsi Modul (untuk Apps Store)

**Remove Odoo URL** mengganti segmen `/odoo` pada URL backend Odoo 18 dengan nama brand Anda, sehingga `https://bisnisanda.com/odoo/action-250` tampil sebagai `https://bisnisanda.com/namabrand/action-250`. Aktifkan atau nonaktifkan dengan satu klik dari General Settings, tentukan teks brand sesuai keinginan, dan nikmati sistem yang tetap aman karena otomatis kembali ke mode bawaan bila konfigurasi tidak tersedia.

*Author: Arif N Ramadhan | Niits Inovasi Teknologi · Price: Free · Website: www.niits.id · License: OPL-1*
