/*eslint-env node*/
var gulp    = require('gulp');
var rimraf  = require('rimraf');

// Cleans the build directory
gulp.task('clean', function(cb) {
  rimraf('./build', cb);   //TODO: fix to clean out under python/server/
});

gulp.task('clean:templates', function(cb){
  rimraf('./server/assets/js/templates*.js', cb);
});

