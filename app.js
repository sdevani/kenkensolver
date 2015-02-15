// first index is the column
// second index is the row

var colorGrids = function(groups) {
  for (var id in groups) {
    $("." + id).css({background: randomColor()});
  }
};

var groupLabel = function(group) {
  if (!group.labelled) {
    group.labelled = true;
    return group.operation + " " + group.result;
  }
  return ".";
};

var notesLabel = function(cell) {
  if (cell.notes) {
    return cell.notes.join(", ");
  } else {
    return ".";
  }
};

var constructCell = function(cell, groups) {
  var cellText = $('<div>');
  var groupText = groupLabel(groups[cell.group]);
  cellText.append($("<p>").text(groupText));
  cellText.append("<br>");
  cellText.append($("<h3>").text(cell.number));
  var notesText = notesLabel(cell);
  cellText.append($("<p>").text(notesText));
  var cellElem = $('<td>').append(cellText);
  cellElem.addClass(cell.group);
  return cellElem;
};

var constructGrid = function(data) {
  var grid = [];

  for (var i = 0; i < data.n; i++) {
    var row = $('<tr>');
    grid.push(row);
  }

  data.cells.forEach(function(column, colNum) {
    column.forEach(function(cell, rowNum) {
      var cellElem = constructCell(cell, data.groups);
      grid[rowNum].append(cellElem);
    });
  });

  grid.forEach(function(elem) {
    $('tbody').append(elem);
  });

  colorGrids(data.groups)
};

var randomColor = function() {
  var n1 = Math.floor(Math.random() * 75) + 180;
  var n2 = Math.floor(Math.random() * 75) + 180;
  var n3 = Math.floor(Math.random() * 75) + 180;

  return "rgb(" + n1 + "," + n2 + "," + n3 + ")";
};

$.get('/samplefile.json', constructGrid);