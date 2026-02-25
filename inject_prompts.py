import json

# 1. Update this line to look in the src folder
with open('src/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

PROMPT_TEMPLATE = (
    "Can you generate an image for \"{title}\" in the following style: "
    "Ink Wash & Sumi-e (True Wabi-Sabi). For a more poetic feel, use "
    "abstract ink-bleed or wash illustrations."
)

for level in data['levels']:
    for event in level['events']:
        event['image_prompt'] = PROMPT_TEMPLATE.format(title=event['title'])

# 2. Update this line to save it back into the src folder
with open('src/data_with_prompts.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print("Done! Check your 'src' folder for 'data_with_prompts.json'.")