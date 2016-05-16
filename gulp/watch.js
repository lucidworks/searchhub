/*eslint-env node*/
var gulp = require('gulp');


gulp.task('watch', function(){
  //watch img
  gulp.watch(['./client/**/*'], ['build']);

  // Watch config
  gulp.watch(global.paths.configJS, ['build']);

  // Watch config sample
  gulp.watch(global.paths.configJSSample, ['build']);
});
