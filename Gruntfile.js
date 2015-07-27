module.exports = function(grunt) {
	grunt.initConfig({
		clean: {
			all: {
				src: ['*.min.*'],
				filter: 'isFile'
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
					'static/bin/zb.action.min.js': ['socket.js', 'zb.action.js']
				}
			}
		}
	});

	grunt.loadNpmTasks('grunt-contrib-clean');
	grunt.loadNpmTasks('grunt-contrib-jshint');
	grunt.loadNpmTasks('grunt-contrib-uglify');
	grunt.registerTask('default', ['clean', 'jshint', 'uglify']);
};