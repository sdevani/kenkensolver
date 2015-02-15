// first index is the column
// second index is the row

var colorGrids = function(groups) {
  for (var id in groups) {
    $("." + id).css({background: randomColor()});
  }
}

var constructGrid = function(data) {
  var grid = [];

  for (var i = 0; i < data.n; i++) {
    var row = $('<tr>');
    grid.push(row);
  }

  data.cells.forEach(function(column, colNum) {
    column.forEach(function(cell, rowNum) {
      var cellElem = $('<td>').text(cell.number);
      cellElem.addClass(cell.group);
      grid[rowNum].append(cellElem);
    });
  });

  grid.forEach(function(elem) {
    $('tbody').append(elem);
  });

  colorGrids(data.groups)
};

var randomColor = function() {
  var n1 = Math.floor(Math.random() * 127) + 128;
  var n2 = Math.floor(Math.random() * 127) + 128;
  var n3 = Math.floor(Math.random() * 127) + 128;

  return "rgb(" + n1 + "," + n2 + "," + n3 + ")";
};

$.get('/samplefile.json', constructGrid);