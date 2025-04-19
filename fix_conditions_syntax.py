#!/usr/bin/env python3
"""
fix_gender_syntax.py

Recursively scans all files in the given directory (and subdirectories),
finds all occurrences of the pattern `{?anything}anything{?}anything{\?}`,
and fixes them by adding a backslash before the last `{?}` (i.e., `{\?}`).
"""

import os
import re
import argparse

def process_file(path, pattern):
    """
    Reads a file, replaces all occurrences of '{?}' with '{\\?}' on lines
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
        new_line = line
        while True:
            # Find the last occurrence of the pattern on the line
            match = re.search(pattern, new_line)
            if not match:
                break
            # Fix the last '{?}' in the match
            start, end = match.span()
            parts = new_line[start:end].rsplit('{?}', 1)  # Split on the last `{?}`
            if len(parts) == 2:
                fixed_line = parts[0] + '{\\?}' + parts[1]
                new_line = new_line[:start] + fixed_line + new_line[end:]
                changed = True

        new_lines.append(new_line)

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return changed

def main():
    parser = argparse.ArgumentParser(description='Fix incorrect closing gender tags in text files.')
    parser.add_argument('root', nargs='?', default='.', help='Root directory to scan (default: current)')
    args = parser.parse_args()

    # Pattern to find all occurrences of the pattern with any "anything"
    pattern = re.compile(r'\{\?[^}]+\}[^{}]*\{\?\}[^{}]*\{\?\}')

    for dirpath, _, filenames in os.walk(args.root):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if process_file(filepath, pattern):
                print(f'Updated: {filepath}')

if __name__ == '__main__':
    main()
