# This file will run all logical tests for typical usage. This is the best place to start when looking over the code. It will create each step in a top down way starting from the simplest case. 
import lib.note
from lib.arg_operations import open_notebook_to_write
import lib.notebook

print "adding notes and printing"
note1 = ['parent sections:\n','0\n','note:\n','Biology']
note2 = ['parent sections:\n','0\n','note:\n','Math']
notebook = lib.notebook.Notebook()
notebook.add_note(note1)
notebook.add_note(note2)
for x in notebook.build_all_notes_text(): print x

print "replacing db with new notes from file"
all_notes = ['parent sections:\n','0\n','note:\n','Biologyy', '\n', 'parent sections:\n','0\n','note:\n','Mathy']
with open_notebook_to_write() as notebook:
    notebook.update_all_from_raw(all_notes)
    for x in notebook.build_all_notes_text(): print x
