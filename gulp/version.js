/*eslint-env node*/
var $               = require('gulp-load-plugins')();
var gulp            = require('gulp');
var argv            = require('yargs').argv;

gulp.task('version', function(){
  return gulp.src(['package.json', 'bower.json'])
    .pipe($.jsonEditor(function(json) {
      json.version = argv.version;
      return json; // must return JSON object.
    }))
    .pipe(gulp.dest('.'));
});
