# this is a notebook file that deals with notebooks (clusters of notes)
from multiprocessing.connection import Listener
from contextlib import contextmanager
from lib._id_manager import _IdManager
import lib.note
import re
import thread
import os
import pickle


@contextmanager
def open_notebook_to_write(note_book_root=[]):
    '''
        This will load the notebook from the database, and if there's no db it'll make a notebook.
    '''
    notebook = None
    pathname = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(pathname, 'notebook.json')
    try:
        with open(filename, 'r+') as f:
            notebook = pickle.load(f)
    except:
        notebook = lib.notebook.Notebook()

    yield notebook
    with open(filename, 'w+') as f:
        pickle.dump(notebook, f)


class Notebook():
    '''
        This is a notebook, it holds notes and operates on them.
    '''
    def __init__(self):
        '''
            top_note = the base note, the blank document itself
            note_table = a table of all the notes for quick updates
                {nodeid: note object}
        '''
        self.id_manager = _IdManager()
        top_note_id = self.id_manager.get_id()
        self.top_level_note = lib.note.Note(top_note_id)
        self.note_table = {top_note_id: self.top_level_note}

    @staticmethod
    def _get_note_text(raw_note_text):
        # the readable part of the note
        note_text = ''
        for cur, line in enumerate(raw_note_text):
            if "note:" in line[:5]:
                note_text = raw_note_text[cur+1:]
                break
        note_text = [t.strip() for t in note_text]
        return note_text

    @staticmethod
    def _clean_parents(raw_parents_text):
        parents = []
        parents += [int(parent.strip()) for parent in raw_parents_text.split(',') if parent.strip()]
        return parents

    @staticmethod
    def _find_parents(raw_note_text):
        for cur, line in enumerate(raw_note_text):
            if "parent sections:" in line[:16]:
                return raw_note_text[cur+1]

    def _get_note_parents(self, raw_note_text):
        raw_parent_text = self._find_parents(raw_note_text)
        clean_parent_ids = self._clean_parents(raw_parent_text)
        parents_dict = dict((key, self.note_table[key]) for key in clean_parent_ids)
        return parents_dict

    def _make_note(self, raw_note_text):
        text = self._get_note_text(raw_note_text)
        parents = self._get_note_parents(raw_note_text)
        return lib.note.Note(text, self.id_manager.get_id(), parents)

    def _add_note_to_parents(self, note):
        for parent in note.parent_notes.iterkeys():
            self.note_table[parent].add_child(note)
        if not note.parent_notes:
            self.top_level_note.add_child(note)

    def _add_note_to_self(self, note):
        self._add_note_to_parents(note)
        self.note_table[note.db_id] = note

    def add_note(self, raw_note_text):
        # The raw_text is going to contain a line with the comma separated list of parent ids, and then its own id. Then the text below
        note = self._make_note(raw_note_text)
        self._add_note_to_self(note)

    def _remove_refs_from_children(self, note):
        for child in note.child_notes.itervalues():
            child.parent_notes.pop(note.db_id)

    @staticmethod
    def _remove_refs_from_parents(note):
        if note.parent_notes:
            for parent in note.parent_notes.itervalues():
                parent.child_notes.pop(note.db_id)

    def _remove_note_from_table(self, note_id):
        self.note_table.pop(note_id)
        self.id_manager.remove_id(note_id)

    def _remove_refs(self, note):
        self._remove_refs_from_parents(note)
        self._remove_refs_from_children(note)

    def _delete_dangling_children(self, note):
        for child in note.child_notes:
            if not child.parent_notes:
                self.delete_note(child.db_id)

    def delete_note(self, note_id):
        note = self.note_table[note_id]

        self._remove_refs(note)
        self._delete_dangling_children(note)
        self._remove_note_from_table(note_id)

    @staticmethod
    def _clean_id(raw_id_text):
        if raw_id_text:
            return int(raw_id_text.strip())
        else:
            return None

    @staticmethod
    def _find_id_raw(raw_note_text):
        for cur, line in enumerate(raw_note_text):
            if re.match(r'^id:\s*$', line):
                id_line = raw_note_text[cur+1]
                return id_line
        return None

    def _get_note_id(self, raw_note_text):
        raw_id_text = self._find_id_raw(raw_note_text)
        clean_note_id = self._clean_id(raw_id_text)
        return clean_note_id

    def update_note(self, raw_note_text):
        note_id = self._get_note_id(raw_note_text)
        self._remove_refs_from_parents(self.note_table[note_id])
        self._remove_note_from_table(note_id)
        updated_note = self._make_note(raw_note_text)
        updated_note.db_id = note_id
        self._add_note_to_self(updated_note)

    def _make_existing_note(self, raw_note):
        text = self._get_note_text(raw_note)
        note_id = self._get_note_id(raw_note)
        parents = self._get_note_parents(raw_note)
        return lib.note.Note(text, note_id, parents)

    def _split_notes_by_breaks(self, raw_notebook):
        # returns a list of possible notes
        notes_list = []
        note_lines = []
        for line in raw_notebook:
            if not line.strip():
                notes_list.append(self._make_existing_note(note_lines))
                note_lines = []
            else:
                note_lines.append(line)
        if note_lines:
            notes_list.append(self._make_existing_note(note_lines))
        return notes_list

    def _delete_or_make_id(self, note):
        if note.db_id in self.note_table.iterkeys():
            note.copy_meta(self.note_table[note.db_id])
            self._remove_refs_from_parents(note)
            db_id = note.db_id
        else:
            db_id = self.id_manager.get_id()
        return db_id

    def _update_and_add_note(self, note):
        note.db_id = self._delete_or_make_id(note)
        self._add_note_to_self(note)
        return [note.db_id]

    def _remove_unfound_notes(self, updated_note_ids):
        old_notes = list(self.note_table.iterkeys())
        for target in old_notes:
            if target not in updated_note_ids:
                self.delete_note(target)

    def _see_if_note_is_changed_db_note(self, note):
        if note.db_id in self.note_table.iterkeys():
            orig_note = self.note_table(note.db_id)
            is_identical = note.compare(orig_note)
            return is_identical
        else:
            return False

    def _update_all_db_notes(self, updated_notes):
        found_note_ids = [0]
        altered_note_ids = [0]
        for note in updated_notes:
            if self._see_if_note_is_changed_db_note(note):
                if note.db_id not in altered_note_ids:
                    note_id = self._update_and_add_note(note)
                    found_note_ids += note_id
                    altered_note_ids += note_id
            elif note.db_id not in found_note_ids:
                if not note.db_id:
                    note_id = self._update_and_add_note(note)
                found_note_ids += note_id
        return found_note_ids

    def update_all_from_raw(self, raw_notebook):
        new_notes_to_add = self._split_notes_by_breaks(raw_notebook)
        found_note_ids = self._update_all_db_notes(new_notes_to_add)
        self._remove_unfound_notes(found_note_ids)

    def build_all_notes_text(self):
        text = self.top_level_note.make_all_text_minus_one_indent()
        return text

    def _get_next_review_note(self):
        note = self.top_level_note.get_note_to_study()
        if not note:
            self._reset_all_note_meta()
            note = self.top_level_note.get_note_to_study()
        return note.note if note else None

    def get_next_review_note(self):
        for key, note in self.note_table.iteritems():
            print note.note

    def _start_listener(self, listener):
        conn = listener.accept()
        print 'connection accepted from', listener.last_accepted
        while True:
            msg = conn.recv()
            # do something with msg
            if msg.name == 'update_all_from_raw':
                self.update_all_from_raw(msg.data)
            if msg.name == 'build_all_notes_text':
                print self.build_all_notes_text()
            if msg.name == 'close':
                conn.close()
                break
        listener.close()

    def start_server(self):
        listener = Listener()
        thread.start_new_thread(self._start_listener, listener)
        return listener.address
