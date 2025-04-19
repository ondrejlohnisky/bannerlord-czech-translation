import os
import re
import argparse

def process_file(path, pattern):
    """
    Reads a file, replaces the last occurrence of '{?}' with '{\\?}' on lines
    matching the provided pattern, and writes back if any changes were made.
    Returns True if the file was modified.
    """
    changed = False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (UnicodeDecodeError, PermissionError):
        # Skip binary or unreadable files
        return False

    new_lines = []
    for line in lines:
        if pattern.search(line):
            # Split at last '{?}', replace it with '{\?}'
            parts = line.rsplit('{?}', 1)
            if len(parts) == 2:
                new_line = parts[0] + '{\\?}' + parts[1]
                new_lines.append(new_line)
                changed = True
                continue
        new_lines.append(line)

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return changed

def main():
    parser = argparse.ArgumentParser(description='Fix incorrect closing gender tags in text files.')
    parser.add_argument('root', nargs='?', default='.', help='Root directory to scan (default: current)')
    args, _ = parser.parse_known_args()

    # Pattern to find lines with two '{?}' tags where the last is incorrect
    pattern = re.compile(r'\{\?[^}]+\}[^{}]*\{\?\}[^{}]*\{\?\}')

    for dirpath, _, filenames in os.walk(args.root):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if process_file(filepath, pattern):
                print(f'Updated: {filepath}')

if __name__ == '__main__':
    main()