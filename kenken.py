import itertools
import json
import operator

class Base(object):
    def __str__(self):
        return self.__repr__()

    def as_dict(self):
        return vars(dict)

class Cell(Base):
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.groups = set()
        self.number = None
        self.notes = set(range(1, state.n + 1))
        self.state = state

    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)

    def get_notes(self):
        return self.notes

    def remove_notes(self, notes_to_remove, retval):
        self.set_notes(self.notes - notes_to_remove, retval)

    def set_notes(self, notes_to_set, retval):
        if self.notes - notes_to_set:
            retval.append(self)
            self.notes = notes_to_set.copy()

        if len(self.notes) == 1:
            self.number = list(self.notes)[0]

    def as_dict(self):
        groups = filter(lambda g: type(g) is MathGroup and g.natural, self.groups)
        if groups:
            group, = groups
        else:
            group = None

        ret = vars(self)
        del ret['groups']
        del ret['state']
        ret['notes'] = list(ret['notes'])
        ret.update(group=str(hash(group)) if group else None)
        return ret

class Operation(Base):
    @classmethod
    def validate(cls, l):
        pass

    @classmethod
    def perform(cls, l):
        return reduce(cls.operator, l)
    @classmethod
    def reduce(cls, mgroup):
        return []

class GrowingOperation(Operation):
    @classmethod
    def reduce(cls, mgroup):
        retval = []
        result = mgroup.result
        cells = set(mgroup.cells) # no need to create new?
        for cell in cells:
            print ''
            print 'Looking at cell - %s' % cell
            print 'number: ', repr(cell.number)
            other_cells = cells - set([cell])
            print 'other notes: ', list(other_cell.notes for other_cell in other_cells)
            print 'op seed notes product: ', cls.op, cls.seed, list(itertools.product(*(other_cell.notes for other_cell in other_cells)))
            other_products = set(
                reduce(cls.op, sequence, cls.seed) for sequence in
                    itertools.product(*(other_cell.notes for other_cell in other_cells))
            )
            if not other_cells:
                other_products = set([cls.seed])

            cell.set_notes(set(filter(
                lambda num: cls.get_complement().op(result, num) in other_products and
                    cls.op(cls.get_complement().op(result, num), num) == result,
                cell.notes
            )), retval)

        return retval

class Add(GrowingOperation):
    op = operator.add
    seed = 0

    @staticmethod
    def get_complement():
        return Sub

class Mul(GrowingOperation):
    op = operator.mul
    seed = 1

    @staticmethod
    def get_complement():
        return Div

class InverseOperation(Operation):
    @classmethod
    def reduce(cls, mgroup):
        retval = []
        assert len(mgroup.cells) == 2
        result = mgroup.result

        cells = list(mgroup.cells)

        print 'Cells: ', cells
        print 'Notes: ', map(Cell.get_notes, cells)
        print 'Product: ', list(itertools.product(*map(Cell.get_notes, cells)))
        map(
            lambda (i, new_notes): cells[i].set_notes(new_notes, retval),
            enumerate(
                map(
                    set,
                    zip(
                        *filter(
                            lambda (x, y):
                                cls.get_complement().op(result, x) == y or
                                cls.get_complement().op(result, y) == x,
                            itertools.product(*map(Cell.get_notes, cells))
                        )
                    )
                )
            )
        )

        return retval


class Sub(InverseOperation):
    @classmethod
    def validate(cls, l):
        assert len(l) == 2

    @staticmethod
    def get_complement():
        return Add

    op = operator.sub

class Div(InverseOperation):
    @classmethod
    def validate(cls, l):
        assert len(l) == 2

    @staticmethod
    def get_complement():
        return Mul

    op = operator.div

class Group(Base):
    def __repr__(self):
        return type(self).__name__ + ': ' + str(self.cells)

    def reduce(self):
        return []

class MathGroup(Group):
    def __init__(self, operation, result, cells, natural, state):
        self.natural = natural
        self.cells = set(cells)
        self.operation = operation
        self.result = result
        self.state = state
        self.active = True

        for cell in cells:
            cell.groups.add(self)

    def as_dict(self):
        return dict(operation=self.operation.op.__name__, result=self.result)

    def reduce(self):
        retval = []

        if not self.active:
            return retval

        retval += self.operation.reduce(self)

        return retval

class LockedSet(Group):
    def __init__(self, state, cells):
        self.n = state.n
        self.cells = set(cells)
        self.state = state
        self.active = True

        for cell in cells:
            cell.groups.add(self)

    def reduce(self):
        if not self.active:
            return []

        taken = []
        retval = []

        for cell in self.cells:
            if cell.number:
                print 'taken'
                taken.append(cell.number)

        for cell in self.cells:
            intersection = cell.notes.intersection(taken).difference(set([cell.number]))
            if intersection:
                print 'eliminating from cell: ', cell.x, cell.y, 'numbers: ', intersection, 'taken: ', taken
                print 'old notes: ', cell.notes
                cell.remove_notes(intersection, retval)
                print 'new notes: ', cell.notes

        return retval


class State(Base):
    def __init__(self, n):
        self.n = n
        self.cells = [[Cell(i, j, self) for j in range(n)] for i in range(n)]
        self.groups = set()
        for cell_col in self.cells:
            self.groups.add(LockedSet(self, cell_col[:]))

        for i in range(n):
            cells = [self[j][i] for j in range(n)]
            self.groups.add(LockedSet(self, cells))


    def __getitem__(self, x):
        return self.cells[x]

    def add_group(self, group):
        self.groups.add(group)

    def as_dict(self):
        return dict(
            n=self.n,
            groups={
                str(hash(group)): group.as_dict() for group in
                    filter(lambda x: type(x) is MathGroup and x.natural, self.groups)
            },
            cells=[[cell.as_dict() for cell in c1] for c1 in self.cells])

    def reduce(self):
        stack = list()
        stack += list(self.groups)
        while stack:
            group = stack.pop()
            print 'reducing with group %s' % group
            result = group.reduce()
            for cell in result:
                print 'cell groups pushing: ', cell.groups
                stack.extend(list(cell.groups)) # - set([group])))

def build_3_state():
    return build_from_string(
        3,
        '''
        aab
        cdb
        cbb
        ''',
        {'a': (Sub, 1), 'b': (Mul, 12), 'c': (Div, 3), 'd': (Mul, 3)}
    )

def build_old_3_state():
    state = State(3)
    state.add_group(MathGroup(Sub, 1, [state[0][0], state[1][0]], True, state))
    state.add_group(MathGroup(Div, 3, [state[0][1], state[0][2]], True, state))
    state.add_group(MathGroup(Mul, 12, [state[1][2], state[2][1], state[2][2], state[2][0]], True, state))
    state.add_group(MathGroup(Mul, 3, [state[1][1]], True, state))
    return state

def build_from_string(n, string, mgroup_dict):
    state = State(n)
    positions_dict = {}
    for i, line in enumerate(string.split()):
        for j, char in enumerate(line):
            positions_dict.setdefault(char, []).append((j,i))

    map(
        state.add_group,
        map(
            lambda (key, (op, res)): MathGroup(op, res, map(lambda (k, l): state[k][l], positions_dict[key]), True, state),
            mgroup_dict.iteritems()
        )
    )

    return state

def build_5_state():
    return build_from_string(
        5,
        '''
        AABBB
        CCDEE
        FDDGH
        FIIGH
        FJJKK
        ''',
        {'A': (Add, 4), 'B': (Mul, 40), 'C': (Sub, 4), 'D': (Add, 7), 'E': (Sub, 1), 'F': (Add, 9),
         'G': (Sub, 3), 'H': (Sub, 2), 'I': (Sub, 2), 'J': (Div, 2), 'K': (Sub, 4)}
    )

def write_to_file(d, fname='samplefile.json'):
    f = open(fname, 'w')
    f.write(json.dumps(d))
    f.close()

def do():
    state = build_3_state()
    state.reduce()
    d = state.as_dict()
    print d
    write_to_file(d)
