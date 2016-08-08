/*eslint-env node*/
/*global global*/
/*eslint no-console:0*/

var $               = require('gulp-load-plugins')();
var gulp            = require('gulp');
var router          = require('front-router');
var sequence        = require('run-sequence');

// Builds your entire app once, without starting a server
gulp.task('build', function(cb) {
  sequence('clean', 'writeDevConfig', 'copy-temp', [ 'copy', 'copy:snowplow', 'copy:index', 'copy:foundation', 'sass', 'uglify'], 'copy:templates', 'copy:config', cb);
});

//copy everything to a temp area
gulp.task('copy-temp', function() {
  return gulp.src(global.paths.temp, {
  })
    .pipe(gulp.dest('./build/client'));
});



// Copies everything in the client folder except templates, Sass, and JS
gulp.task('copy', function() {
  return gulp.src(global.paths.assets, {
    base: './build/client/'
  })
    .pipe(gulp.dest('./python/server'));

});

// Copies your app's page templates and generates URLs for them
gulp.task('copy:templates', function() {
  return gulp.src(global.paths.templates)
    .pipe(router({
      path: 'python/server/assets/js/routes.js',
      root: './build/client'
    }))
    .pipe(gulp.dest('./python/server/templates'));
});

gulp.task('copy:index', function() {
  return gulp.src('./client/index.html')
    .pipe(gulp.dest('./python/server/flask_templates'));
});


gulp.task('copy:snowplow', function() {
  return gulp.src('./client/assets/js/snowplow*.js')
    .pipe(gulp.dest('./python/server/assets/js'));
});

// Compiles the Foundation for Apps directive partials into a single JavaScript file
gulp.task('copy:foundation', function(cb) {
  gulp.src('bower_components/foundation-apps/js/angular/components/**/*.html')
    .pipe($.ngHtml2js({
      prefix: 'components/',
      moduleName: 'foundation',
      declareModule: false
    }))
    .pipe($.uglify())
    .pipe($.concat('templates.js'))
    .pipe(gulp.dest('./python/server/assets/js'));

  gulp.src('build/client/assets/components/**/*.html')
    .pipe($.ngHtml2js({
      prefix: 'assets/components/',
      moduleName: 'foundation',
      declareModule: false
    }))
    .pipe($.uglify())
    .pipe($.concat('templates-shub.js'))
    .pipe(gulp.dest('./python/server/assets/js'));


  // Iconic SVG icons
  gulp.src('./bower_components/foundation-apps/iconic/**/*')
    .pipe(gulp.dest('./python/server/assets/img/iconic/'));

  cb();
});

// Compiles and copies the Foundation for Apps JavaScript, as well as your app's custom JS
gulp.task('uglify', ['uglify:foundation', 'uglify:app']);

gulp.task('uglify:foundation', function() {
  var uglify = $.if(global.isProduction, $.uglify()
    .on('error', function (e) {
      console.log(e);
    }));

  return gulp.src(global.paths.foundationJS)
    .pipe(uglify)
    .pipe($.concat('foundation.js'))
    .pipe(gulp.dest('./python/server/assets/js/'));
});

gulp.task('uglify:app', function() {
  var uglify = $.if(global.isProduction, $.uglify()
    .on('error', function (e) {
      console.log(e);
    })),
    sourcemapsInit = $.if(!global.isProduction, $.sourcemaps.init()),
    sourcemapsWrite = $.if(!global.isProduction, $.sourcemaps.write('.'));

  return gulp.src(global.paths.appJS)
   .pipe(sourcemapsInit)
   .pipe($.ngAnnotate())
   .pipe(uglify)
   .pipe($.plumber())
   .pipe($.directiveReplace({root: 'build/client'}))
   .pipe($.concat('app.js'))
   .pipe(sourcemapsWrite)
   .pipe(gulp.dest('./python/server/assets/js/'));
});
