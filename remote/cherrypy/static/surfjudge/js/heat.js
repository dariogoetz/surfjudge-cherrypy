/* =========================================================
 * heat.js
 * =========================================================
 * Copyright 2016 Dario Goetz
 * ========================================================= */

var Heat = function(element, options){
    this.element = $(element);
    this.surfers_modal = $(options['surfers_modal']);

    if (typeof options === 'undefined')
        options = {};

    this.heat_id = options['id'];
    this.heat_data = options;

    this.heat_data['heat_id'] = options['id'];
    this.heat_data['heat_name'] = options['name'];

    this.surfers = [];

    this.participants = {};
    this.proposed_participants = {};
    this.advancement_rules = {};
    this.init();
}

Heat.prototype.constructor = Heat;

Heat.prototype.init = function(){
    if (this.heat_data['number_of_waves'] == '')
        this.heat_data['number_of_waves'] = 10;
    if (this.heat_data['duration'] == '')
        this.heat_data['duration'] = 15;
    this.element.find('.participants_table').bootstrapTable({'rowStyle': function rowStyle(row, index){
        var res = {};
        if (row['type'] == 'proposal')
            res['classes'] = 'proposal';
        else if (row['type'] == 'rule')
            res['classes'] = 'rule';
        return res;
    }});
    this.surfers_modal.find('.surfers_table').bootstrapTable();

    this.element.find('.plusminusinput').plusminusinput();

    this.register_events();
    this.refresh_from_server();
}


Heat.prototype.destroy = function(){
    this.unregister_events();

    this.element.find('.plusminusinput').plusminusinput('destroy');
    this.element.find('.participants_table').bootstrapTable('destroy');
    this.surfers_modal.find('.surfers_table').bootstrapTable('destroy');
}

Heat.prototype.register_events = function(){
    var _this = this;
    // click on confirm button for pending participant row
    this.element.on('click', '.participants_table .remove_pending_btn', function(){
        _this.remove_pending($(this).data('seed'))
    });


    this.element.on('click', '.participants_table .remove_participant_btn', function(){
        _this.remove_participant($(this).data('seed'));
    });


    this.element.on('click', '.participants_table .edit_participant_btn', function(){
        _this.refresh_surfers_table();
        _this.surfers_modal.data('seed', $(this).data('seed'));
        _this.surfers_modal.modal('toggle');
    });


    this.element.on('click', '.add_participant_btn', function(){
        _this.refresh_surfers_table();
        _this.surfers_modal.data('seed', 'new');
        _this.surfers_modal.modal('toggle');
    });



    this.surfers_modal.find('.surfers_table').on('click-row.bs.table', function(e, row, $element){
        _this.surfers_modal.data('participant', row);
        if (_this.surfers_modal.data('selected_element') != null)
            _this.surfers_modal.data('selected_element').children().removeClass('selected');
        _this.surfers_modal.data('selected_element', $element);
        $element.children().addClass('selected');
    });


    // click on "save" in surfers_modal to select participants
    this.surfers_modal.on('click', '.participant_submit', function(){
        if (_this.surfers_modal.data('participant') != null){
            _this.set_participant(_this.surfers_modal.data('seed'), _this.surfers_modal.data('participant'));
            _this.surfers_modal.data('seed', null);
            _this.surfers_modal.data('participant', null);
            _this.surfers_modal.data('selected_element', null)
        }
        else
            console.log('nothing to submit');
    });

}

Heat.prototype.unregister_events = function(){
    this.element.off('click', '.participants_table .remove_pending_btn');
    this.element.off('click', '.participants_table .edit_participant_btn');
    this.element.off('click', '.participants_table .remove_participant_btn');
    this.element.off('click', '.add_participant_btn');

    this.surfers_modal.off('click', '.participant_submit');
    this.surfers_modal.find('.surfers_table').off('click-row.bs.table');
}


Heat.prototype.refresh_from_server = function(){
    var _this = this;
    this.get_data_from_server().done(function(){
        _this.refresh_surfers_table();
        _this.refresh_participants_table();
        $(_this.element).trigger('refreshed');
    });
}

Heat.prototype.get_data_from_server = function(){
    this.surfers = {};
    this.participants = {};
    this.proposed_participants = {};
    this.advancement_rules = {};
    this.colors = {};
    var deferred_rules = $.getJSON('/tournament_admin/do_get_advancement_rules', {heat_id: this.heat_id});
    var deferred_surfers = $.getJSON('/tournament_admin/do_get_surfers');
    var deferred_participants = $.getJSON('/headjudge/do_get_participating_surfers', {heat_id: this.heat_id});
    var deferred_proposals = $.getJSON('/tournament_admin/do_get_advancing_surfers', {heat_id: this.heat_id});
    var deferred_colors = $.getJSON('/tournament_admin/do_get_lycra_colors');

    var _this = this;

    return $.when(deferred_surfers, deferred_participants, deferred_proposals, deferred_colors, deferred_rules).done(function(ev_surfers, ev_participants, ev_proposals, ev_colors, ev_rules){
        _this.surfers = ev_surfers[0];
        for (var idx=0; idx < ev_participants[0].length; idx++)
            _this.participants[ev_participants[0][idx]['seed']] = ev_participants[0][idx];
        for (var idx=0; idx < ev_proposals[0].length; idx++)
            _this.proposed_participants[ev_proposals[0][idx]['seed']] = ev_proposals[0][idx];
        _this.advancement_rules = ev_rules[0];
        _this.colors = ev_colors[0];
    });
}

Heat.prototype.refresh_surfers_table = function(){
    this.surfers_modal.data('participant', null);
    this.surfers_modal.find('.surfers_table').bootstrapTable('load', this.get_nonparticipating_surfers());
}

Heat.prototype._get_combined_participants = function(){
    var participants = {};
    for (idx in this.advancement_rules){
        var participant = this.advancement_rules[idx];
        var p = {};
        $.extend(p, participant);
        p['type'] = 'rule';
        p['surfer_color'] = this.colors[p['seed'] % this.colors.length];
        participants[participant['seed']] = p;
    }
    for (idx in this.proposed_participants){
        var participant = this.proposed_participants[idx];
        var p = {};
        $.extend(p, participant);
        p['type'] = 'proposal';
        p['surfer_color'] = this.colors[p['seed'] % this.colors.length];
        participants[participant['seed']] = p;
    }
    for (idx in this.participants){
        var participant = this.participants[idx];
        var p = {};
        $.extend(p, participant);
        p['type'] = 'participant';
        participants[participant['seed']] = p;
    }
    return participants;
}

Heat.prototype.refresh_participants_table = function(){
    var res = [];
    var max_seed = -1;
    var participants = this._get_combined_participants();
    for (idx in participants){
        var participant = participants[idx];
        if (participant['seed'] > max_seed){
            max_seed = participant['seed'];
        }
    }

    for (var seed = 0; seed <= max_seed; seed++){
        var type = 'empty';
        var p = {};
        if (participants[seed] == null){
            p['name'] = '-- empty slot --';
            p['seed'] = seed;
            p['surfer_color'] = null;
        } else
        {
            p = participants[seed];
            type = p['type'];
        }
        res.push(this._add_interactive_fields(p, type));
    }
    this.element.find('.participants_table').bootstrapTable('load', res);
}

Heat.prototype._add_interactive_fields = function(participant, type){
    var s = '<select class="form-control"  data-seed="' + participant['seed'] + '">';
    for (var val in this.colors) {
        var sel = '';
        if (participant['surfer_color'] === this.colors[val])
            sel = 'selected=selected';
        s = s + '<option ' + sel + ' value="' + this.colors[val] + '">' + this.colors[val] + '</option>';
    }
    s = s + '</select>';

    var action_field = '';
    if (type == 'proposal'){
        action_field = '<button data-seed=' + participant['seed'] + ' class="btn btn-success remove_pending_btn"><span class="glyphicon glyphicon-ok"></span></button>';
    } else if (type == 'participant') {
        action_field = '<button data-seed=' + participant['seed'] + ' class="btn btn-danger remove_participant_btn"><span class="glyphicon glyphicon-remove"></span></button>';
    } else if (type == 'rule') {
        action_field = '';
    } else {
        action_field = '';
    }
    var edit_field = '&nbsp; <button data-seed=' + participant['seed'] + ' class="btn btn-info edit_participant_btn"><span class="glyphicon glyphicon-edit"></span></button>';

    var res = $.extend({}, participant);
    res['color'] = s;
    res['action'] = action_field + edit_field;
    return res;
}

Heat.prototype.get_nonparticipating_surfers = function(){
    var surfers = [];
    var p_set = new Set();
    for (var idx in this.participants){
        p_set.add(this.participants[idx]['surfer_id']);
    }
    for (idx=0; idx < this.surfers.length; idx++){
        if (!p_set.has(this.surfers[idx]['id']))
            surfers.push(this.surfers[idx]);
    }
    return surfers;
}

Heat.prototype.remove_participant = function(seed){
    delete this.participants[seed];
    this.refresh_participants_table();
    this.refresh_surfers_table();
}

Heat.prototype.confirm_participant = function(seed){
    this.participants[seed] = $.extend({}, this.proposed_participants[seed])
    delete this.participants[seed]['proposal'];
}

Heat.prototype.set_participant = function(seed, data){
    var participants = this._get_combined_participants();
    var new_seed = -1;
    if (seed == 'new'){
        var max_existing_seed = -1;
        for (seed in participants)
            max_existing_seed = Math.max(max_existing_seed, participants[seed]['seed']);
        new_seed = max_existing_seed + 1;
    }
    else
        new_seed = parseInt(seed);

    var existing_participant = this.participants[new_seed];
    this.participants[new_seed] = data;
    if (existing_participant){
        this.participants[new_seed]['surfer_color'] = existing_participant['surfer_color'];
    }
    else {
        var color = this.colors[new_seed % this.colors.length];
        if (color)
            this.participants[new_seed]['surfer_color'] = color;
    }
    this.participants[new_seed]['seed'] = new_seed;
    this.participants[new_seed]['surfer_id'] = this.participants[new_seed]['id'];
    this.participants[new_seed]['heat_id'] = this.heat_id;
    this.refresh_surfers_table();
    this.refresh_participants_table();
}


Heat.prototype.fetch_heat_details_from_inputs = function(){
    var _this = this;
    this.element.find('.heat_input').each(function(idx, elem){
        _this.heat_data[$(this).data('key')] = $(this).val();
    });

    if (this.heat_data['number_of_waves'] === '')
        this.heat_data['number_of_waves'] = 10;
}

Heat.prototype.check_data = function(){

    if (this.heat_id == null && this.heat_data['heat_name'].length == 0) {
        alert('Empty field "Heat Name"');
        return false;
    };

    var colors = new Set();
    var ids = new Set();
    for (seed in this.participants){
        var color = this.participants[seed]['surfer_color'];
        if (colors.has(color)){
            alert('Double entries for "Surfer Color"');
            return false;
        }
        colors.add(color);

        var id = this.participants[seed]['surfer_id'];
        if (ids.has(id)){
            alert('Surfer entered twice');
            return false;
        }
        ids.add(id);
    }
    return true;
}

Heat.prototype.fetch_surfer_colors = function(){
    var _this = this;

    this.element.find('.participants_table select option:selected').each(function(){
        var seed = parseInt($(this).parent().data('seed'));
        if (_this.participants[seed]){
            _this.participants[seed]['surfer_color'] = $(this).val();
        }
    });
}

Heat.prototype.get_available_color = function(){
    this.fetch_surfer_colors();
    var taken_colors = new Set();
    for (seed in this.participants){
        var color = this.participants[seed]['surfer_color'];
        taken_colors.add(color);
    }
    for (idx = 0; idx < this.colors.length; idx++){
        var color = this.colors[idx];
        if (! taken_colors.has(color))
            return color;
    }
    return null;
}

Heat.prototype.upload_data = function(){
    var _this = this;
    this.fetch_heat_details_from_inputs();
    this.fetch_surfer_colors();
    var okay = this.check_data();
    if (!okay){
        return;
    }

    var heat_data = this.heat_data;
    var plist = [];
    for (var idx in this.participants){
        plist.push(this.participants[idx]);
    }
    var participants = JSON.stringify(plist);

    console.log('uploading');

    var deferred_heat_data = $.post('/tournament_admin/do_edit_heat', heat_data);
    var deferred_participants = $.post('/tournament_admin/do_set_participating_surfers', {heat_id: this.heat_id, participants: participants});

    var jqxhr = $.when(deferred_heat_data, deferred_participants);
    jqxhr.done(function(ev_heat_data, ev_part){
        _this.heat_id = ev_heat_data[0];
        _this.refresh_from_server();
    });
    return jqxhr;
}

Heat.prototype.fill_heat_inputs = function(){
    var _this = this;

    this.element.find('.heat_input').each(function(idx, elem){
        var key = $(this).data('key');
        if (key == 'date'){
            $(this).parent().data('datepicker').setValue(_this.heat_data['date'] || '');
        }
        else if (key == 'start_time'){
            var val = _this.heat_data['start_time'];
            if (val != null)
                $(this).timepicker('setTime', val);
        } else
            $(this).val(_this.heat_data[key]);
    });

    this.refresh_participants_table();
}

Heat.prototype.remove_pending = function(seed){
    this.confirm_participant(seed);
    this.refresh_participants_table();
}

Heat.prototype.delete_heat = function(){
    $.post('/tournament_admin/do_delete_heat', {id: this.heat_id});
}



// add functionality to jquery ($.fn)
// if option is an object, this means, that a new JudgingRequests object is generated and put to the elements "data"
// if it is a string, a function of the JudgingRequests object is called
$.fn.heat = function(option, val){
    var $this = $(this);
    var data = $this.data('heat');
    var options = typeof option === 'object' && option;
    if (!data){
        $this.data('heat', new Heat(this, $.extend({}, options)));
        return;
    }

    if (option == 'destroy'){
        data['destroy']();
        $this.data('heat', null);
        return;
    }
    if (typeof option === 'string'){
        return data[option].apply(data, [].slice.call(arguments,1));//(val);
    }
    return $this.data('heat');
};

$.fn.heat.Constructor = Heat;
