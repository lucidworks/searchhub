/*eslint-env node*/
/*eslint no-console:0*/
var $               = require('gulp-load-plugins')();
var gulp            = require('gulp');
var fs              = require('fs');

// Copies your app's vonfig
gulp.task('copy:config', function() {
  if(fs.existsSync(global.paths.configJS[0])){ //If the file exists use that, or copy from the sample
    return gulp.src(global.paths.configJS).pipe(gulp.dest('./python/server/assets/js/'));
  }
  else {
    return gulp.src(global.paths.configJSSample)
      .pipe($.rename('FUSION_CONFIG.js'))
      .pipe(gulp.dest('./'))
      .pipe(gulp.dest('./python/server/assets/js/'));
  }
});

// Copies your app's page templates and generates URLs for them
gulp.task('copy:configSample', function() {
  if(!fs.existsSync(global.paths.configJS[0])){
    return gulp.src(global.paths.configJSSample).pipe($.rename('FUSION_CONFIG.js')).pipe(gulp.dest('./'));
  }
  else{
    return false;
  }
});

// gulp.task('writeBuildConfig', function(){
//   fs.readFile('./FUSION_CONFIG.js', 'utf8', function(err, data){
//     if (err) {
//       return console.log(err);
//     }
//     var file = 'var appConfig = (function(){\n var ' + data + 'return appConfig;})();';
//     fs.writeFile('./build/assets/js/fusion_config.js',file);
//   });
// });

gulp.task('writeDevConfig', function(){
  fs.readFile('./FUSION_CONFIG.js', 'utf8', function(err, data){
    if (err) {
      return console.log(err);
    }
    var file = 'var ' + data + 'module.exports = appConfig;';
    var dir = './tmp';
    if (!fs.existsSync(dir)){
      fs.mkdirSync(dir);
    }
    fs.writeFile('./tmp/fusion_config.js',file);
  });
});
