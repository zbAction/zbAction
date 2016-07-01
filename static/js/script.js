(function(window){
	$('.select').focus(function(){
		$(this).select();
	});

	hljs.configure({
		tabReplace: '    '
	});

	hljs.initHighlightingOnLoad();

	$('pre').has('code').highlight();
})();
