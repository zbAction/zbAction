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

    $('#add-new-panel form').submit(function(e){
        e.preventDefault();

        var key = $('#new-mod-key').val().trim();

        if(mods.indexOf(key) === -1){
            $.post(get_mod_info_ep, {
                key: key
            }).done(function(resp){
                if(resp.status === 0 && resp.enabled){
                    $('#mod-name').text(resp.name || 'N/A');
                    $('#mod-key').text(resp.key);

                    $('#add-new-panel').slideUp();
                    $('#confirm-panel').slideDown();
                }
                else{
                    alert('This modification does not exist.');
                }
            }).fail(function(){
                location.assign('/error/500')
            });
        }
        else{
            alert('This modification is already in use.');
        }
    })
});
