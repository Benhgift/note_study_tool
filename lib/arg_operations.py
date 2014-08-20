# this is the file dealing with all the arguments
from lib import argparse as argy
from lib.notebook import Notebook
from lib.notebook import open_notebook_to_write

def get_args():
    description = ("Take specific notes or a whole file, and insert it into the database")
    parser = argy.ArgumentParser (description=description)
    parser.add_argument('-n', '--note', help='A new note')
    parser.add_argument('-d', '--delete', help='Delete note by id', type=int)
    parser.add_argument('-r', '--replace_all', help='Replace notebook with new raw notebook file')
    parser.add_argument('-t', '--note_text', help='A new note')
    parser.add_argument('-m', '--make_all_text', help='Make the notes file with all notes in it', action='store_true')
    parser.add_argument('-s', '--study_one', action='store_true', help='Gives a note for review and marks it')
    parser.add_argument('-S', '--server', nargs=2, help='Starts this as a server, pass in port and notes filename after that')
    parser.add_argument('-u','--update', help='Pass in the note to update')

    args = parser.parse_args()
    return args

def _get_file_text(filename):
    try:
        with open(filename) as f:
            return f.readlines()
    except:
        return []

def do_args(args):
    with open_notebook_to_write() as notebook:
        if args.note:
            notebook.add_note(_get_file_text(args.note))
        if args.note_text:
            notebook.add_note(args.note_text)
        if args.study_one:
            print notebook.get_next_review_note()
        if args.delete:
            notebook.delete_note(args.delete)
        if args.update:
            notebook.update_note(_get_file_text(args.update))
        if args.make_all_text:
            y = notebook.build_all_notes_text()
            for x in notebook.build_all_notes_text():
                print x
        if args.server:
            print notebook.start_server(args.server[0], args.server[1])
        if args.replace_all:
            raw = _get_file_text(args.replace_all)
            notebook.update_all_from_raw(raw)

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
    with open_notebook_to_write() as notebook:
        if args.note:
            _check_note(args.note, notebook)
        if args.note_text:
            _check_note_text(args.note_text, notebook)
        if args.delete:
            _check_valid_parents({args.delete:0}, notebook.note_table)
        if args.update:
            _check_note(args.update, notebook)

