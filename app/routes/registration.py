from urllib.parse import quote

from flask import Blueprint, flash, redirect, request, url_for

from app.extensions import db
from app.models import Pendaftar

bp = Blueprint('registration', __name__)


# Nomor WhatsApp tujuan, sama seperti yang digunakan JavaScript existing.
WA_NUMBER = '6285384870428'


@bp.route('/daftar', methods=('GET', 'POST'))
def daftar():
    """Proses form pendaftaran secara server-side."""
    if request.method == 'POST':
        nama = request.form.get('nama', '' ).strip()
        kelas = request.form.get('kelas', '' ).strip()
        minat = request.form.get('minat', '' ).strip()
        alasan = request.form.get('alasan', '' ).strip()

        errors = []
        if not nama:
            errors.append('Nama lengkap wajib diisi.')
        if not kelas:
            errors.append('Kelas wajib diisi.')
        if not minat:
            errors.append('Minat utama wajib dipilih.')
        if not alasan:
            errors.append('Alasan bergabung wajib diisi.')

        if not errors:
            pendaftar = Pendaftar(
                nama=nama,
                kelas=kelas,
                minat=minat,
                alasan=alasan,
            )
            db.session.add(pendaftar)
            db.session.commit()

            pesan = (
                'Halo, saya ingin mendaftar sebagai anggota CCS.%0A%0A'
                'Nama: ' + quote(nama) + '%0A'
                'Kelas: ' + quote(kelas) + '%0A'
                'Minat utama: ' + quote(minat) + '%0A'
                'Alasan bergabung: ' + quote(alasan)
            )
            wa_url = 'https://wa.me/' + WA_NUMBER + '?text=' + pesan
            return redirect(wa_url)

        for message in errors:
            flash(message, 'error')
        return redirect(url_for('main.index', _anchor='daftar'))

    # GET /daftar langsung balik ke beranda
    return redirect(url_for('main.index'))