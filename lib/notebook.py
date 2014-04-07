import re

import lib.note

class _IdManager():
    '''
        This distributes ids for the database

        It gives them out a unique one each time, 
        and if you delete one it reuses it later.
    '''
    def __init__(self):
        self.id_reusables = []
        self.id_next = 0
        self.id_used = []

    def get_id(self):
        id_target = 0
        if self.id_reusables:
            id_target = self.id_reusables.pop()
        else:
            id_target = self.id_next
            self.id_next += 1
            self.id_used.append(id_target)
        return id_target

    def remove_id(self, id_target):
        if id_target in self.id_used:
            self.id_used.remove(id_target)
            self.id_reusables.append(id_target)

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
        self.note_table = {top_note_id:self.top_level_note} 

    @staticmethod
    def _get_note_text(raw_note_text):
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
        '''
            The raw_text is going to contain a line with the comma separated list of parent ids, and then its own id. Then the text below
        '''
        note = self._make_note(raw_note_text)
        self._add_note_to_self(note)

    def _remove_refs_from_children(self, note):
        for child in note.child_notes:
            self._remove_refs_from_children(child)
    @staticmethod
    def _remove_refs_from_parents(note):
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

    def build_all_notes_text(self):
        text = self.top_level_note.make_all_text_minus_one_indent()
        return text

    @staticmethod
    def _clean_id(raw_id_text):
        id = int(raw_id_text.strip())
        return id
    @staticmethod
    def _find_id_raw(raw_note_text):
        for cur, line in enumerate(raw_note_text):
            if re.match(r'^id:\s*$', line):
                id_line = raw_note_text[cur+1]
                return id_line
    def _get_note_id(self, raw_note_text):
        raw_id_text = self._find_id_raw(raw_note_text)
        clean_note_id = self._clean_id(raw_id_text) 
        return clean_note_id
    def update_note(self, raw_note_text):
        note_id = self._get_note_id(raw_note_text)
        updated_note = self._make_note(raw_note_text)
        self.delete_note(note_id)
        self._add_note_to_self(updated_note)

    def _get_next_review_note(self):
        note = self.top_level_note.get_note_to_study()
        if not note:
            self._reset_all_note_meta()
            note = self.top_level_note.get_note_to_study()
        return note.note if note else None
    def get_next_review_note(self):
        for key, note in self.note_table.iteritems():
            print note.note
