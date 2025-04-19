import os
import re
from langdetect import detect

pattern = re.compile(
    r'<string[^>]*text="(?:[^{}čďěňřšťžáéíóúýůČĎĚŇŘŠŤŽÁÉÍÓÚÝŮ]*\{[^}]*\})*[^{}čďěňřšťžáéíóúýůČĎĚŇŘŠŤŽÁÉÍÓÚÝŮ]*[a-zA-Z][^{}čďěňřšťžáéíóúýůČĎĚŇŘŠŤŽÁÉÍÓÚÝŮ]*"'
)

def strip_braces(text):
    return re.sub(r'\{[^}]*\}', '', text)

def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False

def is_name(text):
    """
    Checks if the text is likely a name.
    A name typically starts with a capital letter and contains no spaces or special characters.
    """
    return text.istitle() and text.isalpha()

def is_english_or_name(text):
    """
    Determines if the text is English or a name.
    Skips names if they are detected as such.
    """
    if is_name(text):
        return False  # Skip names
    return is_english(text)

def find_english_lines_in_dir(base_path):
    english_lines = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith('.xml') or file.endswith('.xlf'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    match = pattern.search(line)
                    if match:
                        text_attr = re.search(r'text="([^"]+)"', match.group())
                        if text_attr:
                            cleaned_text = strip_braces(text_attr.group(1))
                            if is_english_or_name(cleaned_text):  # Use the new function
                                english_lines.append({
                                    "file": file_path,
                                    "line_num": i,
                                    "original": line.strip(),
                                    "text": cleaned_text.strip()
                                })
    return english_lines

def update_lines(lines):
    for item in lines:
        print(f"\nFile: {item['file']}")
        print(f"Line {item['line_num'] + 1}: {item['original']}")
        new_text = input("Enter replacement text (or leave empty to skip): ")
        if new_text:
            # Replace only the content of text=""
            updated_line = re.sub(r'text="([^"]+)"', f'text="{new_text}"', item['original'])
            with open(item['file'], 'r', encoding='utf-8') as f:
                file_lines = f.readlines()
            file_lines[item['line_num']] = updated_line + "\n"
            with open(item['file'], 'w', encoding='utf-8') as f:
                f.writelines(file_lines)

def summarize_lines(lines):
    print("\nSummary of detected English lines:")
    file_counts = {}
    for item in lines:
        file = item['file']
        file_counts[file] = file_counts.get(file, 0) + 1
        print(f"File: {file}, Line {item['line_num'] + 1}: {item['text']}")
    
    print("\nSummary of counts per file:")
    for file, count in file_counts.items():
        print(f"{file}: {count} English lines found")
    
    print(f"\nTotal English lines found in the scan: {len(lines)}")

if __name__ == "__main__":
    directory = input("Enter directory to scan: ").strip()
    matches = find_english_lines_in_dir(directory)
    summarize_lines(matches)  # Print summary of found lines
    update_lines(matches)
