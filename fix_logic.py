#!/usr/bin/env python3
"""
Script to fix the astro_service.py logic flow by removing the early return bypass.
"""

# Read the original file
with open('src/services/astro_service.py', 'r') as f:
    lines = f.readlines()

# Find and remove the problematic section (lines 246-326 that cause early return)
# We'll replace it with logic that integrates AstrologyAPI.com as enrichment

# Lines to remove: 246-326 (the early return logic)
# Lines to keep: everything else

new_lines = []
skip_mode = False
line_num = 0

for i, line in enumerate(lines, 1):
    # Start skipping at line 246 (the problematic section start)
    if i == 246:
        # Insert the fixed logic instead
        new_lines.append("\n")
        new_lines.append("    # 4. Detect Question Type & Extract Birth Details\n")
        new_lines.append("    question_lower = question.lower()\n")
        new_lines.append("    needs_remedy = any(k in question_lower for k in REMEDY_KEYWORDS)\n")
        new_lines.append("    \n")
        new_lines.append("    astrology_keywords = [\n")
        new_lines.append("        \"kundali\", \"birth chart\", \"janam kundali\", \"natal chart\", \"remedy\", \"astrology\", \n")
        new_lines.append("        \"planet\", \"dasha\", \"lagna\", \"horoscope\", \"zodiac\", \"graha\", \"nakshatra\", \"rashi\", \n")
        new_lines.append("        \"upay\", \"totka\", \"totke\"\n")
        new_lines.append("    ]\n")
        new_lines.append("    is_astrology_question = any(k in question.lower() for k in astrology_keywords)\n")
        new_lines.append("\n")
        new_lines.append("    logging.info(f\"Processing Question: '{question[:50]}...' | Astrology: {is_astrology_question} | Needs Remedy: {needs_remedy}\")\n")
        new_lines.append("\n")
        new_lines.append("    # Extract birth details from context if available\n")
        new_lines.append("    birth_details = {}\n")
        new_lines.append("    if context and isinstance(context, dict):\n")
        new_lines.append("        birth_fields = [\"birthDate\", \"birthTime\", \"birthPlace\", \"birthLatitude\", \"birthLongitude\"]\n")
        new_lines.append("        for field in birth_fields:\n")
        new_lines.append("            if field in context:\n")
        new_lines.append("                birth_details[field] = context[field]\n")
        new_lines.append("\n")
        new_lines.append("    # 5. Get AstrologyAPI.com Response (if astrology question) as enrichment\n")
        new_lines.append("    api_enrichment = \"\"\n")
        new_lines.append("    if is_astrology_question:\n")
        new_lines.append("        try:\n")
        new_lines.append("            api_response = await get_astrologyapi_remedy(question, birth_details)\n")
        new_lines.append("            api_enrichment = f\"\\n\\nAstrologyAPI.com Data:\\n{api_response}\"\n")
        new_lines.append("            logging.info(\"Successfully retrieved AstrologyAPI.com data\")\n")
        new_lines.append("        except Exception as e:\n")
        new_lines.append("            logging.warning(f\"AstrologyAPI.com call failed, continuing with ChromaDB only: {e}\")\n")
        new_lines.append("            api_enrichment = \"\"\n")
        new_lines.append("\n")
        new_lines.append("    # 6. Build Enhanced Retrieved Block (ChromaDB + AstrologyAPI.com)\n")
        new_lines.append("    enhanced_retrieved_block = retrieved_text\n")
        new_lines.append("    if api_enrichment:\n")
        new_lines.append("        enhanced_retrieved_block = f\"{retrieved_text}\\n{api_enrichment}\" if retrieved_text else api_enrichment\n")
        new_lines.append("    \n")
        new_lines.append("    if not enhanced_retrieved_block:\n")
        new_lines.append("        enhanced_retrieved_block = \"No specific knowledge retrieved. Use your expertise.\"\n")
        new_lines.append("\n")
        skip_mode = True
        continue
    
    # Stop skipping at line 328 (where the original comprehensive logic starts)
    if i == 328:
        skip_mode = False
        # Modify this line to use enhanced_retrieved_block
        new_lines.append("    # 7. Generate Response using Comprehensive Prompt\n")
        continue
    
    # Skip lines in the problematic section
    if skip_mode:
        continue
    
    # For line 332, update to use enhanced_retrieved_block
    if i == 332 and "retrieved_block=" in line:
        new_lines.append("        retrieved_block=f\"Retrieved Astrological Knowledge:\\n{enhanced_retrieved_block}\",\n")
        continue
    
    # Keep all other lines
    new_lines.append(line)

# Add persona validation for remedy field (after line 392)
final_lines = []
for i, line in enumerate(new_lines):
    final_lines.append(line)
    # After the line that validates answer, add remedy validation
    if 'data["answer"] = validate_and_fix_persona(data["answer"])' in line:
        final_lines.append('    data["remedy"] = validate_and_fix_persona(data["remedy"])\n')

# Write the fixed file
with open('src/services/astro_service.py', 'w') as f:
    f.writelines(final_lines)

print("✅ Fixed astro_service.py successfully!")
print("Changes made:")
print("1. Removed early return bypass (lines 246-326)")
print("2. Integrated AstrologyAPI.com as enrichment source")
print("3. Updated prompt to use enhanced_retrieved_block")
print("4. Added persona validation for remedy field")
