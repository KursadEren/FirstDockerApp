from flask import Flask, request
import psycopg2
import os
import time

app = Flask(__name__)

def db_baglantisi():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def db_hazir_mi():
    # PostgreSQL hazır olana kadar bekle, max 30 saniye
    for i in range(30):
        try:
            conn = db_baglantisi()
            conn.close()
            print("Veritabani hazir!")
            return True
        except:
            print(f"Veritabani bekleniyor... {i+1}/30")
            time.sleep(1)
    return False

def tablo_olustur():
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notlar (
            id SERIAL PRIMARY KEY,
            baslik TEXT NOT NULL,
            icerik TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def ana_sayfa():
    return """
        <h1>Not Defteri v2 v2</h1>
        <form method="POST" action="/not-ekle">
            <input name="baslik" placeholder="Baslik" required><br><br>
            <textarea name="icerik" placeholder="Icerik" required></textarea><br><br>
            <button type="submit">Kaydet</button>
        </form>
        <br><a href="/notlar">Tum notlari goster</a>
    """

@app.route("/not-ekle", methods=["POST"])
def not_ekle():
    baslik = request.form["baslik"]
    icerik = request.form["icerik"]
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute("INSERT INTO notlar (baslik, icerik) VALUES (%s, %s)", (baslik, icerik))
    conn.commit()
    conn.close()
    return '<h1>Not kaydedildi!</h1><a href="/">Geri don</a><br><a href="/notlar">Notlara git</a>'

@app.route("/notlar")
def notlari_goster():
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute("SELECT id, baslik, icerik FROM notlar ORDER BY id DESC")
    notlar = cur.fetchall()
    conn.close()
    html = "<h1>Notlar</h1>"
    if not notlar:
        html += "<p>Hic not yok.</p>"
    for not_ in notlar:
        html += f"<div><h3>#{not_[0]} — {not_[1]}</h3><p>{not_[2]}</p><hr></div>"
    html += '<br><a href="/">Geri don</a>'
    return html

if __name__ == "__main__":
    db_hazir_mi()       # Önce bekle
    tablo_olustur()     # Sonra tabloyu oluştur
    app.run(host="0.0.0.0", port=5000)
