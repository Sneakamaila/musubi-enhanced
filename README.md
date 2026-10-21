# Musubi 3D Studio (musubi-enhanced) ❖

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![Unraid](https://img.shields.io/badge/Unraid-Compatible-orange.svg)](unraid-musubi-enhanced.xml)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Looking Glass](https://img.shields.io/badge/Looking%20Glass-Musubi%207%22-purple.svg)](https://lookingglassfactory.com)

Ein KI-gestütztes Tool und Web-Studio zur Umwandlung von 2D-Fotos in perfekte, lückenlos holografische 3D-Videos (`.mp4`) für den **Looking Glass Musubi** Bilderrahmen.

---

## 🔍 Das Problem: Warum hat die offizielle Software den weißen Fleck?

In der offiziellen Looking Glass Musubi Companion-Software entsteht hinter freigestellten Personen (z. B. am Kopf/Hals) oft ein auffälliger weißer Fleck:

1. **Fehlende Disocclusion-Rekonstruktion:**  
   Beim 3D-Schwenk (z. B. 15° Y-Achse) bewegt sich der Vordergrund schneller als der Hintergrund. Die Bildteile des Meeres/Himmels, die im Originalfoto *hinter* der Person lagen, existieren im flachen 2D-Bild nicht. Die Standard-App füllt diesen verdeckten Bereich nicht auf, sondern lässt ein leeres Maskenloch.
2. **"Background Color" ist auf Weiß gesetzt:**  
   Im Einstellungs-Panel der Musubi-App steht die Option `Background Color` standardmäßig auf Weiß (`#FFFFFF`). Durch das verdeckte Loch scheint der weiße Hintergrund durch.
3. **Zu starker Wiggle-Winkel:**  
   Ein Schwenk von 15° ist für ein einzelnes 2D-Foto extrem groß und erzeugt riesige Okklusionslücken.

### ✨ Was macht *Musubi 3D Studio* besser?
* **Depth-Anything-V2 KI:** Berechnet gestochen scharfe Tiefenkarten mit präzisen Kanten um Haare, Schultern und Konturen.
* **Disocclusion Inpainting:** Reconstructiert und malt den verdeckten Hintergrund (Meer, Wellen, Himmel) hinter Personen nahtlos weiter. **Keine weißen Flecken, keine Löcher, kein Rubber-Sheet-Tearing!**
* **Harmonischer Sinus-Loop:** Die Kamera schwenkt vollkommen gleichmäßig in einer Dauerschleife (Start- und Endframe sind mathematisch identisch – null Ruckeln).
* **Natives Musubi-Format:** 576 × 1024 Pixel (9:16 Portrait) als hochkompatibles H.264 MP4.
* **Zwei Modi:** Vollbild (9:16 Immersiv) oder Musubi Diorama-Box (schwebende Fotokarte mit weichem Schattenwurf und Decken-Spotlight).

---

## 🐳 Installation auf Unraid Server (Docker)

### Option 1: Docker Compose (Empfohlen)

Wenn du das Unraid-Plugin **Docker Compose Manager** nutzt:

1. Klone das Repository in dein Appdata-Verzeichnis oder erstelle einen neuen Stack:
   ```bash
   cd /mnt/user/appdata
   git clone https://github.com/Sneakamaila/musubi-enhanced.git
   cd musubi-enhanced
   ```
2. Starte den Container:
   ```bash
   docker compose up -d --build
   ```
3. Öffne im Browser: `http://<DEINE-UNRAID-IP>:5151`

---

### Option 2: Unraid Docker Template (XML)

Kopiere die bereitgestellte Vorlage [`unraid-musubi-enhanced.xml`](unraid-musubi-enhanced.xml) in dein Unraid-Flash-Laufwerk:
```bash
cp unraid-musubi-enhanced.xml /boot/config/plugins/dockerMan/templates-user/my-musubi-enhanced.xml
```
Gehe danach in der Unraid Web-GUI auf den Tab **Docker** ➔ **Add Container** ➔ wähle die Vorlage **musubi-enhanced** aus.

#### Wichtige Pfad-Zuweisungen (Volume Mappings):
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
