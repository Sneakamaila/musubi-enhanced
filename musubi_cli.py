#!/usr/bin/env python3
"""
Musubi 3D CLI - Command Line Tool for Batch Converting Images to Musubi 3D MP4 Videos
Compliant with official Looking Glass Hololuminescent Display (HLD) specifications.
"""

import argparse
import sys
import os
import time
from musubi_core import Musubi3DConverter, __version__

def main():
    parser = argparse.ArgumentParser(
        description="Musubi 3D Video Converter: Turn 2D photos into holographic MP4 videos for Looking Glass Musubi."
    )
    parser.add_argument("-v", "--version", action="version", version=f"Musubi 3D Studio v{__version__} (HLD Architecture Compliant)")
    parser.add_argument("input", nargs="?", help="Path to input photo (JPG, PNG, WebP)")
    parser.add_argument("-o", "--output", default=None, help="Path to output MP4 video (default: <input>_musubi.mp4)")
    parser.add_argument(
        "--mode",
        choices=["hld_card", "full", "simulated_box"],
        default="hld_card",
        help="Presentation mode: hld_card (Pre-matted White for real Musubi frame), full (edge-to-edge 9:16), simulated_box (for PC preview)"
    )
    parser.add_argument("--sway", type=float, default=8.0, help="Parallax sway amount (default: 8.0, recommended 6.0-12.0 for HLD)")
    parser.add_argument("--axis", choices=["x", "circle", "figure8"], default="x", help="Camera motion axis: x (horizontal), circle, figure8")
    parser.add_argument("--duration", type=float, default=6.0, help="Video duration in seconds (default: 6.0, seamless loop)")
    parser.add_argument("--fps", type=int, default=30, help="Framerate in FPS (default: 30)")
    parser.add_argument("--resolution", choices=["576x1024", "1080x1920", "2160x3840"], default="576x1024", help="Video resolution (default: 576x1024 native Musubi)")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.output is None:
        base, _ = os.path.splitext(args.input)
        args.output = f"{base}_musubi_{args.mode}.mp4"

    res_map = {
        "576x1024": (576, 1024),
        "1080x1920": (1080, 1920),
        "2160x3840": (2160, 3840)
    }
    res = res_map.get(args.resolution, (576, 1024))

    print(f"=== Musubi 3D Video Converter (HLD Architecture) ===")
    print(f"Input:       {args.input}")
    print(f"Output:      {args.output}")
    print(f"Mode:        {args.mode}")
    print(f"Resolution:  {res[0]}x{res[1]} (9:16 Portrait)")
    print(f"Sway:        {args.sway} | Axis: {args.axis}")
    print(f"Duration:    {args.duration}s @ {args.fps} FPS")
    print("-----------------------------------------------------")

    t0 = time.time()
    converter = Musubi3DConverter()
    
    def on_progress(current, total):
        pct = int((current / total) * 100)
        sys.stdout.write(f"\rRendering HLD video: [{current}/{total}] {pct}%")
        sys.stdout.flush()

    converter.convert_image_to_musubi_video(
        input_image_path=args.input,
        output_video_path=args.output,
        duration=args.duration,
        fps=args.fps,
        sway_amount=args.sway,
        sway_axis=args.axis,
        mode=args.mode,
        target_resolution=res,
        progress_callback=on_progress
    )
    print("\n-----------------------------------------------------")
    print(f"Success! Finished in {time.time() - t0:.1f}s.")
    print(f"Musubi-ready video saved to: {args.output}")
    print("You can now import this MP4 into the Musubi Desktop App or copy it to your Musubi frame.")

if __name__ == "__main__":
    main()
