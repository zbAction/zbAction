zbAction.ready('example_key', function(zbAction){
    $('#profile_menu').find('ul').append(
        $('<li>').append(
            $('<a>').attr({
                'href': '#',
                'id': 'zba-poke-example'
            }).text('Poke')
        )
    );

    zbAction.register('zba-poke-example', function(action){
        alert('You have been poked by ' + action.source.name);
    });
});
