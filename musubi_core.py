"""
Musubi 3D Engine - Core Processing Module
High-precision 2D to 3D Parallax Video Converter for Looking Glass Musubi
Features:
- Depth-Anything-V2 ONNX inference with auto-download
- Disocclusion Inpainting (eliminates voids and edge tearing)
- Layered Depth Image-Based Rendering (DIBR)
- Seamless sinusoidal looping camera trajectories
- Optimized 9:16 H.264 MP4 export for Looking Glass Musubi
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
        print(f"Downloading Depth-Anything-V2 ONNX model from Hugging Face...")
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
        return depth

    def prepare_layers(self, img_bgr, depth, max_shift=16):
        """
        Segments foreground and cleanly inpaints the occluded background region.
        Eliminates the missing background void / white spots completely.
        """
        h, w = img_bgr.shape[:2]
        
        # Automatically determine foreground threshold
        fg_thresh = np.percentile(depth, 55)
        fg_raw = (depth >= fg_thresh).astype(np.uint8) * 255
        
        # Clean mask via morphological filters
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        fg_clean = cv2.morphologyEx(fg_raw, cv2.MORPH_CLOSE, kernel)
        fg_clean = cv2.morphologyEx(fg_clean, cv2.MORPH_OPEN, kernel)
        
        # Keep significant foreground contours
        contours, _ = cv2.findContours(fg_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        clean_mask = np.zeros_like(fg_clean)
        min_area = w * h * 0.015 # at least 1.5% of total frame
        for c in contours:
            if cv2.contourArea(c) > min_area:
                cv2.drawContours(clean_mask, [c], -1, 255, -1)
                
        # Dilate foreground mask to define disocclusion inpainting boundary
        dilation_radius = int(max_shift * 1.8) + 3
        inpaint_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation_radius, dilation_radius))
        inpaint_mask = cv2.dilate(clean_mask, inpaint_kernel, iterations=1)
        
        # Perform inpainting to reconstruct background behind the subjects
        bg_inpainted = cv2.inpaint(img_bgr, inpaint_mask, inpaintRadius=9, flags=cv2.INPAINT_TELEA)
        bg_depth = cv2.inpaint((depth * 255).astype(np.uint8), inpaint_mask, inpaintRadius=9, flags=cv2.INPAINT_TELEA).astype(np.float32) / 255.0
        
        # Soft feather alpha edge for smooth foreground blending
        fg_alpha = cv2.GaussianBlur(clean_mask.astype(np.float32) / 255.0, (15, 15), 0)
        fg_alpha = np.clip(fg_alpha[:, :, np.newaxis], 0.0, 1.0)
        
        return {
            'bg_img': bg_inpainted,
            'bg_depth': bg_depth,
            'fg_img': img_bgr,
            'fg_depth': depth,
            'fg_alpha': fg_alpha,
            'mask': clean_mask
        }

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
        Generates a Musubi-ready MP4 video from a 2D image.
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
            card_w = int(target_w * 0.80)
            card_h = int(card_w * (ih / iw))
            if card_h > int(target_h * 0.68):
                card_h = int(target_h * 0.68)
                card_w = int(card_h * (iw / ih))
            base_img = cv2.resize(img, (card_w, card_h), interpolation=cv2.INTER_CUBIC)

        h, w = base_img.shape[:2]
        depth = self.estimate_depth(base_img)
        layers = self.prepare_layers(base_img, depth, max_shift=int(sway_amount * 1.5))
        
        total_frames = int(duration * fps)
        temp_raw = output_video_path + ".temp.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_raw, fourcc, fps, (target_w, target_h))
        
        grid_x, grid_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        focus_depth = 0.65
        
        # Shadowbox background for diorama mode
        if mode == "diorama":
            box_bg = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            for y_i in range(target_h):
                val = int(24 + 32 * (1.0 - y_i / target_h)) # soft overhead spotlight
                box_bg[y_i, :] = (val, val, val + 3)
            card_x0 = (target_w - w) // 2
            card_y0 = (target_h - h) // 2

        for i in range(total_frames):
            phase = (2 * np.pi * i) / total_frames
            
            if sway_axis == "circle":
                shift_x = np.sin(phase)
                shift_y = np.cos(phase) * 0.5
            elif sway_axis == "figure8":
                shift_x = np.sin(phase)
                shift_y = np.sin(2 * phase) * 0.4
            else: # horizontal x-axis sway (standard for 3D parallax)
                shift_x = np.sin(phase)
                shift_y = 0.0
                
            # Displacements
            bg_disp_x = (layers['bg_depth'] - focus_depth) * sway_amount * shift_x
            bg_disp_y = (layers['bg_depth'] - focus_depth) * sway_amount * shift_y
            fg_disp_x = (layers['fg_depth'] - focus_depth) * sway_amount * shift_x
            fg_disp_y = (layers['fg_depth'] - focus_depth) * sway_amount * shift_y
            
            # Warp background
            bg_src_x = np.clip(grid_x - bg_disp_x, 0, w - 1).astype(np.float32)
            bg_src_y = np.clip(grid_y - bg_disp_y, 0, h - 1).astype(np.float32)
            warped_bg = cv2.remap(layers['bg_img'], bg_src_x, bg_src_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            
            # Warp foreground
            fg_src_x = np.clip(grid_x - fg_disp_x, 0, w - 1).astype(np.float32)
            fg_src_y = np.clip(grid_y - fg_disp_y, 0, h - 1).astype(np.float32)
            warped_fg = cv2.remap(layers['fg_img'], fg_src_x, fg_src_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            warped_alpha = cv2.remap(layers['fg_alpha'], fg_src_x, fg_src_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            if len(warped_alpha.shape) == 2:
                warped_alpha = warped_alpha[:, :, np.newaxis]
                
            composite = (warped_fg * warped_alpha + warped_bg * (1.0 - warped_alpha)).astype(np.uint8)
            
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
