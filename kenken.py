import json
import operator

class Base(object):
    def as_dict(self):
        return vars(dict)

class Cell(Base):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.groups = set()
        self.number = None
        self.notes = []

    def as_dict(self):
        groups = filter(lambda g: type(g) is MathGroup and g.natural, self.groups)
        if groups:
            group, = groups
        else:
            group = None

        ret = vars(self)
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
    pass

class MathGroup(Group):
    def __init__(self, operation, result, cells, natural):
        self.natural = natural
        self.cells = set(cells)
        self.operation = operation
        self.result = result

        for cell in cells:
            cell.groups.add(self)

    def as_dict(self):
        return dict(operation=self.operation.op.__name__, result=self.result)

class State(Base):
    def __init__(self, n):
        self.n = n
        self.cells = [[Cell(i, j) for j in range(n)] for i in range(n)]
        self.groups = set()

    def __getitem__(self, x):
        return self.cells[x]

    def add_group(self, group):
        self.groups.add(group)

    def as_dict(self):
        return dict(n=self.n, groups={str(hash(group)): group.as_dict() for group in self.groups},
            cells=[[cell.as_dict() for cell in c1] for c1 in self.cells])

def build_3_state():
    state = State(3)
    state.add_group(MathGroup(Add, 3, [state[0][1], state[0][0]], True))
    state.add_group(MathGroup(Add, 6, [state[1][0], state[2][0], state[2][1]], True))
    state.add_group(MathGroup(Mul, 9, [state[0][2], state[1][1], state[1][2]], True))
    state.add_group(MathGroup(Add, 9, [state[2][2]], True))
    return state
