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

