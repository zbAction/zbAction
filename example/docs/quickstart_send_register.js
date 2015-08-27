zbAction.register('example', function(action){
    alert('Received an action through event "example"');
    alert('Event name: ' + action.event + '\nEvent Details: ' + action.details);
});

zbAction.send({
    event: 'example',
    details: 'This is an example event.',
    receiver: {
        uid: example_uid
    }
});
