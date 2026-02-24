import json
import os
import time
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, InvalidArgument

# ================= CONFIGURATION =================
# Your Project ID
PROJECT_ID = "p1-history-images" 

# We are defaulting to us-central1 (Iowa). 
# If you get a "404 Not Found" error, try changing this to "us-east4" or "europe-west4".
LOCATION = "us-central1" 

# Using Imagen 3 for best quality and text rendering
MODEL_NAME = "imagen-3.0-fast-generate-001" 

# Set to 4:3 to match the box in your screenshot
ASPECT_RATIO = "4:3" 

# Folder where images will be saved
OUTPUT_DIR = "generated_images"

# Your data file
JSON_FILE = "src/data_with_prompts.json"
# =================================================

def setup_environment():
    """Initializes the Vertex AI SDK and creates output folder."""
    # Initialize the connection to Google Cloud
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # Create the folder if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

def generate_image(model, prompt, event_id, event_title):
    """Generates an image from a prompt and saves it."""
    
    # Create a clean filename: "1_The_Big_Bang.png"
    safe_title = event_title.replace(" ", "_").replace("/", "-").replace("'", "")
    filename = f"{event_id}_{safe_title}.png"
    file_path = os.path.join(OUTPUT_DIR, filename)

    # RESUME CHECK: If the file already exists, skip it.
    if os.path.exists(file_path):
        print(f"[SKIP] Event {event_id}: Image already exists.")
        return

    print(f"[GENERATING] Event {event_id}: {event_title}...")

    try:
        # Generate the image
        images = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="en",
            aspect_ratio=ASPECT_RATIO,
            # 'block_few' is crucial for historical content (War, Slavery, etc.)
            # to prevent the model from being overly sensitive.
            safety_filter_level="block_few", 
            person_generation="allow_adult" 
        )

        # Save the result
        if images:
            images[0].save(location=file_path, include_generation_parameters=True)
            print(f"   -> SUCCESS: Saved to {filename}")
        
    except (ResourceExhausted, ServiceUnavailable) as e:
        # If Google says "Too fast!", wait 60 seconds and try again.
        print(f"   -> RATE LIMIT HIT. Cooling down for 60 seconds...")
        time.sleep(60)
        generate_image(model, prompt, event_id, event_title)
        
    except InvalidArgument as e:
        # This usually happens if a prompt triggers a hard safety block
        print(f"   -> BLOCKED: The prompt for '{event_title}' triggered a safety filter.")
        with open("failed_prompts.txt", "a") as log:
            log.write(f"ID {event_id} ({event_title}): {e}\n")
            
    except Exception as e:
        print(f"   -> ERROR: {e}")

def main():
    setup_environment()
    
    print(f"Connecting to Google Cloud Project: {PROJECT_ID}...")
    try:
        model = ImageGenerationModel.from_pretrained(MODEL_NAME)
    except Exception as e:
        print(f"Error loading model. Are you authenticated? Run 'gcloud auth application-default login' in terminal.")
        print(f"Details: {e}")
        return

    # Load the JSON
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Could not find '{JSON_FILE}'. Make sure the JSON file is in this folder.")
        return

    # Loop through all levels and events
    total_count = 0
    for level in data['levels']:
        print(f"\n--- Processing Level: {level['name']} ---")
        
        for event in level['events']:
            # Extract data
            event_id = event['id']
            title = event['title']
            # Using your prompt exactly as requested
            raw_prompt = event['image_prompt']

            # Run generation
            generate_image(model, raw_prompt, event_id, title)
            
            total_count += 1
            
            # SMALL DELAY: Prevents hitting the "Requests Per Minute" quota
            time.sleep(10)

    print(f"\nDone! Processed {total_count} requests.")

if __name__ == "__main__":
    main()