/*eslint-env node*/
var $    = require('gulp-load-plugins')();
var gulp = require('gulp');

gulp.task('jslint', ['jslint:app', 'jslint:config']);

gulp.task('jslint:app', function() {
  return gulp.src(global.paths.appJS)
    .pipe($.eslint())
    .pipe($.eslint.format());
});

gulp.task('jslint:config', function(){
  return gulp.src(global.paths.configJS)
    .pipe($.eslint({extends:'eslint:recommended'}))
    .pipe($.eslint.format());
});
