
ecs.communication = {
    init_thread: function(container) {
        container = $(container);

        container.on('click', '.message .card-header', function(ev) {
            var el = $(this);
            ev.preventDefault();
            el.next('.card-block').toggle();
            el.find('.preview').toggle();
        });

        container.on('click', '.collapse_all', function(ev) {
            ev.preventDefault();
            container.find('.message .card-block').prop('hidden', true);
            container.find('.message .preview').prop('hidden', false);
        });

        container.on('click', '.expand_all', function(ev) {
            ev.preventDefault();
            container.find('.message .card-block').prop('hidden', false);
            container.find('.message .preview').prop('hidden', true);
        });
    }
};
