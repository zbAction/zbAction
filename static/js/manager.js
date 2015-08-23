$(function(){
    $('.mod .remove').click(function(){
        var $container = $(this).parents('.mod').first();
        var api_key = $container.attr('id');

        $container.addClass('working');

        $.post(update_mod_keys_ep, {
            key: api_key
        }).done(function(resp){
            if(resp.status === 0){
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
            $('#add-new-panel button .fa-spinner').show();
            $('#add-new-panel button .content').hide();

            $.post(get_mod_info_ep, {
                key: key
            }).done(function(resp){
                if(resp.status === 0 && resp.enabled){
                    $('#mod-name').text(resp.name || 'N/A');
                    $('#mod-key').text(resp.key);
                    $('#add-mod-status').text('');

                    $('#add-new-panel').slideUp();
                    $('#confirm-panel').slideDown();
                }
                else{
                    $('#add-mod-status').text('This modification does not exist.');
                }
            }).fail(function(){
                location.assign('/error/500')
            }).always(function(){
                $('#add-new-panel button .fa-spinner').hide();
                $('#add-new-panel button .content').show();
            });
        }
        else{
            $('#add-mod-status').text('This modification is already in use.');
        }
    });

    $('#cancel-add').click(function(){
        $('#add-new-panel').slideDown();
        $('#confirm-panel').slideUp();
    });

    $('#confirm-add').click(function(){
        var key = $('#new-mod-key').val().trim();

        $('#confirm-add .fa-spinner').show();
        $('#confirm-add .content').hide();

        $.post(update_mod_keys_ep, {
            key: key
        }).done(function(resp){
            if(resp.status === 0){
                location.assign('/manager/');
            }
            else{
                location.assign('/error/500');
            }
        }).fail(function(){
            location.assign('/error/500');
        });
    });
});
