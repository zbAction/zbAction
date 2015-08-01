$('#step_1 button').click(function(e){
	e.preventDefault();

	if(this.value === 'owner'){
		$('#step_2bo').css('display', 'table-cell');
		$('#slides').css('transform', 'translate3d(-100vw, 0, 0)');
	}
});