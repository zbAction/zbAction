(function(){
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
			ele.css('display', 'table-cell');

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

				slide_to($target);
			});
		});

		return slide_to;
	};

	var slide_to = $('#slides').slideForm();

	function reset(){
		if(!$('#reg-board-url').get(0).checkValidity())
			return;

		$('#step_4bo aside').hide();
		$('#step_4bo #status').show();

		$.post(crawl_ep, {
			url: $('#reg-board-url').val()
		}).done(function(resp){
			if(resp.status === 6)
				$('#not-owned').show();
			else if(resp.status === 5)
				$('#not-a-board').show();
			else if(resp.status === 4)
				location.assign('/error/500');
			else if(resp.status === 3)
				$('#not-a-url').show();
			else if(resp.status === 2)
				$('#board-in-use').show();
			else if(resp.status === 0)
				slide_to($('#step_5bo'));
		}).fail(function(){
			location.assign('/error/500');
		}).always(function(){
			$('#status').hide();
		});
	}

	$('input[name=step_4bo]').click(reset);
	$('#reg-retry').click(reset);

	$('#step_5bo form').submit(function(){
		if($('#reg-password').val() !== $('#reg-conf-password').val()){
			$('#reg-conf-password').addClass('invalid');
			return;
		}

		$('#reg-finalize').val('Finalizing Registration');

		$.post(finalize_ep, {
			password: $('#reg-password').val()
		}).success(function(resp){
			if(!resp.hasOwnProperty('status') || resp.status !== 0)
				location.assign('/error/500');
			else
				location.replace('/meta/registered');
		}).fail(function(){
			location.assign('/error/500');
		});
	});

	$('input[name=step_3d]').parents('form').submit(function(){
		$.post(api_key_ep, {
			name: $('#mod-name').val()
		});
	});
})();
