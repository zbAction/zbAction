module.exports = function(grunt) {
	var now = 1 * new Date;
	var latest_bin = 'bin/zb.action.min.' + 1 * new Date + '.js';

	var grunt_options = {
		clean: {
			all: {
				src: ['**/.sass-cache', '**/*.pyc', '**/*.map'],
			}
		},
		jshint: {
			files: ['static/*.js', 'static/js/*.js'],
			options: {
				globals: {
					jQuery: true
				}
			}
		},
		uglify: {
			everything: {
				files: {
				}
			}
		},
		sass: {
			dist: {
				options: {
					'sourcemap': 'none',
					'noCache': true,
					'style': 'compressed'
				},
				files: {
					'static/css/zba.css': 'static/css/zba.scss'
				}
			}
		},
		watch: {
			sass: {
				files: '**/*.scss',
				tasks: ['sass']
			}
		}
	};

	grunt_options.uglify.everything.files[latest_bin] = ['static/socket.js', 'static/zb.action.js'];

	grunt.initConfig(grunt_options);

	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.loadNpmTasks('grunt-contrib-sass');
	grunt.loadNpmTasks('grunt-contrib-watch');

	grunt.registerTask('default', ['clean', 'jshint', 'uglify', 'sass']);
};
