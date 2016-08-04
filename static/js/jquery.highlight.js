(function($){
	$.fn.highlight = function(){
		$(this).each(function(){
			var $selectAll = $('<span>').text('Select All')
							.addClass('select-all');

			var content = $(this).text();
			var lines = content.split('\n').length;

			$selectAll.click(function(){
				var select = window.getSelection();

				if(select.rangeCount)
					select.removeAllRanges();

				var range = document.createRange();
				range.selectNode($(this).next().get(0));

				select.addRange(range);
			});

			$(this).prepend($selectAll);
		});
	};
})(jQuery);