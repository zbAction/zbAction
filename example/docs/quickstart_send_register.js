zbAction.register('example', function(action){
    alert('Received an action through event "example"');
});

zbAction.send({
    event: 'example',
    details: 'This is an example event.',
    receiver: {
        uid: example_uid
    }
});
