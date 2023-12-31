ecs.TabbedForm = function(form, tabController, autosaveInterval) {
    this.form = $(form);
    this.autosaveDisabled = false;
    this.autosave_xhr = null;

    tabController.tabs.forEach(function(tab) {
        if (tab.panel.find('.has-danger, .alert.alert-danger').length) {
            tab.setErrorState();
            tab.group.header.addClass('bg-danger');
        }
    });

    this.lastSaveData = this.form.serialize();
    if (autosaveInterval) {
        setInterval(this.autosave.bind(this), autosaveInterval * 1000);
        $(window).on('unload', this.autosave.bind(this));
    }
};
ecs.TabbedForm.prototype = {
    _save: function(extraParameter) {
        var currentData = this.form.serialize();
        this.lastSaveData = currentData;

        $('.last_save').html('<span class="fa fa-spinner fa-spin"></span>');
        this.autosave_xhr = $.post({
            url: window.location.href,
            data: currentData + '&' + extraParameter + '=' + extraParameter,
            success: function() {
                var now = new Date();
                $('.last_save').text(
                    'Last save: ' +
                    ('0' + now.getHours()).slice(-2) + ':' +
                    ('0' + now.getMinutes()).slice(-2)
                );
            },
            error: function() {
                $('.last_save').html(
                    '<span class="text-danger fa fa-exclamation-triangle"></span>'
                );
            },
            complete: (function() {
                this.autosave_xhr = null;
            }).bind(this)
        });
    },
    save: function() {
        this._save('save');
    },
    autosave: function() {
        if (this.autosaveDisabled || this.autosave_xhr ||
            this.lastSaveData == this.form.serialize())
            return;

        this._save('autosave');
    },
    toggleAutosave: function(state) {
        this.autosaveDisabled = !state;
        if (!state && this.autosave_xhr)
            this.autosave_xhr.abort();
    },
    submit: function(name) {
        this.toggleAutosave(false);
        if (!name)
            return this.form.submit();
        this.form.find('input[type=submit][name=' + name + ']').click();
    }
};

//-----------------------------------new-------------------------
// class TabbedForm {
//     constructor(form, tabController, autosaveInterval) {
//         this.form = $(form);
//         this.autosaveDisabled = false;
//         this.autosave_xhr = null;

//         tabController.tabs.forEach(tab => {
//             if (tab.panel.find('.has-danger, .alert.alert-danger').length) {
//                 tab.setErrorState();
//                 tab.group.header.addClass('bg-danger');
//             }
//         });

//         this.lastSaveData = this.form.serialize();
//         if (autosaveInterval) {
//             setInterval(() => this.autosave(), autosaveInterval * 1000);
//             $(window).on('unload', () => this.autosave());
//         }
//     }

//     _save(extraParameter) {
//         const currentData = this.form.serialize();
//         this.lastSaveData = currentData;

//         $('.last_save').html('<span class="fa fa-spinner fa-spin"></span>');
//         this.autosave_xhr = $.post({
//             url: window.location.href,
//             data: `${currentData}&${extraParameter}=${extraParameter}`,
//             success: () => {
//                 const now = new Date();
//                 $('.last_save').text(
//                     `Last save: ${('0' + now.getHours()).slice(-2)}:${('0' + now.getMinutes()).slice(-2)}`
//                 );
//             },
//             error: () => {
//                 $('.last_save').html(
//                     '<span class="text-danger fa fa-exclamation-triangle"></span>'
//                 );
//             },
//             complete: () => {
//                 this.autosave_xhr = null;
//             }
//         });
//     }

//     save() {
//         this._save('save');
//     }

//     autosave() {
//         if (this.autosaveDisabled || this.autosave_xhr || this.lastSaveData == this.form.serialize())
//             return;

//         this._save('autosave');
//     }

//     toggleAutosave(state) {
//         this.autosaveDisabled = !state;
//         if (!state && this.autosave_xhr)
//             this.autosave_xhr.abort();
//     }

//     submit(name) {
//         this.toggleAutosave(false);
//         if (!name)
//             return this.form.submit();
//         this.form.find(`input[type=submit][name=${name}]`).click();
//     }
// }
