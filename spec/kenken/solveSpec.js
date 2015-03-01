var Kenken = require('../../api/services/solver.js');

describe("Kenken", function() {
  describe("solve", function() {
    it("recognizes unsolvable puzzles", function() {
      var kenken = new Kenken({
        cells: [["a", "a"], ["b", "b"]],
        groups: {
          a: {
            operation: "*",
            result: 1
          },
          b: {
            operation: "/",
            result: 1
          }
        }
      });

      expect(function() {
        kenken.solve();
      }).toThrow(new Kenken.ImpossiblePuzzle("Impossible Puzzle"));
    });

    it("solves other puzzles", function() {
      var kenken = new Kenken({
        cells: [["a", "a"], ["b", "b"]],
        groups: {
          a: {
            operation: "*",
            result: 2
          },
          b: {
            operation: "/",
            result: 2
          }
        }
      });
    });
  });
});