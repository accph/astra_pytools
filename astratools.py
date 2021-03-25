from subprocess import run
from re import compile, sub
from os import listdir, unlink


def make_file(pattern_name, new_name, params):
    with open(f'{pattern_name}.in', 'r') as file:
        text = file.read()

    for key, value in params.items():
        patt = compile(_brackets(key)+r' *= *-?\'?[-\w\. ]*\'?')
        if isinstance(value, str):
            text = patt.sub(f"{key}='{value}'", text)
        elif isinstance(value, float):
            text = patt.sub(f'{key}={value:.7e}', text)
        elif isinstance(value, bool):
            text = patt.sub(f'{key}={"T" if value else "F"}', text)
        elif isinstance(value, int):
            text = patt.sub(f'{key}={value}', text)
        else:
            print('Wrong format of parameters!')
            return

    with open(f'{new_name}.in', 'w') as file:
        file.write(text)

def run_ASTRA(filename):
    run(['Astra', filename], input='', shell=True, capture_output=True)

def remove_files(s):
    for filename in listdir('.'):
        if s in filename:
            try:
                unlink(filename)
            except FileNotFoundError:
                return

def _brackets(s):
    p1, p2 = compile(r'\('), compile(r'\)')
    return p2.sub(r'\\)', p1.sub(r'\\(',s))
