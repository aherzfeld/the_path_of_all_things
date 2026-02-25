"""
Converts and optimizes generated Imagen PNGs to WebP for the webapp.
Resizes to 800x600 (2x retina for the modal image area) at 80% quality.
Outputs to public/images/ for use by the game.
"""

import os
from PIL import Image

# ================= CONFIGURATION =================
INPUT_DIR = "generated_images"
OUTPUT_DIR = "public/images"
TARGET_WIDTH = 800
TARGET_HEIGHT = 600
QUALITY = 80
# =================================================


def optimize_image(input_path, output_path):
    """Resize and convert a single image to WebP."""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (e.g. RGBA PNGs)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Resize with high-quality downsampling
            img = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

            # Save as WebP
            img.save(output_path, "WEBP", quality=QUALITY, method=6)

            # File size comparison
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            reduction = (1 - output_size / input_size) * 100

            print(f"  ✓ {os.path.basename(output_path):50s}  "
                  f"{input_size // 1024:>6d}KB → {output_size // 1024:>4d}KB  "
                  f"({reduction:.0f}% smaller)")
            return True

    except Exception as e:
        print(f"  ✗ {os.path.basename(input_path)}: {e}")
        return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find all PNGs in input directory
    png_files = sorted([
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith(".png")
    ])

    if not png_files:
        print(f"No PNG files found in {INPUT_DIR}/")
        return

    print(f"Optimizing {len(png_files)} images")
    print(f"  Source:  {INPUT_DIR}/")
    print(f"  Output:  {OUTPUT_DIR}/")
    print(f"  Size:    {TARGET_WIDTH}x{TARGET_HEIGHT}")
    print(f"  Quality: {QUALITY}%")
    print(f"  Format:  WebP\n")

    success = 0
    failed = 0
    total_input = 0
    total_output = 0

    for filename in png_files:
        input_path = os.path.join(INPUT_DIR, filename)
        # Change extension to .webp, keep the same name
        webp_name = os.path.splitext(filename)[0] + ".webp"
        output_path = os.path.join(OUTPUT_DIR, webp_name)

        if optimize_image(input_path, output_path):
            total_input += os.path.getsize(input_path)
            total_output += os.path.getsize(output_path)
            success += 1
        else:
            failed += 1

    print(f"\nDone! {success} converted, {failed} failed")
    if total_input > 0:
        print(f"Total: {total_input // (1024*1024)}MB → {total_output // (1024*1024)}MB "
              f"({(1 - total_output / total_input) * 100:.0f}% reduction)")


if __name__ == "__main__":
    main()
