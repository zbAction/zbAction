$(function(){
    $('.mod .remove').click(function(){
        var $container = $(this).parents('.mod').first();
        var api_key = $container.attr('id');

        $container.addClass('working');

        $.post(update_mod_keys_ep, {
            key: api_key
        }).done(function(e){
            if(e.status === 0){
                $container.remove();
            }
            else{
                location.assign('/error/500');
            }
        }).fail(function(){
            location.assign('/error/500');
        });
    });
});
