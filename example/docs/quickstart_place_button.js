zbAction.ready('example_key', function(zbAction){
    $('#profile_menu').find('ul').append(
        $('<li>').append(
            $('<a>').attr({
                'href': '#',
                'id': 'zba-poke-example'
            }).text('Poke')
        )
    );
});
