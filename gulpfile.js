var gulp = require('gulp');
var jasmine = require('gulp-jasmine');

gulp.task('solve', function() {
  var jsonfile = require('jsonfile');
  var data = require('./api/data/puzzle1.json');
  var Kenken = require('./api/services/solver.js');
  var kk = new Kenken(data);
  kk.solve();
  jsonfile.writeFileSync('output.json', kk.serialize());
});

gulp.task('test', function () {
  return gulp.src('spec/**/*')
    .pipe(jasmine());
});