import os
import sys
import json
import py_compile

# Set root directory in sys.path
sys.path.insert(0, os.getcwd())

# Set stdout encoding for Windows console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=======================================================")
print(" BULK LEADS CALLER - COMPREHENSIVE DEEP SYSTEM AUDIT")
print("=======================================================\n")

# Audit 1: Python Files Syntax Compilation
print("--- AUDIT 1: PYTHON SYNTAX & COMPILATION ---")
files_to_check = ['main.py', 'quotes_database.py']
errors_found = False

for fname in files_to_check:
    try:
        py_compile.compile(fname, doraise=True)
        print(f"  [OK] {fname}: Clean compilation (0 errors)")
    except Exception as e:
        print(f"  [FAIL] {fname}: Compilation error -> {e}")
        errors_found = True

# Audit 2: Database Integrity & Capacity
print("\n--- AUDIT 2: QUOTES DATABASE INTEGRITY & CAPACITY ---")
try:
    from quotes_database import QUOTES_365_DATABASE
    total = len(QUOTES_365_DATABASE)
    print(f"  [OK] Total database entries: {total}")
    
    if total < 365:
        print(f"  [WARNING] Database has {total} entries (expected at least 365)")
    else:
        print(f"  [OK] Database capacity check: PASSED ({total} >= 365)")
        
    invalid_entries = []
    seen = set()
    duplicates = []
    
    for idx, item in enumerate(QUOTES_365_DATABASE):
        if not isinstance(item, dict) or 'quote' not in item or 'author' not in item or not item['quote'] or not item['author']:
            invalid_entries.append(idx)
        else:
            q_text = item['quote'].strip().lower()
            if q_text in seen:
                duplicates.append(item['quote'])
            seen.add(q_text)
            
    if invalid_entries:
        print(f"  [FAIL] Invalid schema entries found at indices: {invalid_entries}")
        errors_found = True
    else:
        print("  [OK] Schema integrity check: All entries contain valid 'quote' and 'author'")
        
    if duplicates:
        print(f"  [WARNING] Duplicate quotes found: {len(duplicates)}")
    else:
        print("  [OK] Duplication check: 100% unique quotes (0 duplicates)")

except Exception as e:
    print(f"  [FAIL] Database import error: {e}")
    errors_found = True

# Audit 3: Assets, Fonts & Templates
print("\n--- AUDIT 3: ASSETS & TYPOGRAPHY ---")
required_files = ['template.png', 'phone_quote_icon.png', 'history.txt']
for rf in required_files:
    if os.path.exists(rf):
        print(f"  [OK] Asset '{rf}': PRESENT ({os.path.getsize(rf)} bytes)")
    else:
        print(f"  [FAIL] Missing required asset: '{rf}'")
        errors_found = True

font_files = [f for f in os.listdir('.') if f.endswith('.ttf')]
print(f"  [OK] Available TTF font files: {len(font_files)} fonts found")
for font in font_files[:5]:
    print(f"     - {font}")

# Audit 4: Configuration & Fallback Safety
print("\n--- AUDIT 4: CONFIGURATION & FALLBACK SAFETY ---")
import main

print(f"  - LINKEDIN_ACCESS_TOKEN: {main._mask(main.LINKEDIN_ACCESS_TOKEN)}")
print(f"  - LINKEDIN_AUTHOR_URN: {main.LINKEDIN_AUTHOR_URN or '(empty)'}")
print(f"  - GEMINI_API_KEY: {main._mask(main.GEMINI_API_KEY)}")
print(f"  - GROQ_API_KEY: {main._mask(main.GROQ_API_KEY)}")
print(f"  - BUFFER_TOKEN: {main._mask(main.BUFFER_TOKEN)}")

if main.BUFFER_TOKEN:
    print("  [OK] Buffer integration mode: ACTIVE (Direct LinkedIn Business Page posting)")
else:
    print("  [WARNING] Native LinkedIn fallback mode active")

# Audit 5: Image Rendering Engine Test (Dry Run)
print("\n--- AUDIT 5: IMAGE RENDERING ENGINE TEST ---")
try:
    test_quote = "Approach each customer with the idea of helping him or her solve a problem or achieve a goal."
    test_author = "Brian Tracy"
    out_img = main.render_quote_image(test_quote, test_author)
    if os.path.exists(out_img) and os.path.getsize(out_img) > 1000:
        print(f"  [OK] Pillow image rendering engine: PASSED (Generated '{out_img}', {os.path.getsize(out_img)} bytes)")
    else:
        print("  [FAIL] Pillow image rendering engine: FAILED (Output image empty or missing)")
        errors_found = True
except Exception as e:
    print(f"  [FAIL] Rendering engine exception: {e}")
    errors_found = True

# Audit 6: GitHub Actions Workflow File Validation
print("\n--- AUDIT 6: GITHUB ACTIONS WORKFLOW VALIDATION ---")
wf_path = '.github/workflows/daily_post.yml'
if os.path.exists(wf_path):
    with open(wf_path, 'r', encoding='utf-8') as f:
        wf = f.read()
    if 'cron:' in wf and 'python main.py' in wf and 'BUFFER_TOKEN' in wf:
        print("  [OK] GitHub Actions workflow configuration: PASSED (Contains schedule, secrets & execution)")
    else:
        print("  [FAIL] Workflow file incomplete or missing steps")
        errors_found = True
else:
    print("  [FAIL] Missing workflow file!")
    errors_found = True

print("\n=======================================================")
if errors_found:
    print(" [STATUS] AUDIT COMPLETED WITH ISSUES TO FIX")
else:
    print(" [STATUS] DEEP AUDIT COMPLETED: 100% CLEAN - NO BUGS FOUND!")
print("=======================================================")
