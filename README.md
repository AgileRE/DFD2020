# DFD2GUI

DFD2GUI adalah aplikasi web yang bertujuan memudahkan *user*(*developer*) dalam membangun antarmuka berdasarkan DFD(*Data Flow Diagram*) yang dibuat sebelumnya oleh *user*. *User* dapat melakukan itu dengan meng-*upload file* metadata DFD dari *software* SAP PowerDesigner versi 16. Pada fitur yang akan dibuat ke depan, aplikasi *web* ini akan dapat memberi user pilihan *template* antarmuka seperti tampilan *login*, *register*, *table*, *form*, dan lain-lain. Setelah itu, *user* juga dapat memberi informasi tambahan terkait data apa saja yang terlibat dari suatu proses yang ada di metadata DFD.

## Getting Started

Berikut adalah intruksi yang perlu dilakukan agar dapat berjalan di komputer anda untuk keperluan pengembangan, *testing*, *deployment*, serta apa saja yang perlu di-*install*.

### Prerequisites

Salin baris kode di bawah ini satu persatu ke *terminal* atau ke *command prompt* anda untuk dapat menggunakan *Tools*, *Library*, dan *framework* yang digunakan di projek ini.

```
$ pip install Flask

$ pip install Flask-WTF

$ pip install Flask-SQLAlchemy

$ pip install Flask-Bcrypt

$ pip install Flask-Login

$ pip install beautifulsoup4
```

### Installing

Berikut adalah tahapan untuk dapat menggunakan projek ini.

Pindahkan lokasi direktori anda ke projek ini.

```
$ cd DFD2GUI
```

Untuk menjalankan projek ini di *server* lokal anda. Salin kode di bawah ini ke *terminal* anda.

```
$ python run.py
```

Setelah itu, akan muncul balasan seperti di bawah ini di *terminal* anda.

```
 * Serving Flask app "DFD2GUI" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 256-720-034
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
Lalu, salin alamat IP yang ada di atas ke *internet browser* anda.

## Built With

* [Flask](flask.palletsprojects.com/) - Web framework
* [Jinja](https://palletsprojects.com/p/jinja/) - Template engine
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - XML document parser


## Authors

* 081711633005 - **Christiana natalia Corputty**
* 081711633009 - **Firda Atsalis Maulidya Hasanah**
* 081711633011 - **Alam Al Mabruk**
* 081711633014 - **Fadhil Yusni Ramadhan**
* 081711633018 - **Ersalina Trisnawati**
* 081711633020 - **Muhammad Dary Fauzan**
* 081711633022 - **Mardianta Putra Anggara**
* 081711633030 - **Sinta Sintya**
* 081711633039 - **I Ketut Gerry Putra Hartawan**
* 081711633044 - **Yossy Adirta Soerya Legowo**
* 081711633045 - **Adenegara Rizky Gusty P**
* 081711633051 - **Sherina Avianita**
* 081711633055 - **Salsyabila Putri Pratama**
