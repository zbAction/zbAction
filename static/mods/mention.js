/*
 * Name: User Mention
 * Author: The zbAction Team
 * Site: https://zbaction.reticent.io/
 */

zbAction.ready('19fef61b-333d-4c32-9e44-28c04edf6dae', function(zba){
    var ls_key = 'zba_19fef61b-333d-4c32-9e44-28c04edf6dae';
    var regex = /\[mention\](.+?)\[\/mention\]/gi;
    var message = '{poster} has mentioned you in a post.';

    zba.register('zba-user-mention', function(action){
        $.growl({
            title: '',
            message: message.replace('{poster}', action.source.name),
            duration: 5000,
            url: JSON.parse(action.details),
            location: 'bl'
        });
    });

    function check_mention(){
        $('form[action$=/post/]').submit(function(e){
            var users = [];
            var content = $('form[action$=/post/] textarea').val();

            content.replace(regex, function(m, p){
                users.push(p);
            })

            localStorage[ls_key] = JSON.stringify(users);
        });
    }

    function try_mention(){
        if(localStorage[ls_key]){
            var you = $('#top_info strong a').text();
            var latest_post = $('.c_postfoot').last().prev().prev().prev().attr('id');
            var post_url = location.href.split('#')[0] + '#' + latest_post;
            var users = JSON.parse(localStorage[ls_key]);

            users.forEach(function(user){
                zba.send({
                    event: 'zba-user-mention',
                    details: post_url,
                    receiver: {
                        uid: zba.users.by_name(user)
                    }
                });
            });
        }
    }

    function parse_mention(){
        $('.c_post').each(function(){
            var html = $(this).html();
            html = html.replace(regex, function(m, name){
                var uid = zba.users.by_name(name);

                if(!uid) return m;

                var $link = $('<a>')
                                .attr('href', $.zb.stat.url + 'profile/' + zba.users.by_name(name) + '/')
                                .text(name);

                return $link.prop('outerHTML');
            });

            $(this).html(html);
        });
    }

    // This check should be sufficient to ensure only new posts are checked for mentions.
    if(location.href.match(/topic\/\d+/) || location.href.match(/\/post\/(\?type=1&mode=1|$)/)){
        check_mention();
    }

    if(location.href.match(/topic\/\d+/)){
        try_mention();
        parse_mention();
    }

    delete localStorage[ls_key];
});
