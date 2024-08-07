import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

def koleksi_barang():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS koleksi_barang (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barang TEXT,
                merek TEXT,
                jumlah INTEGER,
                link_gambar TEXT
                );''')
    
    # cursor.execute('''
    #                INSERT INTO koleksi_barang (barang, merek, jumlah, link_gambar) 
    #                VALUES (?, ?, ?, ?)''',
    #                ('asd', 'asd', 111, 'asd'))
    conn.commit()

koleksi_barang()


def koleksi_buku():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS koleksi_buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buku TEXT,
                tahun TEXT,
                penerbit TEXT,
                jumlah INTEGER,
                link_gambar TEXT
                );''')
    
    # cursor.execute('''
    #                INSERT INTO koleksi_buku (buku, tahun, penerbit, jumlah, link_gambar) 
    #                VALUES (?, ?, ?, ?, ?)''',
    #                ('asd', 'asd', 'asd', 111, 'asd'))
    conn.commit()

koleksi_buku()


def pinjaman_barang():
    cursor.execute('''
    create table if not exists pinjaman_barang (
                   id integer primary key autoincrement,
                   tanggal_pinjam text,
                   tanggal_kembali text,
                   peminjam text,
                   kelas text,
                   jumlah integer,
                   barang text,
                   link_gambar text)''')

    # cursor.execute(''' insert into pinjaman_barang (tanggal_pinjam, tanggal_kembali, peminjam, kelas, jumlah, barang, link_gambar)
    #                values (?,?,?,?,?,?,?)''', ('asd','asd','asd','asd',111,'asd','asd'))
    conn.commit()
    
# Commit the transaction and close the connection
pinjaman_barang()




def pinjaman_buku():
    cursor.execute('''
    create table if not exists pinjaman_buku (
                   id integer primary key autoincrement,
                   tanggal_pinjam text,
                   tanggal_kembali text,
                   peminjam text,
                   kelas text,
                   jumlah integer,
                   buku text,
                   link_gambar text)''')

    # cursor.execute(''' insert into pinjaman_buku (tanggal_pinjam, tanggal_kembali, peminjam, kelas, jumlah, buku, link_gambar)
    #                values (?,?,?,?,?,?,?)''', ('asd','asd','asd','asd',111,'asd','asd'))
    conn.commit()
    
# Commit the transaction and close the connection
pinjaman_buku()

def kunjungan():
    cursor.execute('''create table if not exists kunjungan (
                   id integer primary key autoincrement,
                   tanggal text,
                   nama text,
                   kelas text,
                   tujuan text)''')
    
    # cursor.execute('''insert into kunjungan(tanggal, nama, kelas, tujuan) values (?,?,?,?)''',('asd','asd','asd','asd'))
    # conn.commit()

kunjungan()
conn.close()
