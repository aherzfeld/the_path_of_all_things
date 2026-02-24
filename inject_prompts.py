import json

# Load your original file
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# The template you know works
PROMPT_TEMPLATE = (
    "Can you generate an image for \"{title}\" in the following style: "
    "Ink Wash & Sumi-e (True Wabi-Sabi). For a more poetic feel, use "
    "abstract ink-bleed or wash illustrations."
)

# Update every event in every level
for level in data['levels']:
    for event in level['events']:
        # Adding the new key 'image_prompt'
        event['image_prompt'] = PROMPT_TEMPLATE.format(title=event['title'])

# Save the updated file
with open('data_with_prompts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Done! Your updated file is saved as 'data_with_prompts.json'.")
