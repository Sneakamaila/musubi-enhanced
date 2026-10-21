"""
Musubi 3D Engine - Core Processing Module (v2.0 Clean DIBR)
High-precision 2D to 3D Parallax Video Converter for Looking Glass Musubi
Features:
- Depth-Anything-V2 ONNX inference with auto-download
- Continuous-Depth Forward Warping with Z-Buffering (no destructive layer slicing!)
- True geometric disocclusion hole detection and background-aware inpainting
- Multi-plane depth parallax across all scene elements (foreground, midground, background)
- Harmonic sinusoidal camera trajectories (seamless, jitter-free loops)
- Optimized 9:16 H.264 MP4 export (576x1024 native / 1080x1920 Full HD)
"""

import os
import sys
import urllib.request
import cv2
import numpy as np
import onnxruntime as ort

MODEL_URL = "https://huggingface.co/yuvraj108c/Depth-Anything-2-Onnx/resolve/main/depth_anything_v2_vits.onnx"

def download_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    percent = min(100, percent)
    sys.stdout.write(f"\rDownloading Depth-Anything-V2 ONNX model: {percent}%")
    sys.stdout.flush()

def ensure_model_exists(model_path):
    if not os.path.exists(model_path):
        os.makedirs(os.path.dirname(os.path.abspath(model_path)), exist_ok=True)
        print(f"Model not found locally at {model_path}.")
        print("Downloading Depth-Anything-V2 ONNX model from Hugging Face...")
        urllib.request.urlretrieve(MODEL_URL, model_path, reporthook=download_progress)
        print("\nModel downloaded successfully!")

class Musubi3DConverter:
    def __init__(self, model_path=None):
        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "models", "depth_anything_v2_vits.onnx")
        self.model_path = model_path
        ensure_model_exists(self.model_path)
        
        # Initialize ONNX Runtime session
        self.session = ort.InferenceSession(self.model_path, providers=['CPUExecutionProvider'])

    def estimate_depth(self, img_bgr):
        """
        Calculates high-resolution metric/relative depth map using Depth-Anything-V2.
        Returns float32 depth map normalized to [0.0, 1.0], where 1.0 is near and 0.0 is far.
        """
        h, w = img_bgr.shape[:2]
        resized = cv2.resize(img_bgr, (518, 518))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        
        # ImageNet normalization
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        norm = (rgb - mean) / std
        blob = np.transpose(norm, (2, 0, 1))[np.newaxis, :, :, :]
        
        depth_out = self.session.run(None, {'input': blob})[0][0, 0]
        # Normalize: near = 1.0, far = 0.0
        d_min, d_max = depth_out.min(), depth_out.max()
        depth = (depth_out - d_min) / (d_max - d_min + 1e-8)
        depth = cv2.resize(depth, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Edge-preserving bilateral filter to suppress depth noise while keeping sharp edges
        depth_u8 = (depth * 255).astype(np.uint8)
        depth_filtered = cv2.bilateralFilter(depth_u8, d=5, sigmaColor=30, sigmaSpace=5)
        depth = depth_filtered.astype(np.float32) / 255.0
        
        return depth

    def render_dibr_frame(self, img_bgr, depth, shift_x, shift_y=0.0, focus_depth=0.65, max_shift=14.0):
        """
        Continuous Depth-Image-Based Rendering (DIBR) with Z-buffering.
        Does NOT segment or destroy objects.
        Renders full 3D parallax and inpaints only the genuine geometric disocclusion gaps.
        """
        h, w = img_bgr.shape[:2]
        
        # Parallax displacement based on distance from focal plane
        # Objects closer than focus_depth move forward; farther objects move backward.
        dx = (depth - focus_depth) * max_shift * shift_x
        dy = (depth - focus_depth) * max_shift * shift_y
        
        grid_y, grid_x = np.indices((h, w), dtype=np.float32)
        target_x = grid_x + dx
        target_y = grid_y + dy
        
        warped = np.zeros_like(img_bgr)
        z_buf = np.full((h, w), -1.0, dtype=np.float32)
        
        # Vectorized projection
        fx = target_x.ravel()
        fy = target_y.ravel()
        fz = depth.ravel()
        fc = img_bgr.reshape(-1, 3)
        
        valid = (fx >= 0) & (fx < w - 1) & (fy >= 0) & (fy < h - 1)
        fx = fx[valid]
        fy = fy[valid]
        fz = fz[valid]
        fc = fc[valid]
        
        # Sort ascending by depth: nearer pixels (higher depth) are drawn last and overwrite farther ones
        order = np.argsort(fz)
        fx = fx[order]
        fy = fy[order]
        fz = fz[order]
        fc = fc[order]
        
        ix0 = np.floor(fx).astype(int)
        iy0 = np.floor(fy).astype(int)
        
        # 2x2 bilinear splatting to prevent sampling pinholes
        for ox, oy in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            px = np.clip(ix0 + ox, 0, w - 1)
            py = np.clip(iy0 + oy, 0, h - 1)
            z_buf[py, px] = fz
            warped[py, px] = fc
            
        # Detect true disocclusion holes (pixels where no surface landed)
        holes = (z_buf < 0).astype(np.uint8) * 255
        
        # Inpaint only the actual disocclusion boundaries
        if np.any(holes > 0):
            filled = cv2.inpaint(warped, holes, inpaintRadius=3, flags=cv2.INPAINT_NS)
        else:
            filled = warped
            
        return filled

    def convert_image_to_musubi_video(
        self,
        input_image_path,
        output_video_path,
        duration=6.0,
        fps=30,
        sway_amount=12.0,
        sway_axis="x", # "x" (horizontal), "circle", or "figure8"
        mode="full", # "full" (immersive 9:16) or "diorama" (Musubi shadowbox)
        target_resolution=(576, 1024), # Musubi native display resolution
        progress_callback=None
    ):
        """
        Generates a Musubi-ready MP4 video from a 2D image using clean DIBR.
        """
        img = cv2.imread(input_image_path)
        if img is None:
            raise ValueError(f"Could not read image from {input_image_path}")
            
        target_w, target_h = target_resolution
        ih, iw = img.shape[:2]
        
        if mode == "full":
            scale = max(target_w / iw, target_h / ih)
            nw, nh = int(iw * scale), int(ih * scale)
            resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_CUBIC)
            sx = (nw - target_w) // 2
            sy = (nh - target_h) // 2
            base_img = resized[sy:sy+target_h, sx:sx+target_w]
        else: # diorama mode
            card_w = int(target_w * 0.82)
            card_h = int(card_w * (ih / iw))
            if card_h > int(target_h * 0.70):
                card_h = int(target_h * 0.70)
                card_w = int(card_h * (iw / ih))
            base_img = cv2.resize(img, (card_w, card_h), interpolation=cv2.INTER_CUBIC)

        h, w = base_img.shape[:2]
        depth = self.estimate_depth(base_img)
        
        # Automatically detect the focal subject depth
        # Look at the bottom-center region (typical portrait subject location)
        sub_h0, sub_h1 = int(h * 0.4), int(h * 0.95)
        sub_w0, sub_w1 = int(w * 0.25), int(w * 0.75)
        subject_region = depth[sub_h0:sub_h1, sub_w0:sub_w1]
        if subject_region.size > 0:
            focus_depth = float(np.median(subject_region))
        else:
            focus_depth = float(np.median(depth))
            
        total_frames = int(duration * fps)
        temp_raw = output_video_path + ".temp.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_raw, fourcc, fps, (target_w, target_h))
        
        # Shadowbox background for diorama mode
        if mode == "diorama":
            box_bg = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            for y_i in range(target_h):
                val = int(22 + 30 * (1.0 - y_i / target_h)) # soft overhead spotlight
                box_bg[y_i, :] = (val, val, val + 3)
            card_x0 = (target_w - w) // 2
            card_y0 = (target_h - h) // 2

        for i in range(total_frames):
            phase = (2 * np.pi * i) / total_frames
            
            if sway_axis == "circle":
                shift_x = np.sin(phase)
                shift_y = np.cos(phase) * 0.35
            elif sway_axis == "figure8":
                shift_x = np.sin(phase)
                shift_y = np.sin(2 * phase) * 0.30
            else: # horizontal x-axis sway (standard for 3D parallax)
                shift_x = np.sin(phase)
                shift_y = 0.0
                
            composite = self.render_dibr_frame(
                base_img,
                depth,
                shift_x=shift_x,
                shift_y=shift_y,
                focus_depth=focus_depth,
                max_shift=sway_amount
            )
            
            if mode == "full":
                frame_out = composite
            else:
                frame_out = box_bg.copy()
                tilt_dx = int(shift_x * 8)
                cx = card_x0 + tilt_dx
                cy = card_y0
                
                # Soft realistic shadow underneath the floating memory card
                shadow_mask = np.zeros((target_h, target_w), dtype=np.uint8)
                cv2.rectangle(shadow_mask, (cx - 4, cy + 6), (cx + w + 4, cy + h + 18), 200, -1)
                shadow_mask = cv2.GaussianBlur(shadow_mask, (35, 35), 0)
                shadow_fac = (1.0 - (shadow_mask.astype(np.float32) / 255.0) * 0.65)[:, :, np.newaxis]
                frame_out = (frame_out * shadow_fac).astype(np.uint8)
                
                # Rounded card overlay
                card_mask = np.ones((h, w), dtype=np.float32)
                cv2.rectangle(card_mask, (0, 0), (w, h), 1.0, -1)
                card_alpha = cv2.GaussianBlur(card_mask, (5, 5), 0)[:, :, np.newaxis]
                
                roi = frame_out[cy:cy+h, cx:cx+w]
                frame_out[cy:cy+h, cx:cx+w] = (composite * card_alpha + roi * (1.0 - card_alpha)).astype(np.uint8)
                
            out.write(frame_out)
            if progress_callback:
                progress_callback(i + 1, total_frames)
                
        out.release()
        
        # Final encode with ffmpeg into standard H.264 MP4 with faststart
        os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)
        cmd = f"ffmpeg -y -i '{temp_raw}' -c:v libx264 -pix_fmt yuv420p -profile:v high -level 4.0 -crf 18 -movflags +faststart '{output_video_path}' > /dev/null 2>&1"
        os.system(cmd)
        if os.path.exists(temp_raw):
            os.remove(temp_raw)
            
        return output_video_path
