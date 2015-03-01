var Cell = require("./cells.js");
var Group = require("./group.js");

var Kenken = function(data) {
  Kenken.ensureSquareBoard(data.cells);

  this.gatherGroups(data.cells);
  this.ensureGroupsMatch(data.groups);

  this.groups = {};
  for (groupId in data.groups) {
    this.groups[groupId] = new Group(groupId, data.groups[groupId]);
  }

  this.cells = data.cells.map(function(row, rowNumber) {
    return row.map(function(cell, colNumber) {
      var cell = new Cell(cell, rowNumber, colNumber);
      this.groups[cell.group].cells.push(cell);
    });
  });
};

Kenken.ensureSquareBoard = function(cells) {
  var squareLength = cells.length;
  cells.forEach(function(row) {
    if(row.length != squareLength) {
      throw new Kenken.InputError("Not a square array");
    }

    row.forEach(function(cell) {
      if (cell instanceof Object) {
        throw new Kenken.InputError("Invalid cell");
      }
    });
  });
};

Kenken.prototype.gatherGroups = function(cells) {
  this.groupsNeeded = {};
  var _this_ = this;

  cells.forEach(function(row) {
    row.forEach(function(cell) {
      _this_.groupsNeeded[cell] = false;
    });
  });
};

Kenken.prototype.ensureGroupsMatch = function(groups) {
  for (group in groups) {
    this.groupsNeeded[group] = true;
    var groupObj = groups[group];
    if (!groupObj.operation || !groupObj.result) {
      throw new Kenken.InputError("Invalid group");
    }
  }

  for (group in this.groupsNeeded) {
    if (!this.groupsNeeded[group]) {
      throw new Kenken.InputError("Group not found");
    }
  }
};

Kenken.prototype.solve = function() {
  throw new Kenken.ImpossiblePuzzle("Impossible Puzzle");
};

Kenken.prototype.serialize = function() {
  return {
    a: 5,
    b: 10
  };
};

Kenken.InputError = function(message) {
  this.name = "InputError";
  this.message = message || "";
}

Kenken.InputError.prototype = Error.prototype;

Kenken.ImpossiblePuzzle = function(message) {
  this.name = "ImpossiblePuzzle";
  this.message = message || "";
}

Kenken.ImpossiblePuzzle.prototype = Error.prototype;

module.exports = Kenken;