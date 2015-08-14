module.exports = function(grunt) {
	grunt.initConfig({
		clean: {
			all: {
				src: ['**/*.min.*', '**/.sass-cache', '**/*.pyc', '**/*.map'],
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
					'static/bin/zb.action.min.js': ['static/socket.js', 'static/zb.action.js']
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
	});

	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.loadNpmTasks('grunt-contrib-sass');
	grunt.loadNpmTasks('grunt-contrib-watch');

	grunt.registerTask('default', ['clean', 'jshint', 'uglify', 'sass']);
};
