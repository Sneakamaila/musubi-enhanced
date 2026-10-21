# Musubi 3D Studio (musubi-enhanced) ❖

[![Version](https://img.shields.io/badge/version-v2.2.1-emerald.svg)](https://github.com/Sneakamaila/musubi-enhanced)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![Unraid](https://img.shields.io/badge/Unraid-Compatible-orange.svg)](unraid-musubi-enhanced.xml)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Looking Glass HLD](https://img.shields.io/badge/Looking%20Glass-HLD%20Architecture-purple.svg)](https://hlddocs.lookingglassfactory.com/)

**Musubi 3D Studio** ist eine KI-gestützte Komplettlösung zur Generierung von hochwertigen 3D-Parallax-Videos (`.mp4`) für den **Looking Glass Musubi** und die gesamte **Hololuminescent™ Display (HLD)** Produktfamilie.

Entwickelt unter strikter Berücksichtigung der offiziellen [Looking Glass HLD Dokumentation](https://hlddocs.lookingglassfactory.com/).

---

## 🔬 Was ist neu in v2.2.1?

* **Fix für 3D-Hologramm (`hld_subject`):**  
  Behebt den Bug, bei dem nur der Umriss (Drahtgitter) der Personen gezeichnet wurde. Motive werden nun vollflächig und solide mit Bodenschatten freigestellt.
* **Nativer Transparenz-Support (PNG mit Alpha-Kanal):**  
  Bilder mit vorhandener Transparenz (z. B. Sticker, iOS-Freisteller, Blender-Renders, Photoshop) werden nativ 1:1 als schwebende 3D-Hologramme ohne Segmentierungsverlust gerendert.
* **Empfehlung für Standardfotos:**  
  Für herkömmliche Fotos bleibt der Modus **`hld_card` (HLD-Fotokarte)** der offizielle, empfohlene Standard, um das gesamte Foto mitsamt Hintergrunddetails harmonisch im Glaskasten schweben zu lassen.

---

## 💡 HLD-Optik: Warum kein Vollbild auf dem Musubi?

Das Looking Glass Musubi ist ein **Hololuminescent Display (HLD)**. Es kombiniert ein Front-LCD mit einem echten, physischen 3D-Schaukasten („Alcove“) im optischen **Multiply-Mischmodus**:
- **Reines Weiß (`#FFFFFF`) ist optisch zu 100 % transparent.** Licht passiert ungehindert das Display – man blickt direkt in den echten Schaukasten.
- **Farben & Schatten verdunkeln das Licht** und projizieren das 3D-Objekt schwebend in die Tiefe.
- **Ein opakes Vollbild-Video (Rechteck) verdeckt den physischen Schaukasten** und bricht die optische Tiefenillusion.

### Empfohlene Ausgabe-Modi:

1. **`hld_card` (HLD-Fotokarte – Standard & Empfohlen):**  
   Das Foto wird als elegante, abgerundete 3D-Karte auf reinweißem Grund mit weichem Bodenschatten gerendert. Auf dem Musubi schwebt die Erinnerung magisch im physischen Schaukasten.
2. **`hld_subject` (Freigestelltes 3D-Hologramm):**  
   Nur die Person oder das Objekt schwebt freigestellt im Schaukasten – ganz ohne rechteckigen Fotorahmen.
3. **`simulated_box` (Simulierte Box – PC-Vorschau):**  
   Rendert für 2D-Monitore die Deckenbeleuchtung und Wände der Alcove mit, um die Wirkung am PC zu prüfen.
4. **`full` (Vollbild 9:16 – Legacy 2D):**  
   Füllt den Bildschirm komplett aus. Nur für herkömmliche 2D-Displays gedacht.

---

## 🐳 Installation auf Unraid Server (Docker)

### Erstinstallation via Docker Compose:

```bash
cd /mnt/user/appdata
git clone https://github.com/Sneakamaila/musubi-enhanced.git
cd musubi-enhanced
docker compose up -d --build
```
Öffne anschließend im Browser: **`http://<DEINE-UNRAID-IP>:5151`**

---

### Update auf die neueste Version (v2.2.0):

Falls dein lokales Git-Repository auf Unraid abweicht (divergent branches), führe diesen Einzeiler aus:

```bash
cd /mnt/user/appdata/musubi-enhanced
git fetch origin
git reset --hard origin/main
docker compose up -d --build
```

---

## 💻 Lokale Installation (ohne Docker)

Voraussetzungen: Python 3.10+, `ffmpeg`

```bash
git clone https://github.com/Sneakamaila/musubi-enhanced.git
cd musubi-enhanced
pip install -r requirements.txt
python3 musubi_web.py
```
Öffne **`http://localhost:5151`** im Browser.

---

## 🛠️ Verwendung

### Web-Oberfläche:
1. Foto per **Drag & Drop** in die Web-App ziehen.
2. Vorschau prüfen (**KI-Tiefenkarte** & **3D-Vorschau**).
3. Modus wählen (**HLD-Fotokarte** oder **3D-Hologramm**).
4. Klick auf **"Musubi-Video erstellen"** – das flüssige `.mp4` wird gerendert und kann sofort abgespielt oder heruntergeladen werden.

### CLI (Kommandozeile):
```bash
python3 musubi_cli.py foto.jpg \
  --mode hld_card \
  --sway 8.0 \
  --axis x \
  --duration 6.0 \
  --fps 30 \
  --resolution 576x1024
```

---

## 📲 Video auf den Looking Glass Musubi übertragen

1. Öffne die offizielle **Looking Glass Musubi App** auf deinem Computer.
2. Ziehe die generierte `.mp4`-Datei per Drag & Drop in die App.
3. Musubi per USB-C verbinden und synchronisieren.

---

## 📄 Lizenz
MIT License. Erstellt für die Looking Glass HLD Community.
