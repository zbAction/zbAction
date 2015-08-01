module.exports = function(grunt) {
	grunt.initConfig({
		clean: {
			all: {
				src: ['*.min.*', '.sass-cache', '*.pyc', '*.map'],
			}
		},
		jshint: {
			files: ['Gruntfile.js', '*.js'],
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
				files: {
					'static/css/zba.css': 'static/css/zba.scss'
				}
			},
			options: {
				cache: false
			}
		}
	});

	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.loadNpmTasks('grunt-contrib-sass');
	grunt.registerTask('default', ['clean', 'jshint', 'uglify', 'sass']);
};