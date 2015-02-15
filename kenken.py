import json
import operator

class Base(object):
    def as_dict(self):
        return vars(dict)

class Cell(Base):
    def __init__(self, x, y, state):
        self.x = x
        self.y = y
        self.groups = set()
        self.number = None
        self.notes = range(1, state.n + 1)
        self.state = state

    def as_dict(self):
        groups = filter(lambda g: type(g) is MathGroup and g.natural, self.groups)
        if groups:
            group, = groups
        else:
            group = None

        ret = vars(self)
        del ret['groups']
        del ret['state']
        ret.update(group=str(hash(group)) if group else None)
        return ret

class Operation(Base):
    @classmethod
    def validate(cls, l):
        pass

    @classmethod
    def perform(cls, l):
        return reduce(cls.operator, l)

class Add(Operation):
    op = operator.add

class Sub(Operation):
    @classmethod
    def validate(cls, l):
        assert len(l) == 2

    op = operator.sub

class Div(Operation):
    @classmethod
    def validate(cls, l):
        assert len(l) == 2

    op = operator.div

class Mul(Operation):
    op = operator.mul

class Group(Base):
    def reduce(self):
        pass

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
        if len(self.cells) == 1:
            cell = self.cells.pop()
            assert cell.number is None
            assert self.result in cell.notes, '%s, %s' % (self.result, cell.notes)
            cell.number = self.result
            self.active = False

class State(Base):
    def __init__(self, n):
        self.n = n
        self.cells = [[Cell(i, j, self) for j in range(n)] for i in range(n)]
        self.groups = set()

    def __getitem__(self, x):
        return self.cells[x]

    def add_group(self, group):
        self.groups.add(group)

    def as_dict(self):
        return dict(n=self.n, groups={str(hash(group)): group.as_dict() for group in self.groups},
            cells=[[cell.as_dict() for cell in c1] for c1 in self.cells])

    def reduce(self):
        stack = list()
        stack += list(self.groups)
        while stack:
            group = stack.pop()
            group.reduce()

def build_3_state():
    state = State(3)
    state.add_group(MathGroup(Add, 3, [state[0][1], state[0][0]], True, state))
    state.add_group(MathGroup(Add, 6, [state[1][0], state[2][0], state[2][1]], True, state))
    state.add_group(MathGroup(Mul, 9, [state[0][2], state[1][1], state[1][2]], True, state))
    state.add_group(MathGroup(Add, 2, [state[2][2]], True, state))
    return state

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
