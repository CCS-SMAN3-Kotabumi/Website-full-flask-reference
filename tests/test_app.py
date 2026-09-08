import re

import pytest

from app import create_app
from app.extensions import db
from app.models import Admin, Pendaftar, Pengurus


@pytest.fixture
def app(tmp_path):
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-secret',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + str(tmp_path / 'test.db'),
    })
    with app.app_context():
        db.create_all()
        admin = Admin(username='admin')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


def get_csrf(resp):
    """Extrahe token CSRF dari rendered HTML."""
    m = re.search(r'name="csrf_token" value="([^"]+)"', resp.get_data(as_text=True))
    return m.group(1) if m else ''


def test_index_renders(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'Computer Club Smanthree' in res.data


def test_form_post_saves_pendaftar(client, app):
    # Form tanpa CSRF token -> 400 (CSRF aktif).
    res = client.post('/daftar', data={'nama': 'Budi', 'kelas': 'XI IPA 2',
                                       'minat': 'Pemrograman (Python / C++ / OSN)',
                                       'alasan': 'Ingin belajar'})
    assert res.status_code == 400

    # Dengan CSRF token -> valid, tersimpan, redirect ke WhatsApp.
    page = client.get('/')
    token = get_csrf(page)
    assert token != ''
    res = client.post('/daftar', data={'csrf_token': token, 'nama': 'Budi',
                                       'kelas': 'XI IPA 2',
                                       'minat': 'Pemrograman (Python / C++ / OSN)',
                                       'alasan': 'Ingin belajar'},
                      follow_redirects=False)
    assert res.status_code == 302
    assert 'wa.me' in res.headers['Location']
    with app.app_context():
        assert Pendaftar.query.count() == 1
        assert Pendaftar.query.first().status == 'menunggu'


def test_form_post_rejects_empty(client):
    page = client.get('/')
    token = get_csrf(page)
    res = client.post('/daftar', data={'csrf_token': token, 'nama': '', 'kelas': '',
                                       'minat': '', 'alasan': ''},
                      follow_redirects=False)
    assert res.status_code == 302
    assert 'daftar' in res.headers['Location']


def test_index_does_not_expose_pendaftar(client, app):
    # Pendaftar privat: tidak muncul pada halaman publik.
    unique = 'ZoMqXpRk'
    with app.app_context():
        db.session.add(Pendaftar(nama=unique, kelas='XI IPA 2', minat='Desain',
                                 alasan='private'))
        db.session.commit()
    res = client.get('/')
    assert unique.encode() not in res.data


def test_admin_requires_login(client):
    res = client.get('/admin/')
    assert res.status_code == 302
    assert 'admin/login' in res.headers['Location']


def test_admin_login_logout(client):
    # Login pakar -> dashboard.
    page = client.get('/admin/login')
    token = get_csrf(page)
    res = client.post('/admin/login', data={'csrf_token': token, 'username': 'admin',
                                            'password': 'secret'},
                      follow_redirects=False)
    assert res.status_code == 302
    assert '/admin/' in res.headers['Location']
    res = client.get('/admin/')
    assert res.status_code == 200
    assert b'Pendaftar CCS' in res.data

    # Logout -> redirect balik ke login.
    res = client.get('/admin/logout', follow_redirects=False)
    assert res.status_code == 302
    res = client.get('/admin/')
    assert res.status_code == 302


def test_admin_login_wrong_password(client):
    page = client.get('/admin/login')
    token = get_csrf(page)
    res = client.post('/admin/login', data={'csrf_token': token, 'username': 'admin',
                                            'password': 'wrong'},
                      follow_redirects=False)
    assert res.status_code == 200  # login form dengan flash error


def test_admin_change_status_and_delete(client, app):
    with app.app_context():
        p = Pendaftar(nama='Budi', kelas='XI IPA 2', minat='Desain', alasan='x')
        db.session.add(p)
        db.session.commit()
        pid = p.id

    # Login.
    page = client.get('/admin/login')
    token = get_csrf(page)
    client.post('/admin/login', data={'csrf_token': token, 'username': 'admin',
                                      'password': 'secret'})

    dash = client.get('/admin/')
    token = get_csrf(dash)
    res = client.post('/admin/pendaftar/%s/status' % pid,
                      data={'csrf_token': token, 'status': 'diterima'},
                      follow_redirects=False)
    assert res.status_code == 302
    with app.app_context():
        assert Pendaftar.query.get(pid).status == 'diterima'

    dash = client.get('/admin/')
    token = get_csrf(dash)
    res = client.post('/admin/pendaftar/%s/hapus' % pid,
                      data={'csrf_token': token}, follow_redirects=False)
    assert res.status_code == 302
    with app.app_context():
        assert Pendaftar.query.get(pid) is None


# --- CRUD Pengurus ---


def _login_admin(client):
    page = client.get('/admin/login')
    token = get_csrf(page)
    client.post('/admin/login', data={'csrf_token': token, 'username': 'admin',
                                      'password': 'secret'})


def test_pengurus_list_requires_login(client):
    res = client.get('/admin/pengurus')
    assert res.status_code == 302
    assert 'admin/login' in res.headers['Location']


def test_pengurus_tambah_and_list(client, app):
    _login_admin(client)

    # POST tanpa CSRF -> 400.
    res = client.post('/admin/pengurus/tambah',
                      data={'nama': 'Zendra', 'jabatan': 'Ketua', 'urutan': '1'})
    assert res.status_code == 400

    # Dengan CSRF -> tersimpan, redirect ke daftar.
    page = client.get('/admin/pengurus/tambah')
    token = get_csrf(page)
    res = client.post('/admin/pengurus/tambah',
                      data={'csrf_token': token, 'nama': 'Zendra', 'jabatan': 'Ketua',
                            'urutan': '1', 'foto': '', 'deskripsi': ''},
                      follow_redirects=False)
    assert res.status_code == 302

    res = client.get('/admin/pengurus')
    assert res.status_code == 200
    assert b'Zendra' in res.data

    with app.app_context():
        pg = Pengurus.query.filter_by(nama='Zendra').first()
        assert pg is not None
        assert pg.jabatan == 'Ketua'
        assert pg.urutan == 1


def test_pengurus_tambah_invalid_empty(client, app):
    _login_admin(client)
    page = client.get('/admin/pengurus/tambah')
    token = get_csrf(page)
    before = Pengurus.query.count()
    res = client.post('/admin/pengurus/tambah',
                      data={'csrf_token': token, 'nama': '', 'jabatan': '',
                            'urutan': ''},
                      follow_redirects=False)
    assert res.status_code == 200  # re-render form dengan error
    with app.app_context():
        assert Pengurus.query.count() == before


def test_pengurus_edit(client, app):
    _login_admin(client)
    with app.app_context():
        pg = Pengurus(nama='Old', jabatan='Wakil', urutan=2)
        db.session.add(pg)
        db.session.commit()
        pid = pg.id

    page = client.get('/admin/pengurus/%s/edit' % pid)
    assert page.status_code == 200
    assert b'Old' in page.data
    token = get_csrf(page)

    res = client.post('/admin/pengurus/%s/edit' % pid,
                      data={'csrf_token': token, 'nama': 'New Name',
                            'jabatan': 'Ketua', 'urutan': '3'},
                      follow_redirects=False)
    assert res.status_code == 302
    with app.app_context():
        pg = db.session.get(Pengurus, pid)
        assert pg.nama == 'New Name'
        assert pg.jabatan == 'Ketua'
        assert pg.urutan == 3


def test_pengurus_hapus(client, app):
    _login_admin(client)
    with app.app_context():
        pg = Pengurus(nama='Temp', jabatan='Tester', urutan=5)
        db.session.add(pg)
        db.session.commit()
        pid = pg.id

    page = client.get('/admin/pengurus')
    assert page.status_code == 200
    token = get_csrf(page)
    res = client.post('/admin/pengurus/%s/hapus' % pid,
                      data={'csrf_token': token}, follow_redirects=False)
    assert res.status_code == 302
    with app.app_context():
        assert db.session.get(Pengurus, pid) is None