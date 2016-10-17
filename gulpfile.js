/*eslint-env node*/
// FOUNDATION FOR APPS TEMPLATE GULPFILE
// -------------------------------------
// This file processes all of the assets in the "client" folder, combines them with the Foundation for Apps assets, and outputs the finished files in the "build" folder as a finished app.

// 1. LIBRARIES
// - - - - - - - - - - - - - - -
//

/*
 * gulpfile.js
 * ===========
 * Rather than manage one giant configuration file responsible
 * for creating multiple tasks, each task has been broken out into
 * its own file in the 'gulp' folder. Any files in that directory get
 *  automatically required below.
 *
 * To add a new task, simply add a new task file in that directory.
 */
require('es6-promise').polyfill();
var gulp       = require('gulp');
var argv       = require('yargs').argv;
var requireDir = require('require-dir');

// 2. FILE PATHS
// - - - - - - - - - - - - - - -
// Specify paths & globbing patterns for tasks.
global.paths = {
  //use to copy view and shub to a temp build space
  temp:[
    './client/**/*.*',
    '!./client/index.html',
    './node_modules/lucidworks-view/client/**/*.*',
    './node_modules/lucidworks-view/client/assets/scss/_fonts.scss',
    '!./node_modules/lucidworks-view/client/**/app.js',
    '!./node_modules/lucidworks-view/client/index.html',
    '!./node_modules/lucidworks-view/client/templates/home.html',
    '!./node_modules/lucidworks-view/client/assets/js/controllers/Home*',
    '!./node_modules/lucidworks-view/client/assets/scss/app.scss',
    '!./node_modules/lucidworks-view/client/assets/img/iconic/logo.svg',
    '!./node_modules/lucidworks-view/client/assets/scss/_settings.scss'

  ],

  assets: [
    './build/client/**/*.*',
    '!./build/client/templates/**/*.*',
    '!./build/client/assets/{scss,js,components}/**/*.*'
  ],
  // Sass will check these folders for files when you use @import.
  sass: [
    'build/client/assets/scss',
    'bower_components/foundation-apps/scss',
    'bower_components/angucomplete-alt/angucomplete-alt.css',
    'build/client/assets/components/**/*.scss'
  ],
  // These files include Foundation for Apps and its dependencies
  foundationJS: [
    'bower_components/lodash/lodash.js',
    'bower_components/fastclick/lib/fastclick.js',
    'bower_components/viewport-units-buggyfill/viewport-units-buggyfill.js',
    'bower_components/tether/tether.js',
    'bower_components/hammerjs/hammer.js',
    'bower_components/angular/angular.js',
    'bower_components/angular-animate/angular-animate.js',
    'bower_components/angular-sanitize/angular-sanitize.js',
    'bower_components/angular-cookies/angular-cookies.js',
    'bower_components/angular-ui-router/release/angular-ui-router.js',
    'bower_components/angucomplete-alt/angucomplete-alt.js',
    'bower_components/angular-rison/dist/angular-rison.js',
    'bower_components/foundation-apps/js/vendor/**/*.js',
    'bower_components/foundation-apps/js/angular/**/*.js',
    '!bower_components/foundation-apps/js/angular/app.js',
    'bower_components/ng-orwell/Orwell.js',
    'bower_components/humanize/humanize.js',
    'bower_components/angularjs-humanize/src/angular-humanize.js',
    'bower_components/angular-nvd3/dist/angular-nvd3.js',
    'bower_components/d3/d3.min.js',
    'bower_components/nvd3/build/nv.d3.min.js'
  ],
  // These files are for your app's JavaScript
  appJS: [
    'build/client/assets/js/app.js',
    'build/client/assets/js/services/*.js',
    'build/client/assets/js/controllers/*.js',
    'build/client/assets/js/utils/**/*.js',
    'build/client/assets/components/**/*.js'
  ],
  components: [
    'build/client/assets/components/**/*.html',
    'bower_components/foundation-apps/js/angular/components/**/*.html'
  ],
  templates:[
    './build/client/templates/**/*.html'
  ],
  configJS: [
    './FUSION_CONFIG.js'
  ],
  configJSSample: [
    './FUSION_CONFIG.sample.js'
  ]
};

// Check for --production flag
global.isProduction = !!(argv.production);

// 3. TASKS
// - - - - - - - - - - - - - - -

// Require all tasks in the 'gulp' folder.
requireDir('./gulp', { recurse: false });


// Default task
//
// builds your app, starts a server, and recompiles assets when they change.

gulp.task('default', ['serve']);
