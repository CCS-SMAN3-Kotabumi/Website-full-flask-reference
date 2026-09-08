from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import Admin, Pendaftar, Pengurus

bp = Blueprint('admin', __name__, url_prefix='/admin')

_ALLOWED_STATUS = ('menunggu', 'diterima', 'ditolak')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Login admin."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin.dashboard'))
        flash('Nama user atau password tidak ia.', 'error')

    return render_template('admin/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Logout admin."""
    logout_user()
    return redirect(url_for('admin.login'))


@bp.route('/')
@login_required
def dashboard():
    """Dashboard admin: list pendaftar. Data pendaftar privat hanya admin yang dapat lihat."""
    pendaftar_list = Pendaftar.query.order_by(Pendaftar.id.desc()).all()
    return render_template('admin/dashboard.html', pendaftar_list=pendaftar_list)


@bp.route('/pendaftar/<int:pid>/status', methods=('POST',))
@login_required
def set_status(pid):
    """Ubah status pendaftar (menunggu/diterima/ditolak)."""
    pendaftar = db.get_or_404(Pendaftar, pid)
    status = (request.form.get('status') or '').strip()
    if status in _ALLOWED_STATUS:
        pendaftar.status = status
        db.session.commit()
    return redirect(url_for('admin.dashboard'))


@bp.route('/pendaftar/<int:pid>/hapus', methods=('POST',))
@login_required
def hapus(pid):
    """Hapus pendaftar dari database."""
    pendaftar = db.get_or_404(Pendaftar, pid)
    db.session.delete(pendaftar)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


# ---------------------------------------------------------------------------
# CRUD Pengurus
# ---------------------------------------------------------------------------

def _parse_pengurus_form():
    """Lextrak data form Pengurus dengan validasi server-side."""
    nama = (request.form.get('nama') or '').strip()
    jabatan = (request.form.get('jabatan') or '').strip()
    deskripsi = (request.form.get('deskripsi') or '').strip()
    foto = (request.form.get('foto') or '').strip()

    urutan_raw = (request.form.get('urutan') or '').strip()
    try:
        urutan = int(urutan_raw)
    except (TypeError, ValueError):
        urutan = 0

    return nama, jabatan, foto, deskripsi, urutan


def _validate_pengurus(nama, jabatan):
    """Return list error message."""
    errors = []
    if not nama:
        errors.append('Nama wajib diisi.')
    if len(nama) > 120:
        errors.append('Nama tidak boleh lebih dari 120 karakter.')
    if not jabatan:
        errors.append('Jabatan wajib diisi.')
    if len(jabatan) > 120:
        errors.append('Jabatan tidak boleh lebih dari 120 karakter.')
    return errors


@bp.route('/pengurus')
@login_required
def list_pengurus():
    """Daftar Pengurus, urutkan berdasarkan `urutan`."""
    pengurus_list = Pengurus.query.order_by(Pengurus.urutan.asc(), Pengurus.id.asc()).all()
    return render_template('admin/pengurus.html', pengurus_list=pengurus_list)


@bp.route('/pengurus/tambah', methods=('GET', 'POST'))
@login_required
def tambah_pengurus():
    """Form tambah Pengurus."""
    if request.method == 'POST':
        nama, jabatan, foto, deskripsi, urutan = _parse_pengurus_form()
        errors = _validate_pengurus(nama, jabatan)
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template('admin/pengurus_form.html', pengurus=None,
                                   nama=nama, jabatan=jabatan, foto=foto,
                                   deskripsi=deskripsi, urutan=urutan)
        pengurus = Pengurus(nama=nama, jabatan=jabatan, foto=foto or None,
                            deskripsi=deskripsi or None, urutan=urutan)
        db.session.add(pengurus)
        db.session.commit()
        return redirect(url_for('admin.list_pengurus'))

    return render_template('admin/pengurus_form.html', pengurus=None,
                           nama='', jabatan='', foto='', deskripsi='', urutan=0)


@bp.route('/pengurus/<int:pid>/edit', methods=('GET', 'POST'))
@login_required
def edit_pengurus(pid):
    """Edit data Pengurus."""
    pengurus = db.get_or_404(Pengurus, pid)
    if request.method == 'POST':
        nama, jabatan, foto, deskripsi, urutan = _parse_pengurus_form()
        errors = _validate_pengurus(nama, jabatan)
        if errors:
            for message in errors:
                flash(message, 'error')
            return render_template('admin/pengurus_form.html', pengurus=pengurus,
                                   nama=nama, jabatan=jabatan, foto=foto,
                                   deskripsi=deskripsi, urutan=urutan)
        pengurus.nama = nama
        pengurus.jabatan = jabatan
        pengurus.foto = foto or None
        pengurus.deskripsi = deskripsi or None
        pengurus.urutan = urutan
        db.session.commit()
        return redirect(url_for('admin.list_pengurus'))

    return render_template('admin/pengurus_form.html', pengurus=pengurus,
                           nama=pengurus.nama, jabatan=pengurus.jabatan,
                           foto=pengurus.foto or '', deskripsi=pengurus.deskripsi or '',
                           urutan=pengurus.urutan)


@bp.route('/pengurus/<int:pid>/hapus', methods=('POST',))
@login_required
def hapus_pengurus(pid):
    """Hapus Pengurus dari database."""
    pengurus = db.get_or_404(Pengurus, pid)
    db.session.delete(pengurus)
    db.session.commit()
    return redirect(url_for('admin.list_pengurus'))