import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

import sqlite3, requests, os, subprocess

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

    
    conn.commit()
    

pinjaman_buku()

def kunjungan():
    cursor.execute('''create table if not exists kunjungan (
                   id integer primary key autoincrement,
                   tanggal text,
                   nama text,
                   kelas text,
                   tujuan text)''')
    
    conn.commit()

kunjungan()

def main():
    app = QApplication(sys.argv)  # Create an application object

    # Create a QMainWindow instance
    window = QMainWindow()
    window.setWindowTitle('MultiPerpus')
    window.setWindowIcon(QIcon('logo.png'))
    # window.setGeometry(100, 100, 600, 400)  # Set the position and size of the window (x, y, width, height)
    window.setFixedSize(1000,700)
    
    sidebar = QLabel('', window)
    sidebar.setFixedSize(200,700)
    sidebar_layout = QVBoxLayout(sidebar)

    def sidebarButtons(name):
        btn = QPushButton(name)
        btn.setFixedHeight(90)
        sidebar_layout.addWidget(btn)
        return btn
    
    # btn = sidebarButtons(name='DASHBOARD')
    logo_lbl = QLabel('MultiPerpus');sidebar_layout.addWidget(logo_lbl);logo_lbl.setAlignment(Qt.AlignCenter)
    logo_lbl.setProperty('class','white')
    def LogoLbl():
        pixmap = QPixmap('logo.png')
        logo_lbl.setPixmap(pixmap.scaled(logo_lbl.size() - QSize(400,400), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    LogoLbl()
    btn = sidebarButtons(name='KUNJUNGAN').clicked.connect(lambda:(kunjungan.setVisible(True)))
    btn = sidebarButtons(name='PINJAMAN BUKU').clicked.connect(lambda:(pinjaman_buku.setVisible(True)))
    btn = sidebarButtons(name='PINJAMAN BARANG').clicked.connect(lambda:(pinjaman_barang.setVisible(True)))
    btn = sidebarButtons(name='KOLEKSI BUKU').clicked.connect(lambda:(koleksi_buku.setVisible(True)))
    btn = sidebarButtons(name='KOLEKSI BARANG').clicked.connect(lambda:(koleksi_barang.setVisible(True)))
    btn = sidebarButtons(name='TENTANG APLIKASI \n DAN EXPORT DATA').clicked.connect(lambda:(tentang_aplikasi.setVisible(True)))


#
#
# Dashboard

    dashboard = QLabel(window)
    dashboard.setGeometry(200, 0, 800, 700)

    def Dashboard():
        dashboard_layout = QVBoxLayout(dashboard)

        refresh = QPushButton('Refresh / Reload'); refresh.setFixedHeight(30) ;dashboard_layout.addWidget(refresh)
        

        img = QLabel(); dashboard_layout.addWidget(img)
        img2 = QLabel(); dashboard_layout.addWidget(img2)
        
        def get_data():
            cursor.execute('''SELECT tanggal, kelas FROM kunjungan''')
            data = cursor.fetchall()

            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(data, columns=['tanggal', 'kelas'])

            # Convert tanggal to datetime
            df['tanggal'] = pd.to_datetime(df['tanggal'], format='%a %b %d %Y')

            # Extract year and month
            df['year'] = df['tanggal'].dt.year
            df['month'] = df['tanggal'].dt.month

            # Get the current year and month
            current_year = datetime.now().year
            current_month = datetime.now().month

            # Filter data for the current year and previous year
            current_year_data = df[df['year'] == current_year]
            previous_year_data = df[df['year'] == (current_year - 1)]

            # Group by kelas for the pie chart (filtered by current year)
            yearly_data = current_year_data.groupby('kelas').size()

            # Group by month and kelas for the line chart
            monthly_data = pd.concat([previous_year_data, current_year_data])
            monthly_data = monthly_data.groupby(['year', 'month', 'kelas']).size().unstack(fill_value=0)

            # Adjust number of months to display (e.g., last 12 months)
            num_months_to_display = 12

            # Calculate the starting month based on the number of months to display
            start_month = max(1, current_month - (num_months_to_display - 1))

            # Ensure the line chart includes data for the specified number of months
            monthly_data = monthly_data.loc[(current_year - 1, start_month):(current_year, current_month)]

            # Generate yearly pie chart for the current year
            if not yearly_data.empty:
                yearly_data.plot(kind='pie', autopct='%1.1f%%', startangle=90, figsize=(16, 8), fontsize=20)
                plt.title(f'Data Tahunan Pengunjung Perpustakaan Pada Tahun {current_year}', fontsize=30)
                plt.ylabel('')
                plt.tight_layout()  # Adjust layout for better spacing

                # Save pie chart as JPG
                plt.savefig('chart/tahunan.jpg')
                plt.close()

            # Generate monthly line chart for the specified number of months
            if not monthly_data.empty:
                monthly_data_sorted = monthly_data.groupby(level=[0, 1]).sum().sort_index(level=[0, 1])

                # Create custom x-axis labels with month and year
                x_labels = [f'{datetime(2000, month, 1).strftime("%b")} {year}' for year, month in monthly_data_sorted.index]

                ax = monthly_data_sorted.plot(kind='line', marker='o', figsize=(12, 6), fontsize=15)

                # Set x-axis labels
                ax.set_xticks(range(len(x_labels)))
                ax.set_xticklabels(x_labels, rotation=45, ha='right')

                plt.title(f'Data Bulanan Pengunjung Perpustakaan hingga {datetime(current_year, current_month, 1).strftime("%b %Y")}', fontsize=20)
                plt.xlabel('Bulan', fontsize=20)
                plt.ylabel('Jumlah', fontsize=20)
                plt.grid(True)
                plt.tight_layout()  # Adjust layout to prevent clipping of tick-labels

                # Save line chart as JPG
                plt.savefig('chart/bulanan.jpg')
                plt.close()


            # Display the yearly pie chart if it exists

            if not yearly_data.empty:
                
                img.setAlignment(Qt.AlignCenter)
                img.setProperty('class', 'white')
                pixmap = QPixmap('chart/tahunan.jpg')
                scaled_pixmap = pixmap.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img.setPixmap(scaled_pixmap)
            else:
                img.clear()

            # Display the monthly line chart if it exists

            if not monthly_data.empty:
                
                img2.setAlignment(Qt.AlignCenter)
                img2.setProperty('class', 'white')
                pixmap = QPixmap('chart/bulanan.jpg')
                scaled_pixmap = pixmap.scaled(img2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                img2.setPixmap(scaled_pixmap)
            else:
                img2.clear()

        get_data()
        refresh.clicked.connect(get_data)


    Dashboard()





#
#
# kunjungan (tanggal, nama, kelas, tujuan berkunjung)
    kunjungan = QLabel(window)
    kunjungan.setVisible(False)
    kunjungan.setGeometry(0,0,1000,700)

    def Kunjungan():
        

        b_btn = QPushButton('Kembali', kunjungan)
        b_btn.setGeometry(0,0,100,25)
        b_btn.clicked.connect(lambda:(kunjungan.setVisible(False)))
        
        title = QLabel('Kunjungan Perpustakaan', kunjungan)
        title.setGeometry(100,0,200,25)

        cal = QCalendarWidget(kunjungan); cal.setGeometry(0,425,400,275)
        def cal_clicked(date):
            cal_lbl.setText(date.toString())
        cal.clicked.connect(cal_clicked)
        
        form = QLabel(kunjungan)
        form.setGeometry(400,425,600,275)
        form_layout = QVBoxLayout(form)

        def form_text(placeholder):
            text = QLineEdit()
            text.setPlaceholderText(placeholder)
            form_layout.addWidget(text)
            return text
        
        def form_buttons(name):
            btn = QPushButton(name)
            btn.setFixedHeight(30)
            form_layout.addWidget(btn)
            return btn
        
        # ids = None
        
        cal_lbl = QLabel();cal_lbl.setFixedHeight(30);form_layout.addWidget(cal_lbl)
        text2 = form_text(placeholder='Nama')
        text3 = form_text(placeholder='Kelas')
        text4 = form_text(placeholder='Tujuan Berkunjung')
        
        insert = form_buttons(name='Insert')
        insert.clicked.connect(lambda:(
            cursor.execute('insert into kunjungan(tanggal, nama, kelas, tujuan) values (?,?,?,?)',
            (cal_lbl.text(),text2.text(),text3.text(),text4.text())),
            conn.commit(),
            get_data()
        ))
        

        edit = form_buttons(name='Edit')
        def edit_koleksi_barang():
            global ids
            cursor.execute('''update kunjungan set tanggal=?, nama=?, kelas=?, tujuan=? where id =?''',(cal_lbl.text(),text2.text(),text3.text(),text4.text(),ids))
            conn.commit()
            get_data()
        edit.clicked.connect(edit_koleksi_barang)

        delete = form_buttons(name='Delete')
        def delete_koleksi_barang():
            global ids
            cursor.execute('''delete from kunjungan where id = ?''', (ids,))
            conn.commit()
            get_data()
        delete.clicked.connect(delete_koleksi_barang)

        table = QTableWidget(kunjungan)
        table.setGeometry(0,25,1000,400)
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(['ID','Tanggal','Nama','Kelas','Tujuan Berkunjung'])
        table.setColumnWidth(0,10)
        column = [1,2,3,4]
        for col in column:
            table.horizontalHeader().setSectionResizeMode(col,QHeaderView.Stretch)

        def get_data():
            cursor.execute('select * from kunjungan order by id desc')
            data = cursor.fetchall()
            table.setRowCount(len(data))

            for row_index, row_data in enumerate(data):
                for column_index, item in enumerate(row_data):
                    table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

            table.setRowCount(len(data))
        get_data()

        def row_click(index):
            global ids

            row = index.row()
            ids = table.item(row, 0).text()
            cal_lbl.setText(table.item(row, 1).text())
            text2.setText(table.item(row, 2).text())
            text3.setText(table.item(row, 3).text())
            text4.setText(table.item(row, 4).text())
        table.clicked.connect(row_click)

        search_text = QLineEdit(kunjungan); search_text.setPlaceholderText('Cari'); search_text.setGeometry(300,0,400,25)
        def search():
            search_query = search_text.text()
            
            if search_query == '':
                get_data()
            else:
                cursor.execute(
                    'SELECT * FROM kunjungan where tanggal like ? or nama like ? or kelas like ? or tujuan like ?',
                    (f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%')
                )
                data = cursor.fetchall()
                table.setRowCount(len(data))

                for row_index, row_data in enumerate(data):
                    for column_index, item in enumerate(row_data):
                        table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

        search_text.textChanged.connect(search)
            
    

    Kunjungan()






#
#
# Pinjaman Buku

    pinjaman_buku = QLabel(window)
    pinjaman_buku.setVisible(False)
    pinjaman_buku.setGeometry(0,0,1000,700)

    def pinjamanBuku():

        b_btn = QPushButton('Kembali', pinjaman_buku)
        b_btn.setGeometry(0,0,100,25)
        b_btn.clicked.connect(lambda:(pinjaman_buku.setVisible(False)))
        
        title = QLabel('Pinjaman Buku', pinjaman_buku)
        title.setGeometry(100,0,200,25)
        
        table = QTableWidget(pinjaman_buku)
        table.setGeometry(0,25,1000,300)
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(['ID','Tgl_Pinjam','Tgl_Kembali','Peminjam','Kelas','Jumlah','Buku','Link Gambar'])
        table.setColumnWidth(0,10)
        column = [1,2,3,4,5,6,7]
        for col in column:
            table.horizontalHeader().setSectionResizeMode(col,QHeaderView.Stretch)
    
        img = QLabel(pinjaman_buku)
        img.setGeometry(0,325,400,375)

        form = QLabel(pinjaman_buku)
        form.setGeometry(400,325,600,375)
        form_layout = QVBoxLayout(form)

        def form_text(placeholder):
            txt = QLineEdit();txt.setPlaceholderText(placeholder);form_layout.addWidget(txt)
            # txt.setFixedHeight(30)
            return txt
        
        tgl_lbl = QLabel();form_layout.addWidget(tgl_lbl);form_layout.addWidget(tgl_lbl)
        tgl_layout = QGridLayout(tgl_lbl)


        cal_btn1 = QPushButton('Tanggal Pinjam');cal_btn1.setFixedHeight(50);tgl_layout.addWidget(cal_btn1,0,0)
        cal_btn1.clicked.connect(lambda:(cal1.setVisible(True)))
        cal_lbl1 = QLabel();tgl_layout.addWidget(cal_lbl1,1,0)

        cal_btn2 = QPushButton('Tanggal Kembali');cal_btn2.setFixedHeight(50);tgl_layout.addWidget(cal_btn2,0,1)
        cal_btn2.clicked.connect(lambda:(cal2.setVisible(True)))
        cal_lbl2 = QLabel();tgl_layout.addWidget(cal_lbl2,1,1)

        


        text3 = form_text(placeholder='Peminjam')
        text4 = form_text(placeholder='Kelas')
        text5 = form_text(placeholder='Jumlah'); text5.setValidator(QIntValidator())
        text6 = form_text(placeholder='Buku'); text6.setDisabled(True)
        text6.setProperty('class','black')
        text7 = form_text(placeholder='Link Gambar'); text7.setDisabled(True)
        text7.setProperty('class','black')
        def load_image():
            url = text7.text()
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_data):
                        scaled_pixmap = pixmap.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.setPixmap(scaled_pixmap)
                    else:
                        img.clear()  # Clear the label if the image couldn't be loaded
                else:
                    img.clear()  # Clear the label if the request failed
            except Exception as e:
                print(f"An error occurred: {e}")
                img.clear()  # Clear the label if any exception occurs
        text7.textChanged.connect(load_image)

        cal1 = QCalendarWidget(form);cal1.setGeometry(10,10,310,200); cal1.setVisible(False)
        def cal1_clicked(date):
            # print('date cal1 is '+date.toString())
            cal_lbl1.setText(date.toString())
            cal1.setVisible(False)
        cal1.clicked.connect(cal1_clicked)

        cal2 = QCalendarWidget(form);cal2.setGeometry(280,10,310,200); cal2.setVisible(False)
        def cal2_clicked(date):
            # print('date cal1 is '+date.toString())
            cal_lbl2.setText(date.toString())
            cal2.setVisible(False)
        cal2.clicked.connect(cal2_clicked)
        


        pilih_btn = QPushButton('Pilih Buku');pilih_btn.setFixedHeight(50);form_layout.addWidget(pilih_btn)
        pilih_btn.clicked.connect(lambda:(get_data2(),form2.setVisible(True)))

        def get_data():
            cursor.execute('SELECT * FROM pinjaman_buku order by id desc')
            data = cursor.fetchall()
            table.setRowCount(len(data))

            for row_index, row_data in enumerate(data):
                for column_index, item in enumerate(row_data):
                    table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

            table.setRowCount(len(data))
        get_data()
        def row_click(index):
            global ids

            row = index.row()
            ids = table.item(row, 0).text()
            cal_lbl1.setText(table.item(row, 1).text())
            cal_lbl2.setText(table.item(row, 2).text())
            text3.setText(table.item(row, 3).text())
            text4.setText(table.item(row, 4).text())
            text5.setText(table.item(row, 5).text())
            text6.setText(table.item(row, 6).text())
            text7.setText(table.item(row, 7).text())
            

            load_image()
        table.clicked.connect(row_click)



        act_lbl = QLabel();act_lbl.setFixedHeight(50);form_layout.addWidget(act_lbl)
        act_lbl_layout = QHBoxLayout(act_lbl)
        
        insert = QPushButton('Insert');insert.setFixedHeight(30);act_lbl_layout.addWidget(insert)
        insert.clicked.connect(lambda:(cursor.execute(''' insert into pinjaman_buku (tanggal_pinjam, tanggal_kembali, peminjam, kelas, jumlah, buku, link_gambar)
                   values (?,?,?,?,?,?,?)''', (cal_lbl1.text(),cal_lbl2.text(),text3.text(),text4.text(),text5.text(),text6.text(),text7.text())),
                   conn.commit(),
                   get_data()))
        
        edit = QPushButton('Edit');edit.setFixedHeight(30);act_lbl_layout.addWidget(edit)
        def edit_clicked():
            global ids

            cursor.execute('''update pinjaman_buku set tanggal_pinjam=?, tanggal_kembali=?, peminjam=?, kelas=?, jumlah=?, buku=?, link_gambar=? where id =?''',
                           (cal_lbl1.text(),cal_lbl2.text(),text3.text(),text4.text(),text5.text(),text6.text(),text7.text(),ids))
            conn.commit()
            get_data()
        edit.clicked.connect(edit_clicked)

        delete = QPushButton('Delete');delete.setFixedHeight(30);act_lbl_layout.addWidget(delete)
        def delete_clicked():
            global ids
            cursor.execute('delete from pinjaman_buku where id=?',ids)
            conn.commit()
            get_data()
        delete.clicked.connect(delete_clicked)

        form2 = QLabel(form); form2.setFixedSize(form.size());form2.setVisible(False)
        table2 = QTableWidget(form2);table2.setGeometry(0,0,600,300);table2.setColumnCount(2);table2.setHorizontalHeaderLabels(['Buku','Link Gambar'])
        ok_btn = QPushButton('OK', form2);ok_btn.setGeometry(0,300,300,50);ok_btn.clicked.connect(lambda:(form2.setVisible(False)))
        cancel_btn = QPushButton('Hapus', form2);cancel_btn.setGeometry(300,300,300,50)
        cancel_btn.clicked.connect(lambda:(text6.setText(''),text7.setText(''),form2.setVisible(False), img.clear()))
        
        def get_data2():
            cursor.execute('SELECT buku, link_gambar FROM koleksi_buku')
            data = cursor.fetchall()
            table2.setRowCount(len(data))

            for row_index, row_data in enumerate(data):
                for column_index, item in enumerate(row_data):
                    table2.setItem(row_index, column_index, QTableWidgetItem(str(item)))

            table2.setRowCount(len(data))

        get_data2()
        def row_click2(index):
            row = index.row()
            text6.setText(table2.item(row, 0).text())
            text7.setText(table2.item(row, 1).text())
            

            url = table2.item(row, 1).text()
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_data):
                        scaled_pixmap = pixmap.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.setPixmap(scaled_pixmap)
                    else:
                        img.clear()  # Clear the label if the image couldn't be loaded
                else:
                    img.clear()  # Clear the label if the request failed
            except Exception as e:
                print(f"An error occurred: {e}")
                img.clear()  # Clear the label if any exception occurs
        table2.clicked.connect(row_click2)

        search_text = QLineEdit(pinjaman_buku); search_text.setPlaceholderText('Cari'); search_text.setGeometry(300,0,400,25)
        def search():
            search_query = search_text.text()
            
            if search_query == '':
                get_data()
            else:
                cursor.execute(
                    'SELECT * FROM pinjaman_buku where tanggal_pinjam like ? or tanggal_kembali like ? or peminjam like ? or kelas like ? or jumlah like ? or buku like ? or link_gambar like ?',
                    (f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',)
                )
                data = cursor.fetchall()
                table.setRowCount(len(data))

                for row_index, row_data in enumerate(data):
                    for column_index, item in enumerate(row_data):
                        table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

        search_text.textChanged.connect(search)
        
        
        
        
    pinjamanBuku()







#
#
# Pinjaman Barang 

    pinjaman_barang = QLabel(window)
    pinjaman_barang.setVisible(False)
    pinjaman_barang.setGeometry(0,0,1000,700)

    def pinjamanBarang():

        b_btn = QPushButton('Kembali', pinjaman_barang)
        b_btn.setGeometry(0,0,100,25)
        b_btn.clicked.connect(lambda:(pinjaman_barang.setVisible(False)))
        
        title = QLabel('Pinjaman Barang', pinjaman_barang)
        title.setGeometry(100,0,200,25)
        
        table = QTableWidget(pinjaman_barang)
        table.setGeometry(0,25,1000,300)
        table.setColumnCount(8)
        table.setHorizontalHeaderLabels(['ID','Tgl_Pinjam','Tgl_Kembali','Peminjam','Kelas','Jumlah','Barang','Link Gambar'])
        table.setColumnWidth(0,10)
        column = [1,2,3,4,5,6,7]
        for col in column:
            table.horizontalHeader().setSectionResizeMode(col,QHeaderView.Stretch)
    
        img = QLabel(pinjaman_barang)
        img.setGeometry(0,325,400,375)

        form = QLabel(pinjaman_barang)
        form.setGeometry(400,325,600,375)
        form_layout = QVBoxLayout(form)

        def form_text(placeholder):
            txt = QLineEdit();txt.setPlaceholderText(placeholder);form_layout.addWidget(txt)
            # txt.setFixedHeight(30)
            return txt
        
        tgl_lbl = QLabel();form_layout.addWidget(tgl_lbl);form_layout.addWidget(tgl_lbl)
        tgl_layout = QGridLayout(tgl_lbl)


        cal_btn1 = QPushButton('Tanggal Pinjam');cal_btn1.setFixedHeight(50);tgl_layout.addWidget(cal_btn1,0,0)
        cal_btn1.clicked.connect(lambda:(cal1.setVisible(True)))
        cal_lbl1 = QLabel();tgl_layout.addWidget(cal_lbl1,1,0)

        cal_btn2 = QPushButton('Tanggal Kembali');cal_btn2.setFixedHeight(50);tgl_layout.addWidget(cal_btn2,0,1)
        cal_btn2.clicked.connect(lambda:(cal2.setVisible(True)))
        cal_lbl2 = QLabel();tgl_layout.addWidget(cal_lbl2,1,1)

        


        text3 = form_text(placeholder='Peminjam')
        text4 = form_text(placeholder='Kelas')
        text5 = form_text(placeholder='Jumlah'); text5.setValidator(QIntValidator())
        text6 = form_text(placeholder='Barang'); text6.setDisabled(True)
        text6.setProperty('class','black')
        text7 = form_text(placeholder='Link Gambar'); text7.setDisabled(True)
        text7.setProperty('class','black')
        def load_image():
            url = text7.text()
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_data):
                        scaled_pixmap = pixmap.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.setPixmap(scaled_pixmap)
                    else:
                        img.clear()  # Clear the label if the image couldn't be loaded
                else:
                    img.clear()  # Clear the label if the request failed
            except Exception as e:
                print(f"An error occurred: {e}")
                img.clear()  # Clear the label if any exception occurs
        text7.textChanged.connect(load_image)
        

        cal1 = QCalendarWidget(form);cal1.setGeometry(10,10,310,200); cal1.setVisible(False)
        def cal1_clicked(date):
            # print('date cal1 is '+date.toString())
            cal_lbl1.setText(date.toString())
            cal1.setVisible(False)
        cal1.clicked.connect(cal1_clicked)

        cal2 = QCalendarWidget(form);cal2.setGeometry(280,10,310,200); cal2.setVisible(False)
        def cal2_clicked(date):
            # print('date cal1 is '+date.toString())
            cal_lbl2.setText(date.toString())
            cal2.setVisible(False)
        cal2.clicked.connect(cal2_clicked)
        


        pilih_btn = QPushButton('Pilih Barang');pilih_btn.setFixedHeight(50);form_layout.addWidget(pilih_btn)
        pilih_btn.clicked.connect(lambda:(get_data2(),form2.setVisible(True)))

        def get_data():
            cursor.execute('SELECT * FROM pinjaman_barang order by id desc')
            data = cursor.fetchall()
            table.setRowCount(len(data))

            for row_index, row_data in enumerate(data):
                for column_index, item in enumerate(row_data):
                    table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

            table.setRowCount(len(data))
        get_data()
        def row_click(index):
            global ids

            row = index.row()
            ids = table.item(row, 0).text()
            cal_lbl1.setText(table.item(row, 1).text())
            cal_lbl2.setText(table.item(row, 2).text())
            text3.setText(table.item(row, 3).text())
            text4.setText(table.item(row, 4).text())
            text5.setText(table.item(row, 5).text())
            text6.setText(table.item(row, 6).text())
            text7.setText(table.item(row, 7).text())
            

            load_image()
        table.clicked.connect(row_click)



        act_lbl = QLabel();act_lbl.setFixedHeight(50);form_layout.addWidget(act_lbl)
        act_lbl_layout = QHBoxLayout(act_lbl)
        
        insert = QPushButton('Insert');insert.setFixedHeight(30);act_lbl_layout.addWidget(insert)
        insert.clicked.connect(lambda:(cursor.execute(''' insert into pinjaman_barang (tanggal_pinjam, tanggal_kembali, peminjam, kelas, jumlah, barang, link_gambar)
                   values (?,?,?,?,?,?,?)''', (cal_lbl1.text(),cal_lbl2.text(),text3.text(),text4.text(),text5.text(),text6.text(),text7.text())),
                   conn.commit(),
                   get_data()))
        
        edit = QPushButton('Edit');edit.setFixedHeight(30);act_lbl_layout.addWidget(edit)
        def edit_clicked():
            global ids

            cursor.execute('''update pinjaman_barang set tanggal_pinjam=?, tanggal_kembali=?, peminjam=?, kelas=?, jumlah=?, barang=?, link_gambar=? where id =?''',
                           (cal_lbl1.text(),cal_lbl2.text(),text3.text(),text4.text(),text5.text(),text6.text(),text7.text(),ids))
            conn.commit()
            get_data()
        edit.clicked.connect(edit_clicked)

        delete = QPushButton('Delete');delete.setFixedHeight(30);act_lbl_layout.addWidget(delete)
        def delete_clicked():
            global ids
            cursor.execute('delete from pinjaman_barang where id=?',ids)
            conn.commit()
            get_data()
        delete.clicked.connect(delete_clicked)

        form2 = QLabel(form); form2.setFixedSize(form.size());form2.setVisible(False)
        table2 = QTableWidget(form2);table2.setGeometry(0,0,600,300);table2.setColumnCount(2);table2.setHorizontalHeaderLabels(['Barang','Link Gambar'])
        ok_btn = QPushButton('OK', form2);ok_btn.setGeometry(0,300,300,50);ok_btn.clicked.connect(lambda:(form2.setVisible(False)))
        cancel_btn = QPushButton('Hapus', form2);cancel_btn.setGeometry(300,300,300,50)
        cancel_btn.clicked.connect(lambda:(text6.setText(''),text7.setText(''),form2.setVisible(False), img.clear()))
        
        def get_data2():
            cursor.execute('SELECT barang, link_gambar FROM koleksi_barang')
            data = cursor.fetchall()
            table2.setRowCount(len(data))

            for row_index, row_data in enumerate(data):
                for column_index, item in enumerate(row_data):
                    table2.setItem(row_index, column_index, QTableWidgetItem(str(item)))

            table2.setRowCount(len(data))

        get_data2()
        def row_click2(index):
            row = index.row()
            text6.setText(table2.item(row, 0).text())
            text7.setText(table2.item(row, 1).text())
            

            url = table2.item(row, 1).text()
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_data):
                        scaled_pixmap = pixmap.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.setPixmap(scaled_pixmap)
                    else:
                        img.clear()  # Clear the label if the image couldn't be loaded
                else:
                    img.clear()  # Clear the label if the request failed
            except Exception as e:
                print(f"An error occurred: {e}")
                img.clear()  # Clear the label if any exception occurs
        table2.clicked.connect(row_click2)

        search_text = QLineEdit(pinjaman_barang); search_text.setPlaceholderText('Cari'); search_text.setGeometry(300,0,400,25)
        def search():
            search_query = search_text.text()
            
            if search_query == '':
                get_data()
            else:
                cursor.execute(
                    'SELECT * FROM pinjaman_barang where tanggal_pinjam like ? or tanggal_kembali like ? or peminjam like ? or kelas like ? or jumlah like ? or barang like ? or link_gambar like ?',
                    (f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',)
                )
                data = cursor.fetchall()
                table.setRowCount(len(data))

                for row_index, row_data in enumerate(data):
                    for column_index, item in enumerate(row_data):
                        table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

        search_text.textChanged.connect(search)
        
        
        
    pinjamanBarang()










#
#
# Koleksi Buku 
    koleksi_buku = QLabel(window)
    koleksi_buku.setVisible(False)
    koleksi_buku.setGeometry(0,0,1000,700)

    def koleksiBuku():

        b_btn = QPushButton('Kembali', koleksi_buku)
        b_btn.setGeometry(0,0,100,25)
        b_btn.clicked.connect(lambda:(koleksi_buku.setVisible(False)))
        
        title = QLabel('Koleksi Buku', koleksi_buku)
        title.setGeometry(100,0,200,25)

        img = QLabel(koleksi_buku)
        img.setGeometry(0,325,400,375)

        form = QLabel(koleksi_buku)
        form.setGeometry(400,325,600,375)
        form_layout = QVBoxLayout(form)

        def form_text(placeholder):
            text = QLineEdit()
            text.setPlaceholderText(placeholder)
            form_layout.addWidget(text)
            return text
        
        def form_buttons(name):
            btn = QPushButton(name)
            btn.setFixedHeight(30)
            form_layout.addWidget(btn)
            return btn
        
        text1 = form_text(placeholder='Buku')
        text2 = form_text(placeholder='Tahun')
        text3 = form_text(placeholder='Penerbit')
        text4 = form_text(placeholder='Jumlah'); text4.setValidator(QIntValidator())
        text5 = form_text(placeholder='Link Gambar')
        def load_image():
            url = text5.text()
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_data):
                        scaled_pixmap = pixmap.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.setPixmap(scaled_pixmap)
                    else:
                        img.clear()  # Clear the label if the image couldn't be loaded
                else:
                    img.clear()  # Clear the label if the request failed
            except Exception as e:
                print(f"An error occurred: {e}")
                img.clear()  # Clear the label if any exception occurs
        text5.textChanged.connect(load_image)

        insert = form_buttons(name='Insert')
        insert.clicked.connect(lambda:(
            cursor.execute('''insert into koleksi_buku (buku, tahun, penerbit, jumlah, link_gambar) values (?,?,?,?,?)''',(text1.text(),text2.text(),text3.text(),text4.text(),text5.text()))
            , conn.commit()
            , get_data()
        ))

        edit = form_buttons(name='Edit')
        def edit_koleksi_barang():
            global ids
            cursor.execute('''update koleksi_buku set buku=?, tahun=?, penerbit=?, jumlah=?, link_gambar=? where id =?''',(text1.text(),text2.text(),text3.text(),text4.text(),text5.text(),ids))
            conn.commit()
            get_data()
        edit.clicked.connect(edit_koleksi_barang)

        delete = form_buttons(name='Delete')
        def delete_koleksi_barang():
            global ids
            cursor.execute('''delete from koleksi_buku where id = ?''', (ids,))
            conn.commit()
            get_data()
        delete.clicked.connect(delete_koleksi_barang)

        table = QTableWidget(koleksi_buku)
        table.setGeometry(0,25,1000,300)
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(['ID','Buku','Tahun','Penerbit','Jumlah','Link Gambar'])
        table.setColumnWidth(0,10)
        column = [1,2,3,4,5]
        for col in column:
            table.horizontalHeader().setSectionResizeMode(col,QHeaderView.Stretch)

        def get_data():
            cursor.execute('SELECT * FROM koleksi_buku order by id desc')
            data = cursor.fetchall()
            table.setRowCount(len(data))

            for row_index, row_data in enumerate(data):
                for column_index, item in enumerate(row_data):
                    table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

            table.setRowCount(len(data))

        get_data()

        def row_click_koleksi_buku(index):
            global ids

            row = index.row()
            ids = table.item(row, 0).text()
            text1.setText(table.item(row, 1).text())
            text2.setText(table.item(row, 2).text())
            text3.setText(table.item(row, 3).text())
            text4.setText(table.item(row, 4).text())
            text5.setText(table.item(row, 5).text())

            load_image()

        table.clicked.connect(row_click_koleksi_buku)

        search_text = QLineEdit(koleksi_buku); search_text.setPlaceholderText('Cari'); search_text.setGeometry(300,0,400,25)
        def search():
            search_query = search_text.text()
            
            if search_query == '':
                get_data()
            else:
                cursor.execute(
                    'SELECT * FROM koleksi_buku WHERE buku like ? or tahun like ? or penerbit like ? or jumlah like ? or link_gambar like ?',
                    (f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',f'%{search_query}%',)
                )
                data = cursor.fetchall()
                table.setRowCount(len(data))

                for row_index, row_data in enumerate(data):
                    for column_index, item in enumerate(row_data):
                        table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

        search_text.textChanged.connect(search)
    
    koleksiBuku()
    









#
#
# Koleksi Barang 
    koleksi_barang = QLabel(window)
    koleksi_barang.setVisible(False)
    koleksi_barang.setGeometry(0,0,1000,700)

    def koleksiBarang():
        

        b_btn = QPushButton('Kembali', koleksi_barang)
        b_btn.setGeometry(0,0,100,25)
        b_btn.clicked.connect(lambda:(koleksi_barang.setVisible(False)))
        
        title = QLabel('Koleksi Barang', koleksi_barang)
        title.setGeometry(100,0,200,25)

        img = QLabel(koleksi_barang)
        img.setGeometry(0,325,400,375)

        form = QLabel(koleksi_barang)
        form.setGeometry(400,325,600,375)
        form_layout = QVBoxLayout(form)

        def form_text(placeholder):
            text = QLineEdit()
            text.setPlaceholderText(placeholder)
            form_layout.addWidget(text)
            return text
        
        def form_buttons(name):
            btn = QPushButton(name)
            btn.setFixedHeight(30)
            form_layout.addWidget(btn)
            return btn
        
        # ids = None

        text1 = form_text(placeholder='Barang')
        text2 = form_text(placeholder='Merek')
        text3 = form_text(placeholder='Jumlah'); text3.setValidator(QIntValidator())
        text4 = form_text(placeholder='Link Gambar')
        def load_image():
            url = text4.text()
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    image_data = response.content
                    pixmap = QPixmap()
                    if pixmap.loadFromData(image_data):
                        scaled_pixmap = pixmap.scaled(img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        img.setPixmap(scaled_pixmap)
                    else:
                        img.clear()  # Clear the label if the image couldn't be loaded
                else:
                    img.clear()  # Clear the label if the request failed
            except Exception as e:
                print(f"An error occurred: {e}")
                img.clear()  # Clear the label if any exception occurs
        text4.textChanged.connect(load_image)
        
        insert = form_buttons(name='Insert')
        insert.clicked.connect(lambda:(
            cursor.execute('''insert into koleksi_barang (barang, merek, jumlah, link_gambar) values (?,?,?,?)''',(text1.text(),text2.text(),text3.text(),text4.text()))
            , conn.commit()
            , get_data()
            
        ))
        edit = form_buttons(name='Edit')

        def edit_koleksi_barang():
            global ids
            cursor.execute('''update koleksi_barang set barang=?, merek=?, jumlah=?, link_gambar=? where id =?''',(text1.text(),text2.text(),text3.text(),text4.text(),ids))
            conn.commit()
            get_data()
        edit.clicked.connect(edit_koleksi_barang)

        delete = form_buttons(name='Delete')
        def delete_koleksi_barang():
            global ids
            cursor.execute('''delete from koleksi_barang where id = ?''', (ids,))
            conn.commit()
            get_data()
        delete.clicked.connect(delete_koleksi_barang)

        table = QTableWidget(koleksi_barang)
        table.setGeometry(0,25,1000,300)
        table.setColumnCount(5)
        # table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table.setHorizontalHeaderLabels(['ID','Barang','Merek','Jumlah','Link Gambar'])
        table.setColumnWidth(0,10)
        column = [1,2,3,4]
        for col in column:
            table.horizontalHeader().setSectionResizeMode(col,QHeaderView.Stretch)

        def get_data():
            cursor.execute('SELECT * FROM koleksi_barang order by id desc')
            data = cursor.fetchall()
            table.setRowCount(len(data))

            for row_index, row_data in enumerate(data):
                for column_index, item in enumerate(row_data):
                    table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

            table.setRowCount(len(data))

        get_data()

        def row_click_koleksi_barang(index):
            global ids

            row = index.row()
            ids = table.item(row, 0).text()
            text1.setText(table.item(row, 1).text())
            text2.setText(table.item(row, 2).text())
            text3.setText(table.item(row, 3).text())
            text4.setText(table.item(row, 4).text())

            load_image()

        table.clicked.connect(row_click_koleksi_barang)


        search_text = QLineEdit(koleksi_barang); search_text.setPlaceholderText('Cari'); search_text.setGeometry(300,0,400,25)
        def search():
            search_query = search_text.text()
            
            if search_query == '':
                get_data()
            else:
                cursor.execute(
                    'SELECT * FROM koleksi_barang WHERE barang LIKE ? OR merek LIKE ? OR jumlah LIKE ? OR link_gambar LIKE ?',
                    (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
                )
                data = cursor.fetchall()
                table.setRowCount(len(data))

                for row_index, row_data in enumerate(data):
                    for column_index, item in enumerate(row_data):
                        table.setItem(row_index, column_index, QTableWidgetItem(str(item)))

        search_text.textChanged.connect(search)

    koleksiBarang()










# 
#
# tentang aplikasi

    tentang_aplikasi = QLabel(window)
    tentang_aplikasi.setVisible(False)
    tentang_aplikasi.setGeometry(0,0,1000,700)

    def TentangAplikasi():

        b_btn = QPushButton('Kembali', tentang_aplikasi)
        b_btn.setGeometry(0,0,100,25)
        b_btn.clicked.connect(lambda:(tentang_aplikasi.setVisible(False)))
        
        title = QLabel('Tentang Aplikasi Dan Expor Data', tentang_aplikasi)
        title.setGeometry(100,0,250,25)

        lbl = QLabel(tentang_aplikasi); lbl.setGeometry(0,25,1000,675)
        
        layout = QVBoxLayout(lbl)
        with open('tentang_aplikasi.html', 'r') as file:
            content = file.read()
            tentang = QLabel(content); layout.addWidget(tentang)
            tentang.setWordWrap(True)

        export = QPushButton('Export Data Sebagai Excel');export.setFixedHeight(100) ;layout.addWidget(export)
        def export_data():
            conn = sqlite3.connect('data.db')

            # Query the data from each table
            query_koleksi_barang = 'SELECT * FROM koleksi_barang'
            query_koleksi_buku = 'SELECT * FROM koleksi_buku'
            query_pinjaman_barang = 'SELECT * FROM pinjaman_barang'
            query_pinjaman_buku = 'SELECT * FROM pinjaman_buku'
            query_kunjungan = 'SELECT * FROM kunjungan'

            # Read the data into pandas DataFrames
            df_koleksi_barang = pd.read_sql_query(query_koleksi_barang, conn)
            df_koleksi_buku = pd.read_sql_query(query_koleksi_buku, conn)
            df_pinjaman_barang = pd.read_sql_query(query_pinjaman_barang, conn)
            df_pinjaman_buku = pd.read_sql_query(query_pinjaman_buku, conn)
            df_kunjungan = pd.read_sql_query(query_kunjungan, conn)

            # Create a Pandas Excel writer using Openpyxl as the engine
            with pd.ExcelWriter('../saves/output.xlsx', engine='openpyxl') as writer:
                # Write each DataFrame to a different worksheet
                df_koleksi_barang.to_excel(writer, sheet_name='Koleksi Barang', index=False)
                df_koleksi_buku.to_excel(writer, sheet_name='Koleksi Buku', index=False)
                df_pinjaman_barang.to_excel(writer, sheet_name='Pinjaman Barang', index=False)
                df_pinjaman_buku.to_excel(writer, sheet_name='Pinjaman Buku', index=False)
                df_kunjungan.to_excel(writer, sheet_name='Kunjungan', index=False)

            # Close the connection

            file_path = os.path.abspath('../saves/output.xlsx')

            # Open the folder containing the file
            folder_path = os.path.dirname(file_path)

            # Open the folder in Explorer (Windows)
            subprocess.Popen(f'explorer /select,"{file_path}"')
        export.clicked.connect(export_data)



        
    
    TentangAplikasi()
    

    window.show()  # Show the window

    with open('styles.css', 'r') as file:
        content = file.read()
        app.setStyleSheet(content)
    

    def close_db():
        conn.close()

    app.aboutToQuit.connect(close_db)

    sys.exit(app.exec_())  # Run the application's main loop




if __name__ == '__main__':
    main()
