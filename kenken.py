import itertools
import json
import operator
import random

class MyException(Exception):
    pass

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
        assert type(self.notes) is set
        self.state = state

    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)

    def get_notes(self):
        assert type(self.notes) is set
        return self.notes

    def remove_notes(self, notes_to_remove, retval):
        assert type(notes_to_remove) is set
        assert type(self.notes) is set
        self.set_notes(self.notes - notes_to_remove, retval)

    def set_notes(self, notes_to_set, retval):
        assert type(notes_to_set) is set
        assert type(self.notes) is set
        print self.notes, notes_to_set
        if self.notes - notes_to_set:
            retval.append(self)
            self.notes = notes_to_set.copy()

        if len(self.notes) == 1:
            self.number = list(self.notes)[0]
            # Detect inactive group here??

        if not self.notes:
            raise MyException

    def as_dict(self):
        assert type(self.notes) is set
        groups = filter(lambda g: type(g) is MathGroup and g.natural, self.groups)
        if groups:
            group, = groups
        else:
            group = None

        return dict(
            group=str(hash(group)) if group else None,
            notes=list(self.notes),
            number=self.number,
            x=self.x,
            y=self.y,
        )

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
            assert type(cell.notes) is set
            print 'this notes: ', cell.notes
            other_cells = cells - set([cell])
            for other_cell in other_cells:
                assert type(other_cell.notes) is set
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
            assert type(cell.notes) is set

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
        for cell in cells:
            assert type(cell.notes) is set
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

        for cell in cells:
            assert type(cell.notes) is set

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
        if not self.active:
            return []

        return self.operation.reduce(self)

class LockedSet(Group):
    def __init__(self, state, cells, possibilities=None):
        assert len(cells) > 0
        self.possibilities = possibilities or set(range(1, state.n + 1))
        self.cells = set(cells)
        self.state = state
        self.active = True

        for cell in cells:
            cell.groups.add(self)

    def reduce(self):
        retval = []

        if not self.active:
            return retval

        # Only need to do once for group
        for cell in self.cells:
            assert type(cell.notes) is set
            cell.remove_notes(cell.notes - self.possibilities, retval)
            assert type(cell.notes) is set

        cells = sorted(self.cells, key=lambda cell: len(cell.notes))
        for cell in cells:
            subset_cells = set(filter(
                lambda c: c.notes.issubset(cell.notes),
                cells,
            ))
            if len(subset_cells) == len(self.cells):
                continue # could probably break

            assert len(subset_cells) <= len(cell.notes)
            if len(subset_cells) == len(cell.notes):
                self.active = False
                group1 = LockedSet(self.state, subset_cells, possibilities=cell.notes.copy())
                retval += group1.reduce()
                self.state.add_group(group1)

                if len(self.cells) > len(subset_cells): # don't want to create empty locked set
                    group2 = LockedSet(self.state, set(self.cells) - subset_cells, possibilities=self.possibilities - cell.notes)
                    retval += group2.reduce()
                    self.state.add_group(group2)

                break

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

    def solved(self):
        return all(map(lambda cell: cell.number, sum(self.cells, [])))

    def apply_seed(self):
        retval = []
        first_unsolved = min([cell for cell in sum(self.cells, []) if not cell.number], key=lambda cell: len(cell.notes))
        print first_unsolved.number, first_unsolved.notes, first_unsolved
        notes = list(first_unsolved.notes)
        num_to_assign = random.choice(notes)
        assert len(first_unsolved.notes) > 1
        first_unsolved.set_notes(set([num_to_assign]), retval)
        return retval

    def add_group(self, group):
        self.groups.add(group)

    def as_dict(self):
        for cell in sum(self.cells, []):
            assert type(cell.notes) is set
        retval = dict(
            n=self.n,
            groups={
                str(hash(group)): group.as_dict() for group in
                    filter(lambda x: type(x) is MathGroup and x.natural, self.groups)
            },
            cells=[[cell.as_dict() for cell in c1] for c1 in self.cells])

        for cell in sum(self.cells, []):
            assert type(cell.notes) is set

        return retval
    def reduce(self):
        stack = list()
        stack += list(self.groups)
        while stack:
            group = stack.pop()
            print 'reducing with group %s' % group
            result = group.reduce()
            for cell in set(result):
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

def build_from_string_2(n, string, ops):
    def parser(s):
        return (
            {
                '+': Add,
                '-': Sub,
                'x': Mul,
                '%': Div,
            }[s[0]],
            int(s[1:]),
        )

    return build_from_string(n, string,
        {op[0]: parser(op[1:]) for op in ops.split()}
    )

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

def build_7_state():
    return build_from_string_2(
        7,
        '''
        AAABBCC
        DEEBFFG
        DHHIJJG
        KKKILLG
        KMNNOLP
        QMRRSSP
        QMRTTUU
        ''',
        '''
        Ax60  Bx35  C-4
        D+5   E-6   F-4
        G+15  H%3   I-3
        J-4   K+16  L+8
        Mx24  N-5   O+5
        P%2   Q-5   Rx90
        S-1   T%2   U+8
        '''
        )

def build_9_state():
    return build_from_string_2(
        9,
        '''
        AAABBCDDE
        FGGHICKKE
        FJJHIMNOO
        FPQQIMMRR
        SPTQUUVVW
        SPTUUXYWW
        ZaabbXYcc
        deefbggch
        diifjjkkh
        ''',
        '''
        Ax162 B+9   C-1   D-3   E-6
        F+20  G%3   H+14  I+15  K+12
        J-2   M+11  N+9   O-5   P+24
        Q+13  R+10  S%2   Tx35  Ux216
        V+17  Wx10  X+10  Y-2   Zx9
        a%2   b+13  c+16  d-5   e-2
        f%2   g-6   h-2   i+13  j%2
        k-4
        '''
        )

def build_other_9_state():
    return build_from_string_2(
        9,
        '''
        AABBCCCDE
        FFFGHIIIE
        JJGGHKKLE
        JMMNNNLLO
        PQQQRRRRO
        PSSTTUVWX
        PSYYZUVWX
        abbbZccdd
        abeeffcdd
        ''',
        '''
        A-5 B-5 Cx40 D+6 E+13
        F+24 G+13 H-6 I+15
        Jx30 K+11 Lx15 M-8 Nx224 O+10
        S+8 T+13 U-8 V+11 W-1 X-2 Y-7 Z-4
        a%4 bx1260 c+13 dx567 e-3 f-1
        '''
    )

def write_to_file(d, fname='samplefile.json'):
    f = open(fname, 'w')
    f.write(json.dumps(d))
    f.close()

def seed_generator(n):
    def base_convert(val):
        return [val] if val < n else base_convert(val / n) + base_convert(val % n)

    i = 0
    while True:
        yield base_convert(i)
        i += 1

def hax_branch_solver(builder):
    while True:
        state = builder()
        try:
            state.reduce()
            for cell in sum(state.cells, []):
                assert type(cell.notes) is set
            write_to_file(state.as_dict())
            for cell in sum(state.cells, []):
                assert type(cell.notes) is set
            while not state.solved():
                for cell in sum(state.cells, []):
                    assert type(cell.notes) is set
                state.apply_seed()
                for cell in sum(state.cells, []):
                    assert type(cell.notes) is set
                state.reduce()
                for cell in sum(state.cells, []):
                    assert type(cell.notes) is set
        except Exception: # fix bug and change to MyException
            pass
        else:
            break

    d = state.as_dict()
    print d
    print '\n'.join(map(lambda row: ' '.join(map(lambda cell: str(cell.number), row)), state.cells))
    write_to_file(d)


def do():
    hax_branch_solver(build_other_9_state)
    return

    state = build_7_state()
    state.reduce()
    d = state.as_dict()
    print d
    write_to_file(d)


