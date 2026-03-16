from flask import Flask, request, redirect
import psycopg2
import os
import time

app = Flask(__name__)

def db_baglantisi():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def db_hazir_mi():
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
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute("SELECT id, baslik, icerik FROM notlar ORDER BY id DESC")
    notlar = cur.fetchall()
    conn.close()

    html = """
        <h1>Not Defteri</h1>
        <form method="POST" action="/not-ekle">
            <input name="baslik" placeholder="Baslik" required><br><br>
            <textarea name="icerik" placeholder="Icerik" required></textarea><br><br>
            <button type="submit">Kaydet</button>
        </form>
        <hr>
        <h2>Notlar</h2>
    """

    if not notlar:
        html += "<p>Hic not yok.</p>"

    for not_ in notlar:
        html += f"""
        <div style="border:1px solid #ccc; padding:10px; margin:10px 0;">
            <h3>#{not_[0]} — {not_[1]}</h3>
            <p>{not_[2]}</p>
            <a href="/duzenle/{not_[0]}">Duzenle</a> |
            <form method="POST" action="/sil/{not_[0]}" style="display:inline">
                <button type="submit" onclick="return confirm('Emin misin?')">Sil</button>
            </form>
        </div>
        """
    return html

@app.route("/not-ekle", methods=["POST"])
def not_ekle():
    baslik = request.form["baslik"]
    icerik = request.form["icerik"]
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute("INSERT INTO notlar (baslik, icerik) VALUES (%s, %s)", (baslik, icerik))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/sil/<int:not_id>", methods=["POST"])
def not_sil(not_id):
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute("DELETE FROM notlar WHERE id = %s", (not_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/duzenle/<int:not_id>")
def duzenle_sayfasi(not_id):
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute("SELECT id, baslik, icerik FROM notlar WHERE id = %s", (not_id,))
    not_ = cur.fetchone()
    conn.close()

    if not not_:
        return "<h1>Not bulunamadi</h1><a href='/'>Geri don</a>"

    return f"""
        <h1>Notu Duzenle</h1>
        <form method="POST" action="/guncelle/{not_[0]}">
            <input name="baslik" value="{not_[1]}" required><br><br>
            <textarea name="icerik" required>{not_[2]}</textarea><br><br>
            <button type="submit">Guncelle</button>
            <a href="/">Iptal</a>
        </form>
    """

@app.route("/guncelle/<int:not_id>", methods=["POST"])
def not_guncelle(not_id):
    baslik = request.form["baslik"]
    icerik = request.form["icerik"]
    conn = db_baglantisi()
    cur = conn.cursor()
    cur.execute(
        "UPDATE notlar SET baslik = %s, icerik = %s WHERE id = %s",
        (baslik, icerik, not_id)
    )
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    db_hazir_mi()
    tablo_olustur()
    app.run(host="0.0.0.0", port=5000)
