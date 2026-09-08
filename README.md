# Website CCS — Flask + Jinja2

Migrasi backend dari website statis ( HTML + CSS + JavaScript) menjadi aplikasi **Flask + Jinja2 + SQLite**. Desain, CSS, dan JavaScript UI/UX dipertahankan apa adanya — hanya arsitektur backend yang diubah.

## Struktur

```
├── app/
│   ├── __init__.py          # application factory
│   ├── models.py             # Pendaftar, Admin
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          # GET /
│   │   ├── admin.py         # GET /admin (placeholder)
│   │   └── registration.py  # GET/POST /daftar
│   ├── templates/
│   │   ├── base.html        # struktur umum (head, nav, footer, script)
│   │   └── index.html       # konten halaman utama
│   └── static/
│       ├── css/style.css
│       ├── js/script.js
│       └── images/          # (disiapkan untuk aset nanti)
├── migrations/              # migrasi Alembic (Flask-Migrate)
├── tests/
│   └── test_app.py
├── config.py
├── run.py
├── requirements.txt
└── .env
```

## Cara menjalankan

```bash
pip install -r requirements.txt

# inisialisasi database:
flask db upgrade

# jalankan:
python run.py
# atau:
python -m flask run
```

Buka `http://127.0.0.1:5000`.

## Form pendaftaran

- Form `POST /daftar` divalidasi dan disimpan ke SQLite oleh Flask.
- Setelah valid dan tersimpan, pengguna diarahkan ke WhatsApp ( nomor yang sama dengan JavaScript existing).
- JavaScript hanya untuk UI/UX; validasi utama dilakukan di server.

## Catatan

- File statis asing (`index.html`, `CSS/`, `js/`) di root dipertahankan apa adanya sebagai sumber/perbandingan dan tidak dipakai oleh Flask.
- Design/warna/responsive layout tidak diubah.