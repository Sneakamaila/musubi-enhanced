# Musubi 3D Studio (musubi-enhanced) ❖

[![Version](https://img.shields.io/badge/version-v2.1.0-emerald.svg)](https://github.com/Sneakamaila/musubi-enhanced)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)
[![Unraid](https://img.shields.io/badge/Unraid-Compatible-orange.svg)](unraid-musubi-enhanced.xml)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![Looking Glass HLD](https://img.shields.io/badge/Looking%20Glass-HLD%20Architecture-purple.svg)](https://hlddocs.lookingglassfactory.com/)

**Musubi 3D Studio** ist eine KI-gestützte Komplettlösung zur Generierung von hochwertigen 3D-Parallax-Videos (`.mp4`) für den **Looking Glass Musubi** und die gesamte **Hololuminescent™ Display (HLD)** Produktfamilie.

Die Anwendung wurde unter strikter Berücksichtigung der offiziellen [Looking Glass HLD Dokumentation](https://hlddocs.lookingglassfactory.com/) entwickelt. Sie erzeugt exakt nach den optischen und physikalischen Anforderungen der HLD-Technologie aufbereitete Medien.

---

## 🔬 HLD-Konforme Kernfeatures

* **Pre-matted Reines Weiß (`#FFFFFF`) für echte HLD-Transparenz:**  
  HLD-Displays kombinieren ein Frontdisplay mit einer physischen holografischen Lichtkammer ("Alcove") im optischen Multiplikations-Mischmodus (*Multiply*). Reines Weiß (`1.0`) wirkt optisch zu 100 % transparent. Der `hld_card`-Modus bettet Fotos mit feinen Rundungen auf reinweißem Grund ein, sodass das Bild frei im physischen 3D-Schaukasten des Musubi schwebt.
* **Physikalischer Boden-Kontaktschatten:**  
  Ein berechneter, weich auslaufender Kontaktschatten multipliziert sich direkt mit dem Boden des physischen 3D-Kastens und verankert die Erinnerung räumlich in der Box.
* **Safe-Areas der Alcove:**  
  Einhaltung der offiziellen Sicherheitsränder (~3–4 % Randabstand), damit Bildinhalte niemals an die Wände oder die Decke des Schaukastens stoßen.
* **Subtile, natürliche Parallaxe (2°–5° Richtlinie):**  
  Statt übertriebener Drehungen, die das menschliche Auge überfordern, nutzt das Studio feinfühlig kalibrierte Kameraschwünge (~2.4°), die für lebendige, natürliche Raumtiefe ohne Geisterbilder sorgen.
* **Clean-DIBR v2 Engine:**  
  Kontinuierliche Vorwärtsprojektion mit Z-Buffering. Kein Zerschneiden von Objekten in künstliche Ebenen – sämtliche Bilddetails (z. B. Bäume, Haare, Hintergründe) bleiben gestochen scharf.
* **Präzise KI-Tiefenschätzung (Depth-Anything-V2):**  
  Modernste Tiefenkarten mit exakter räumlicher Trennung.
* **HLD Video-Spezifikationen:**  
  Exportiert direkt als H.264 MP4 im **BT.709 Farbraum** (`yuv420p`, High Profile, Faststart), nativ optimiert für den integrierten Musubi-Hardwareplayer.

---

## 🎨 Verfügbare Ausgabe-Modi

1. **`hld_card` (Musubi HLD-Card – Standard für die Hardware):**  
   Die Fotokarte schwebt mit kontinuierlicher Raumtiefe im echten Musubi-Schaukasten. Der Hintergrund ist pre-matted reinweiß und auf dem echten Musubi transparent.
2. **`simulated_box` (Simulierte Alcove – PC-Monitor-Vorschau):**  
   Zeichnet den virtuellen Schaukasten mit Wänden und Deckenbeleuchtung – ideal zur Beurteilung des Effekts auf normalen 2D-Bildschirmen.
3. **`full` (Vollbild 9:16 Immersiv):**  
   Füllt das gesamte Display randlos mit flüssiger 3D-Parallaxe aus.

---

## 🐳 Installation auf Unraid Server (Docker)

### Option 1: Docker Compose (Empfohlen)

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
3. Im Browser öffnen: **`http://<DEINE-UNRAID-IP>:5151`**

---

### Option 2: Unraid Docker Template (XML)

Kopiere die Vorlage [`unraid-musubi-enhanced.xml`](unraid-musubi-enhanced.xml) in dein Unraid-Flash-Laufwerk:
```bash
cp unraid-musubi-enhanced.xml /boot/config/plugins/dockerMan/templates-user/my-musubi-enhanced.xml
```
Wähle in der Unraid Web-GUI unter **Docker** ➔ **Add Container** die Vorlage **musubi-enhanced** aus.

#### Pfad-Zuweisungen (Volume Mappings):
| Host-Pfad (Unraid) | Container-Pfad | Beschreibung |
|---|---|---|
| `/mnt/user/appdata/musubi/outputs` | `/app/outputs` | Speicherort der generierten MP4-Videos |
| `/mnt/user/appdata/musubi/uploads` | `/app/uploads` | Zwischenspeicher für hochgeladene Bilder |
| `/mnt/user/appdata/musubi/models`  | `/app/models`  | Zwischenspeicher für KI-Gewichte |
| Port `5151` | `5151` | Web-Oberfläche |

---

## 💻 Lokale Installation (ohne Docker)

Voraussetzungen: Python 3.10+, `ffmpeg`

```bash
git clone https://github.com/Sneakamaila/musubi-enhanced.git
cd musubi-enhanced
pip install -r requirements.txt
./start_studio.sh
```
Öffne anschließend **`http://localhost:5151`** im Browser.

---

## 🛠️ Verwendung

### Grafische Web-Oberfläche (Web UI)
1. Foto per **Drag & Drop** in die Web-App ziehen.
2. Vorschau der **KI-Tiefenkarte** und des **3D-Parallax-Effekts** prüfen.
3. Modus wählen (*HLD-Card für echten Musubi*, *Simulierte Box* oder *Vollbild 9:16*).
4. Kameraschwenk einstellen (Standard: 8 px / ~2.4° für HLD).
5. Klick auf **"Musubi-Video erstellen"** – das fertige `.mp4` wird sofort gerendert und steht zum Download bereit.

### CLI (Kommandozeile)
```bash
# Standardkonvertierung für echten Musubi:
python3 musubi_cli.py foto.jpg -o video_musubi.mp4

# Erweiterte Optionen:
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
2. Ziehe die mit *Musubi 3D Studio* erstellte `.mp4`-Datei per Drag & Drop in die App.
3. Verbinde den Musubi per USB-C-Kabel und synchronisiere die Medien auf das Gerät.

---

## 📄 Lizenz
MIT License. Erstellt für die Looking Glass HLD Community.
