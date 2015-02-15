// first index is the column
// second index is the row

$.get('/samplefile.json').then(function(data) {
  console.log(data.name);
});