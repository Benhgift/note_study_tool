#Quickstart:
Make a note file that looks like the example. There's an "id" section, a "parents" section and the "note" section. The id is the database id of the note. Omit this section when adding a note, since the id isn't known. The parents are the ids of all the notes that want this note as a sub note. And the "note" section is the text.

Then call `python main.py -n your_notefile.note`, and then `python main.py -m` to view all notes in the database.

#Description:
This program is the backend for note management. You can tag notes heirarchically and they'll stay under their parent notes.

Next is to support spaced repitition study.

Pass in notes and it'll store them. Then you can:
    - retrieve a note for study (not implimented)
    - build a notes file from all of them
    - add/remove/update

Which notes should we study?
    - the note with the highest importance.
        imporance = time_since_review * imporance_scale 
            importance_scale changes with user saying note was easy

    - parent notes first
        - when we study a note, reset its age to 0
            - increase importance of child notes
