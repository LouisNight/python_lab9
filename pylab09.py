import os
import json
import random
import re
import sys

HOW_MANY_BOOK = 3
LINE = 128
PAGE = 64
pages = {}
page_number = 0
line_window = {}
line_number = 0
char_window = []

def clean_line(line):
    return line.strip().replace('-', '') + ' '  # Adding a space instead of a newline.

def process_char(char):
    global char_window
    char_window.append(char)
    if len(char_window) == LINE:
        add_line()

def add_line():
    global char_window, line_number
    line_number += 1
    process_page(''.join(char_window), line_number)
    char_window.clear()

def process_page(line, line_num):
    global line_window, pages, page_number
    line_window[line_num] = line
    if len(line_window) == PAGE:
        add_page()

def add_page():
    global line_number, line_window, pages, page_number
    page_number += 1
    pages[page_number] = dict(line_window)
    line_window.clear()
    line_number = 0

def process_books_with_rotation(*paths):
    global char_window
    book_files = [open(path, 'r', encoding='utf-8-sig') for path in paths]
    current_book = 0

    while book_files:
        try:
            line = book_files[current_book].readline()
            if not line:
                book_files[current_book].close()
                book_files.pop(current_book)
                if not book_files:
                    break
            else:
                line = clean_line(line)
                if line.strip():
                    for c in line:
                        process_char(c)
        except IndexError:
            break
        current_book = (current_book + 1) % len(book_files)

    if len(char_window) > 0:
        add_line()
    if len(line_window) > 0:
        add_page()

def interweave_pages():
    global pages
    interwoven_pages = {}
    current_page = 1

    all_lines = []
    for page_lines in pages.values():
        all_lines.extend(page_lines.values())

    random.shuffle(all_lines)

    for i, line in enumerate(all_lines):
        line_window[i % PAGE] = line
        if len(line_window) == PAGE:
            interwoven_pages[current_page] = dict(line_window)
            line_window.clear()
            current_page += 1

    pages.clear()
    pages.update(interwoven_pages)

def generate_code_book():
    global pages
    code_book = {}
    for page, lines in pages.items():
        for num, line in lines.items():
            for pos, char in enumerate(line):
                code_book.setdefault(char, []).append(f'{page}-{num}-{pos}')
    return code_book

def save(file_path, book):
    with open(file_path, 'w') as fp:
        json.dump(book, fp)

def load(file_path, *key_books, reverse=False):
    if os.path.exists(file_path):
        with open(file_path, 'r') as fp:
            return json.load(fp)
    else:
        process_books_with_rotation(*key_books)
        interweave_pages()
        if reverse:
            save(file_path, pages)
            return pages
        else:
            code_book = generate_code_book()
            save(file_path, code_book)
            return code_book

def encrypt(code_book, message):
    cipher_text = []
    for char in message:
        if char not in code_book or not code_book[char]:
            raise ValueError(f"Character '{char}' cannot be encrypted.")
        index = random.randint(0, len(code_book[char]) - 1)
        cipher_text.append(code_book[char].pop(index))
    return '-'.join(cipher_text)

def decrypt(rev_code_book, ciphertext):
    plaintext = []
    for cc in re.findall(r'\d+-\d+-\d+', ciphertext):
        page, line, char = cc.split('-')
        plaintext.append(rev_code_book[page][line][int(char)])
    return ''.join(plaintext)

def main_menu():
    print("""1). Encrypt
2). Decrypt
3). Quit
""")
    return int(input("Make a selection [1,2,3]: "))

def main():
    key_books = ('books/War_and_Peace.txt', 'books/Moby_Dick.txt', 'books/Dracula.txt')
    code_book_path = 'code_books/dmdwp.txt'
    rev_code_book_path = 'code_books/dmdwp_r.txt'
    while True:
        try:
            choice = main_menu()
            match choice:
                case 1:
                    code_book = load(code_book_path, *key_books)
                    message = input("Please enter your secret message: ")
                    print(encrypt(code_book, message))
                case 2:
                    rev_code_book = load(rev_code_book_path, *key_books, reverse=True)
                    message = input("Please enter your cipher text: ")
                    print(decrypt(rev_code_book, message))
                case 3:
                    sys.exit(0)
        except ValueError as ve:
            print("Improper selection or character issue:", ve)

if __name__ == '__main__':
    main()
