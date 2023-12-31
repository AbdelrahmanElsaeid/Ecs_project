

//---------------------------------------------
ecs.textarea.toolbarItems = {};

ecs.textarea.toolbarItems.boilerplate = function(label, url) {
    return function(textarea) {
        var button = $('<a>', {
            title: label,
            'class': 'fa fa-2x fa-paragraph text-primary',
            click: function(ev) {
                ev.preventDefault();
                var status = {
                    value: textarea.val().slice(
                        textarea.prop('selectionStart'),
                        textarea.prop('selectionEnd'))
                };
                var container = $('<div>', {'class': 'boilerplate_container'});
                var selector = $('<div>', {'class': 'boilerplate_selector'});
                var searchInput = $('<input>', {type: 'text', value: status.value, 'class': 'form-control'});
                var resultList = $('<div>', {'class': 'list-group resultlist'});
                selector.append(searchInput);
                selector.append(resultList);
                container.append(selector);
                $(textarea).before(container);
                var dispose = function() {
                    $(window).off('click', dispose);
                    clearInterval(status.interval);
                    container.remove();
                };
                var insert = function(text) {
                    dispose();
                    textarea.focus();
                    var v = textarea.val();
                    var s = textarea.prop('selectionStart');
                    var e = textarea.prop('selectionEnd');
                    textarea.val(v.slice(0, s) + text + v.slice(e, -1));
                    textarea.prop('selectionStart', s);
                    textarea.prop('selectionEnd', s + text.length);
                    textarea.trigger('input');
                };
                var update = function(q, initial) {
                    var csrftoken = document.cookie.match(/.*csrftoken=([^;]*).*/)[1];
                    $.get({
                        url: url + '?q=' + encodeURIComponent(q),
                        headers: {'X-CSRFtoken': csrftoken},
                        dataType: 'json',
                        success: function(results){
                            if(initial){
                                if(results.length == 1){
                                    insert(results[0].text);
                                    return;
                                }
                                $(window).click(dispose);
                                container.show();
                                searchInput.focus();
                            }
                            resultList.html('');
                            results.forEach(function(text) {
                                var display = $('<a>', {
                                    class: 'list-group-item list-group-item-action d-block',
                                    html: '<strong>' + text.slug + '</strong>: ' + text.text,
                                    href: '#',
                                    click: function(ev) {
                                        ev.preventDefault();
                                        insert(text.text);
                                    }
                                });
                                resultList.append(display);
                            });
                        }
                    });
                };
                update(status.value, true);
                searchInput.keydown(function(ev) {
                    if(ev.key == 'Enter'){
                        ev.preventDefault();
                        update(searchInput.val(), true);
                    }
                    if(ev.key == 'Escape'){
                        ev.preventDefault();
                        dispose();
                    }
                });
                status.interval = setInterval(function(){
                    if(searchInput.val() != status.value){
                        status.value = searchInput.val();
                        update(searchInput.val());
                    }
                }, 500);
            }
        });
        textarea.keydown(function(ev) {
            if (ev.altKey && ev.key == 'm') {
                ev.preventDefault();
                button.click();
            }
        });
        return button;
    };
};

ecs.textarea.toolbarItems.versionHistory = function(label, url){
    return function(textarea) {
        return $('<a>', {
            title: label,
            'class': 'fa fa-2x fa-history text-primary',
            click: function(ev) {
                ev.preventDefault();
                ecs.fieldhistory.show(url);
            }
        });
    };
};