import json
import os
import time
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InvalidArgument

# ================= CONFIGURATION =================
PROJECT_ID = "p1-history-images"
LOCATION = "us-central1"

# Full quality model (not the "fast" variant)
MODEL_NAME = "imagen-3.0-generate-002"

# Landscape to match the reference image style
ASPECT_RATIO = "4:3"

OUTPUT_DIR = "generated_images"
JSON_FILE = "src/data_with_prompts.json"

MAX_RETRIES = 3
COOLDOWN_SECS = 60
DELAY_BETWEEN = 10  # seconds between requests
# =================================================


def build_prompt(event):
    """
    Style: black ink wash on aged parchment, like the Big Bang reference.
    The subject should be recognizable but rendered in loose ink wash sumi-e.
    """
    title = event["title"]
    return (
        f"{title}. "
        f"Black ink wash and Sumi-e (wabi sabi) on aged cream parchment paper. "
        f"Monochrome, no color. No text, no words, no letters."
    )


def setup_environment():
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_image(model, prompt, event_id, event_title, retries=0):
    safe_title = event_title.replace(" ", "_").replace("/", "-").replace("'", "")
    filename = f"{event_id}_{safe_title}.png"
    file_path = os.path.join(OUTPUT_DIR, filename)

    if os.path.exists(file_path):
        print(f"  [SKIP] {event_id}: already exists")
        return True

    print(f"  [GEN]  {event_id}: {event_title}")

    try:
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio=ASPECT_RATIO,
            safety_filter_level="block_few",
            person_generation="allow_adult",
        )

        if images:
            images[0].save(location=file_path, include_generation_parameters=True)
            print(f"         -> saved {filename}")
            return True
        else:
            print(f"         -> no image returned")
            return False

    except (ResourceExhausted, ServiceUnavailable):
        if retries < MAX_RETRIES:
            print(f"         -> rate limit, cooling {COOLDOWN_SECS}s (retry {retries+1}/{MAX_RETRIES})")
            time.sleep(COOLDOWN_SECS)
            return generate_image(model, prompt, event_id, event_title, retries + 1)
        else:
            print(f"         -> rate limit, max retries reached — skipping")
            return False

    except InvalidArgument as e:
        print(f"         -> BLOCKED by safety filter")
        with open("failed_prompts.txt", "a") as log:
            log.write(f"ID {event_id} | {event_title} | {e}\n")
        return False

    except Exception as e:
        print(f"         -> ERROR: {e}")
        return False


def main():
    setup_environment()
    print(f"Project: {PROJECT_ID}")
    print(f"Model:   {MODEL_NAME}")
    print(f"Ratio:   {ASPECT_RATIO}\n")

    try:
        model = ImageGenerationModel.from_pretrained(MODEL_NAME)
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: '{JSON_FILE}' not found.")
        return

    generated = 0
    skipped = 0
    failed = 0

    for level in data["levels"]:
        print(f"\n{'='*50}")
        print(f"  {level['name']}")
        print(f"{'='*50}")

        for event in level["events"]:
            prompt = build_prompt(event)

            ok = generate_image(model, prompt, event["id"], event["title"])
            if ok:
                generated += 1
            else:
                failed += 1

            time.sleep(DELAY_BETWEEN)

    print(f"\nDone! Generated: {generated}  Failed: {failed}")


if __name__ == "__main__":
    main()
