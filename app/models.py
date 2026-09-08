from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Pendaftar(db.Model):
    """Pendaftar anggota CCS (hasil form pendaftaran."""
    __tablename__ = 'pendaftar'

    # Status mendafter: menunggu / diterima / ditolak
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(50), nullable=False)
    minat = db.Column(db.String(120), nullable=False)
    alasan = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='menunggu')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Pendaftar {self.nama}>'


class Admin(UserMixin, db.Model):
    """Akun admin pengelola website."""
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


class Pengurus(db.Model):
    """Pengurus/struktur organisasi CCS.

    `foto` menyimpan path/URL aset (optional). Sistem upload file belum
    dibuat pada tahap ini (TODO); field foto digunakan sebagai text untuk
    path asset yang sudah ada.
    """
    __tablename__ = 'pengurus'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(120), nullable=False)
    jabatan = db.Column(db.String(120), nullable=False)
    foto = db.Column(db.String(255), nullable=True)
    deskripsi = db.Column(db.Text, nullable=True)
    urutan = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Pengurus {self.nama}>'