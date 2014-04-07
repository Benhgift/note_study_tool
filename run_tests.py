'''
  This file will run all logical tests for typical usage. This is the best place to start when looking over the code. It will create each step in a top down way starting from the simplest case. 
'''

import lib.note
import main

# make a note 
parent_notes = [[1,2], [1,3]]
note_id = 4
note = lib.note.Note("note text", parent_notes, note_id)

# insert the note into the db (aka notebook)
with __open_notebook_to_write() as notebook:
    notebook.add_note(note)

    # review 1 note
    #print notebook.get_next_review_note()
