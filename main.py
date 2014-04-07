'''
    This is the main file. All it does is read the the user's choice and then tell the notebook class to do whatever the user asked for. 
'''

import argparse as argy
from contextlib import contextmanager
import pickle

import lib.notebook

def get_args():
    description = ("Take specific notes or a whole file, and insert it into the database")
    parser = argy.ArgumentParser (description=description)
    parser.add_argument('-n', '--note', help='A new note')
    parser.add_argument('-d', '--delete', help='Delete note by id', type=int)
    parser.add_argument('-t', '--note_text', help='A new note')
    parser.add_argument('-m', '--make_all_text', help='Make the notes file with all notes in it', action='store_true')
    parser.add_argument('-s', '--study_one', action='store_true', help='Gives a note for review and marks it')
    parser.add_argument('-r','--remove', help='Remove a note or section')

    args = parser.parse_args()
    return args

@contextmanager
def _open_notebook_to_write ():
    '''
        This will load the notebook from the database, and if there's no db it'll make a notebook. 
    '''
    notebook = None
    try:
        with open('notebook.json', 'r+') as f:
            notebook = pickle.load(f)
    except: 
        notebook = lib.notebook.Notebook()

    yield notebook
    with open('notebook.json', 'w+') as f:
        pickle.dump(notebook, f)
def _get_file_text(filename):
    try:
        with open(filename) as f:
            return f.readlines()
    except:
        return []
def do_args(args):
    with _open_notebook_to_write() as notebook:
        if args.note:
            notebook.add_note(_get_file_text(args.note))
        if args.note_text:
            notebook.add_note(args.note_text)
        if args.study_one:
            print notebook.get_next_review_note()
        if args.delete:
            notebook.delete_note(args.delete)
        if args.make_all_text:
            y = notebook.build_all_notes_text()
            for x in notebook.build_all_notes_text():
                print x

def _bad_formatting_error():
    print "BAD FORMATTING ON NOTE"
    raise NameError
def _bad_key_error():
    print "BAD PARENT ID"
    raise NameError
def _check_note(note, notebook):
    text = _get_file_text(note)
    _check_note_text(text, notebook)
def _check_note_formatting(text):
    found_section_parents = False
    found_note_section = False
    found_note_text = False
    for text_line in text:
        if 'parent sections:' in text_line:
            found_section_parents = True
        if found_note_section and text_line != '\n':
            found_note_text = True
        if 'note:' in text_line:
            found_note_section = True
    if not all([found_section_parents, found_note_section, found_note_text]):
        _bad_formatting_error()
def _check_valid_parents(parents, db):
    for parent in parents.iterkeys():
        if not parent in db.keys():
            _bad_key_error()
def _check_valid_raw_parents(text, notebook):
    db = notebook.note_table
    parents = notebook._get_note_parents(text)
    _check_valid_parents(parents, db)
def _check_note_text(text, notebook):
    _check_note_formatting(text)
    _check_valid_raw_parents(text, notebook)
def check_args(args):
    with _open_notebook_to_write() as notebook:
        if args.note:
            _check_note(args.note, notebook)
        if args.note_text:
            _check_note_text(args.note_text, notebook)
        if args.delete:
            _check_valid_parents({args.delete:0}, notebook.note_table)

def main():
    args = get_args()
    check_args(args)
    do_args(args)

if __name__=='__main__':
    main()
