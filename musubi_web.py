import os
import uuid
import base64
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from musubi_core import Musubi3DConverter

app = FastAPI(title="Musubi 3D Studio")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

converter = None

def get_converter():
    global converter
    if converter is None:
        converter = Musubi3DConverter()
    return converter

# Mount static and outputs
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/health")
async def health():
    return {"status": "ok", "app": "Musubi 3D Studio"}

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Musubi 3D Studio - UI loading...</h1>"

@app.post("/api/preview")
async def generate_preview(file: UploadFile = File(...)):
    conv = get_converter()
    file_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(file.filename)[1].lower() or ".png"
    upload_path = os.path.join(UPLOADS_DIR, f"{file_id}{ext}")
    
    contents = await file.read()
    with open(upload_path, "wb") as f:
        f.write(contents)
        
    img = cv2.imread(upload_path)
    if img is None:
        return JSONResponse({"error": "Invalid image format"}, status_code=400)
        
    # Resize for fast interactive preview
    max_dim = 640
    h, w = img.shape[:2]
    scale = min(max_dim / w, max_dim / h, 1.0)
    prev_w, prev_h = int(w * scale), int(h * scale)
    img_prev = cv2.resize(img, (prev_w, prev_h))
    
    depth = conv.estimate_depth(img_prev)
    # Generate sample 3D parallax view (max displacement)
    prev_focus = float(np.median(depth))
    parallax_prev = conv.render_dibr_frame(img_prev, depth, shift_x=1.0, max_shift=12.0, focus_depth=prev_focus)
    
    # Colorize depth for display
    depth_u8 = (depth * 255).astype(np.uint8)
    depth_color = cv2.applyColorMap(depth_u8, cv2.COLORMAP_VIRIDIS)
    
    _, orig_buf = cv2.imencode('.jpg', img_prev, [cv2.IMWRITE_JPEG_QUALITY, 85])
    _, depth_buf = cv2.imencode('.jpg', depth_color, [cv2.IMWRITE_JPEG_QUALITY, 85])
    _, parallax_buf = cv2.imencode('.jpg', parallax_prev, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    return {
        "file_id": file_id,
        "filename": os.path.basename(upload_path),
        "orig_b64": base64.b64encode(orig_buf).decode('utf-8'),
        "depth_b64": base64.b64encode(depth_buf).decode('utf-8'),
        "parallax_b64": base64.b64encode(parallax_buf).decode('utf-8'),
        "width": w,
        "height": h
    }

@app.post("/api/render")
async def render_video(
    file_id: str = Form(...),
    sway: float = Form(8.0),
    axis: str = Form("x"),
    duration: float = Form(6.0),
    fps: int = Form(30),
    mode: str = Form("hld_card"),
    resolution: str = Form("576x1024")
):
    conv = get_converter()
    matches = [f for f in os.listdir(UPLOADS_DIR) if f.startswith(file_id)]
    if not matches:
        return JSONResponse({"error": "Original file not found"}, status_code=404)
        
    in_path = os.path.join(UPLOADS_DIR, matches[0])
    out_name = f"musubi_{file_id}_{mode}_{int(duration)}s.mp4"
    out_path = os.path.join(OUTPUTS_DIR, out_name)
    
    res_map = {
        "576x1024": (576, 1024),
        "1080x1920": (1080, 1920),
        "2160x3840": (2160, 3840)
    }
    res = res_map.get(resolution, (576, 1024))
    
    conv.convert_image_to_musubi_video(
        input_image_path=in_path,
        output_video_path=out_path,
        duration=duration,
        fps=fps,
        sway_amount=sway,
        sway_axis=axis,
        mode=mode,
        target_resolution=res
    )
    
    return {
        "success": True,
        "video_url": f"/outputs/{out_name}",
        "filename": out_name
    }

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5151))
    uvicorn.run("musubi_web:app", host=host, port=port, reload=False)
