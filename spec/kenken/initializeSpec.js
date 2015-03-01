var Kenken = require('../../api/services/solver.js');

describe("Kenken", function() {
  it("exists", function() {
    expect(Kenken).toBeDefined();
  });

  describe("initialization", function() {
    var inputs;

    beforeEach(function() {
      inputs = {};
    });

    describe("cell inputs", function() {
      it("errors with no inputs", function() {
        expect(function() {
          new Kenken();
        }).toThrow();
      });

      it("errors without cells", function() {
        expect(function() {
          new Kenken(inputs);
        }).toThrow();
      });

      it("errors without an array as an input", function() {
        inputs.cells = {a: "b"};
        expect(function() {
          new Kenken();
        }).toThrow();
      });

      it("errors without a 2d array as an input", function() {
        inputs.cells = [1, 2, 3];
        expect(function() {
          new Kenken(inputs);
        }).toThrow();;
      })

      it("errors without a square 2d array", function() {
        inputs.cells = [[1,2,3], [1,2]];
        expect(function() {
          new Kenken(inputs);
        }).toThrow();
      });

      it("errors if a cell is an object", function() {
        inputs.cells = [["a", "b"], ["c", {a: 5}]];
        expect(function() {
          new Kenken(inputs);
        }).toThrow();
      });
    });

    describe("groups", function() {
      beforeEach(function() {
        inputs = {
          cells: [["a", "a"], ["b", "b"]]
        };
      });

      it("errors without every group listed", function() {
        inputs.groups = {
          "a": {
            operation: "*",
            result: 10
          }
        };

        expect(function() {
          new Kenken(inputs);
        }).toThrow();
      });

      it("errors without operations and result listed per group", function() {
        inputs.groups = {
          "a": {
            operation: "*",
            result: 10
          },
          "b": {
            operation: "/"
          }
        };

        expect(function() {
          new Kenken(inputs);
        }).toThrow();
      });

      it("creates the board with all inputs", function() {
        inputs.groups = {
          "a": {
            operation: "*",
            result: 10
          },
          "b": {
            operation: "/",
            result: 4
          }
        };

        expect(new Kenken(inputs)).toBeDefined();
      });
    });
  });
});