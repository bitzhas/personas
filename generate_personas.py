import openai
from openai import OpenAI  # For newer API versions
import json
import time
import os

# Initialize client - for newer API versions
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Better to use environment variables

def generate_company_persona(retry_attempts=3):
    prompt = """
    Generate a fictional company persona for a legal dispute simulation. Include the following fields:
    
    - company_name
    - jurisdiction
    - industry
    - core_activities
    - legal_issues
    - key_persons (list with name, role, background)
    - dispute_style
    - financial_status
    - goals
    - communication_style
    - dispute_context (type, opposing_party, facts, preferred_resolution)
    
    Return the result as valid JSON only, without any additional text or explanation.
    """
    
    for attempt in range(retry_attempts):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={ "type": "json_object" }  # Ensures JSON output
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Attempt {attempt+1}: JSON parse failed, trying to extract JSON...")
            # Try to extract JSON from malformed response
            try:
                json_str = content[content.find('{'):content.rfind('}')+1]
                return json.loads(json_str)
            except:
                continue
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {str(e)}")
            time.sleep(2 * (attempt + 1))  # Exponential backoff
    return None

# Generate personas with better pacing
dataset = []
for i in range(25):
    print(f"Generating persona {i+1}...")
    persona = generate_company_persona()
    if persona:
        dataset.append(persona)
        time.sleep(3)  # Add delay between requests
    else:
        print(f"Failed to generate persona {i+1} after multiple attempts.")

# Save to file
with open("legal_company_personas.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"✅ Done: Generated {len(dataset)} personas. Saved to legal_company_personas.json")