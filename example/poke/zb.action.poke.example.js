function poke(zbAction){
	var current_user = $('#top_info strong a').text();

	zbAction.register('poke', function(action){
		var poked_by = action.source.name || 'A user with the ID ' + action.source.uid;
		alert('You have been poked by: ' + poked_by);
	});

	// TODO: Fill in code to actually poke somebody.

	zbAction.send({
		event: 'poke',
		details: 'Poked by ' + current_user,
		receiver: {
			uid: $.zb.stat.mid
		}
	});
}

zbAction.ready(
	/* This is your modification key. Once set, it should never change. */
	/* This value should match the one in your manifest.json. */
	"1234-5678-9101-1123",
	/* This is your callback function. It should take one argument (zbAction). */
	poke
);