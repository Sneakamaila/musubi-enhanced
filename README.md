# Musubi 3D Studio (musubi-enhanced) ❖

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![Unraid](https://img.shields.io/badge/Unraid-Compatible-orange.svg)](unraid-musubi-enhanced.xml)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Looking Glass](https://img.shields.io/badge/Looking%20Glass-Musubi%207%22-purple.svg)](https://lookingglassfactory.com)

**Musubi 3D Studio** ist eine moderne, KI-gestützte Komplettlösung zur Generierung von hochwertigen 3D-Parallax-Videos (`.mp4`) für den **Looking Glass Musubi** holografischen Bilderrahmen.

Die Anwendung dient als leistungsstarke Alternative zur Standard-Software und ermöglicht die professionelle Aufbereitung von 2D-Fotos zu räumlichen 3D-Videoloops mit feiner Tiefenstaffelung und sauber rekonstruierten Bildinhalten.

---

## ✨ Features & Highlights

* **Modernste KI-Tiefenschätzung (Depth-Anything-V2):**  
  Berechnet detaillierte, metrisch stimmige Tiefenkarten mit präzisen Trennkanten um Personen, Haare und feine Konturen.
* **Intelligentes Disocclusion Inpainting:**  
  Bei Kameraschwenks verdeckte Bildbereiche werden im Hintergrund nahtlos und fotorealistisch rekonstruiert. Keine Löcher, kein Tearing und keine unschönen Kanten-Artefakte.
* **Harmonische Sinus-Kamerabewegung (Nahtloser Loop):**  
  Die virtuelle Kamera schwenkt entlang einer mathematischen Sinuskurve. Start- und Endframe sind exakt identisch, wodurch das Video auf dem Rahmen in einer perfekten, ruckelfreien Endlosschleife läuft.
* **Wählbare Präsentations-Modi:**
  - *Vollbild 9:16 (Immersiv):* Das Foto füllt das Display randlos aus – ideal für Landschafts- und Personenaufnahmen.
  - *Musubi Diorama-Box:* Die Fotokarte schwebt mit weichem Schattenwurf und Decken-Spotlight in einem virtuellen 3D-Schattenkasten.
* **Natives Musubi-Format:**  
  Exportiert direkt als H.264 MP4 in 576 × 1024 Pixeln (9:16 Portrait) oder wahlweise Full HD (1080 × 1920) bei 30 oder 60 FPS.
* **Intuitive Bedienung:**  
  Moderne Web-Oberfläche mit Drag & Drop, Vorschau von Tiefenkarte und rekonstruiertem Hintergrund sowie ein CLI-Tool für die automatisierte Stapelverarbeitung.
* **Cloud- & Server-Ready:**  
  Vollständig vorkonfiguriert für **Docker** und **Unraid**.

---

## 🐳 Installation auf Unraid Server (Docker)

### Option 1: Docker Compose (Empfohlen)

Wenn du das Unraid-Plugin **Docker Compose Manager** nutzt:

1. Repository in dein Appdata-Verzeichnis klonen:
   ```bash
   cd /mnt/user/appdata
   git clone https://github.com/Sneakamaila/musubi-enhanced.git
   cd musubi-enhanced
   ```
2. Container starten:
   ```bash
   docker compose up -d --build
   ```
3. Im Browser öffnen:  
   **`http://<DEINE-UNRAID-IP>:5151`**

---

### Option 2: Unraid Docker Template (XML)

Kopiere die Vorlage [`unraid-musubi-enhanced.xml`](unraid-musubi-enhanced.xml) in dein Unraid-Flash-Laufwerk:
```bash
cp unraid-musubi-enhanced.xml /boot/config/plugins/dockerMan/templates-user/my-musubi-enhanced.xml
```
Gehe danach in der Unraid Web-GUI auf den Tab **Docker** ➔ **Add Container** ➔ wähle die Vorlage **musubi-enhanced** aus.

#### Pfad-Zuweisungen (Volume Mappings):
| Host-Pfad (Unraid) | Container-Pfad | Beschreibung |
|---|---|---|
| `/mnt/user/appdata/musubi/outputs` | `/app/outputs` | Speicherort der generierten MP4-Videos |
| `/mnt/user/appdata/musubi/uploads` | `/app/uploads` | Zwischenspeicher für hochgeladene Bilder |
| `/mnt/user/appdata/musubi/models`  | `/app/models`  | Zwischenspeicher für KI-Gewichte |
| Port `5151` | `5151` | Web-Oberfläche |

---

### Option 3: Direkter Docker Run Befehl
```bash
docker build -t musubi-enhanced:latest .

docker run -d \
  --name=musubi-enhanced \
  -p 5151:5151 \
  -v /mnt/user/appdata/musubi/outputs:/app/outputs \
  -v /mnt/user/appdata/musubi/uploads:/app/uploads \
  -v /mnt/user/appdata/musubi/models:/app/models \
  --restart unless-stopped \
  musubi-enhanced:latest
```

---

## 💻 Lokale Installation (ohne Docker)

Voraussetzungen: Python 3.10+, `ffmpeg`

```bash
# 1. Repository klonen
git clone https://github.com/Sneakamaila/musubi-enhanced.git
cd musubi-enhanced

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Web-Studio starten
./start_studio.sh
```
Öffne anschließend **`http://localhost:5151`** im Browser.

---

## 🛠️ Verwendung

### Grafische Web-Oberfläche (Web UI)
1. Ziehe dein Foto per **Drag & Drop** in die Web-App.
2. Kontrolliere sofort die **KI-Tiefenkarte** und den **aufgefüllten Hintergrund**.
3. Wähle den gewünschten Modus (*Vollbild 9:16* oder *Musubi Diorama*).
4. Passe die Schwenkstärke (Parallaxe), Achse (Horizontal, Kreis, 8er-Schleife) und Dauer (3–15 s) an.
5. Klicke auf **"Musubi-Video erstellen"** und lade die fertige `.mp4`-Datei direkt herunter.

### CLI (Kommandozeile für Stapelverarbeitung)
```bash
# Standardkonvertierung:
python3 musubi_cli.py mein_foto.jpg -o output.mp4

# Erweiterte Optionen:
python3 musubi_cli.py mein_foto.jpg \
  --mode diorama \
  --sway 12.0 \
  --axis x \
  --duration 6.0 \
  --fps 30 \
  --resolution 576x1024
```

---

## 📲 Video auf den Looking Glass Musubi übertragen

1. Öffne die offizielle **Looking Glass Musubi App** auf deinem PC oder Mac.
2. Ziehe die von *Musubi 3D Studio* erstellte `.mp4`-Datei per Drag & Drop in die App (die Desktop-Software akzeptiert MP4-Videos direkt als Hologramm-Momente).
3. Schließe den Musubi per USB-C-Kabel an und synchronisiere das Album auf den internen Gerätespeicher.

---

## 📄 Lizenz
MIT License. Erstellt für die Looking Glass Musubi Community.
