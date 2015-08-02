$.fn.valid = function(){
	var ele = $(this).get();
	var valid = true;

	for(var n = 0; n < ele.length; n++){
		if(!ele[n].checkValidity()){
			ele[n].classList.add('invalid');
			valid = false;
		}
		else{
			ele[n].classList.remove('invalid');
		}
	}

	return valid;
};

$('form').submit(function(){
	return false;
});

$('input').change(function(){
	$(this).valid();
});

$('input').keydown(function(){
	$(this).valid();
});

$.fn.slideForm = function(){
	$(this).find('form').submit(function(e){
		e.preventDefault();
	});

	var container = this;

	function slide_to(ele){
		var $slides = $(container).find('> .slide:visible');
		var dest = $slides.index(ele);
		var offset = '-' + dest * 100 + 'vw';
		
		$(container).css('transform', 'translateX(' + offset + ')');
	}

	$(this).find('.slide').each(function(){
		var that = this;

		$(this).find('button, input[type=submit]').click(function(e){
			if(!$(that).find('form input').valid())
				return;

			var $target = $('#' + this.name);
			$target.css('display', 'table-cell');

			slide_to($target);
		});
	});
};

$('#slides').slideForm();