zbAction.ready('example_key', function(zbAction){
    $('#profile_menu').find('ul').append(
        $('<li>').append(
            $('<a>').attr({
                'href': '#',
                'id': 'zba-poke-example'
            }).text('Poke')
        )
    );

    $('#zba-poke-example').click(function(e){
        e.preventDefault();

        var current_user = location.href.match(/\/(\d+)\/$/).pop();

        zbAction.send({
            event: 'zba-poke-example',
            details: 'This is an example poke.',
            receiver: {
                uid: current_user
            }
        });
    });

    zbAction.register('zba-poke-example', function(action){
        alert('You have been poked by ' + action.source.name);
    });
});
