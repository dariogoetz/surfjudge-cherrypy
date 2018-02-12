

var SelectDropdown = function(element, ops){
    this.element = $(element);
    this.initialized = $.Deferred();

    var options = $.extend({}, this.element.data());
    options = $.extend(options, ops);

    if (options['requires_payload'])
        this.requires_payload = true;
    else
        this.requires_payload = false;

    if (options['update_label'] != null && !options['update_label'])
        this.update_label = false;
    else
        this.update_label = true;

    if (options['remove_selected'])
        this.remove_selected = true;
    else
        this.remove_selected = false;

    this.label = options['label'];
    if (this.label == null)
        this.label = this.element.find('.dropdown_label').html();

    this.server_call = options['url'];

    this.action_callback = options['action_callback'];

    this.selected_value = null;
    this.list_items = [];

    this.init();

    var _this = this;
    if (options['remove_elements'] != null){
        this.initialized.done(function(){_this.remove_elements(options['remove_elements']);});
    }
}

SelectDropdown.prototype.constructor = SelectDropdown;


SelectDropdown.prototype.init = function(){
    this.refresh_from_server();
    this.register_events();
}

SelectDropdown.prototype.destroy = function(){
    this.unregister_events();
}

SelectDropdown.prototype.register_events = function(){
    var _this = this;
    this.element.on('click', '.select', function(e){
        _this.select_item(this);
 });
}

SelectDropdown.prototype.unregister_events = function(){
    this.element.off('click', '.select');
}

SelectDropdown.prototype.refresh_from_server = function(payload){
    if (this.server_call == null){
        console.log('Error in select_dropdown.js: No URL provided');
        return;
    }
    if (this.requires_payload && payload == null)
        return;
    if (payload == null)
        payload = {};
    var _this = this;
    // fill dropdown with item names
    $.get(this.server_call, payload, function(data){
        var list_items = JSON.parse(data);
        // sort
        function comp_func(a,b){
            return (b['start_datetime'] < a['start_datetime']) ? 1 : -1;
        }
        list_items.sort(comp_func);

        _this.list_items = list_items;
        _this.refresh_list();
        _this.initialized.resolve();
     });
    this.element.find('.dropdown_label').html(_this.label);
    this.selected_value = null;
};

SelectDropdown.prototype.refresh_list = function(){
    // fill dropdown list with sorted item names
    var l = this.element.find('.dropdown-menu');
    l.empty();
    for (var i=0; i<this.list_items.length; i++){
        l.append('<li><a class="select" href="#" data-index=' + i + '>' + this.list_items[i]['name'] + '</a></li>');
    };
}

SelectDropdown.prototype.select_item = function(elem){
    var idx = $(elem).data('index');
    var val = this.list_items[idx]['id'];
    var label = this.list_items[idx]['name'];
    if (this.update_label)
        this.element.find('.dropdown_label').html(this.label + ' <b>' + label + '</b>');
    if (this.remove_selected)
        this.list_items.splice(idx,1);
    this.selected_value = val;
    this.refresh_list();
    this.action_callback(this.selected_value);
}

SelectDropdown.prototype.get_selected_value = function(){
    return this.selected_value;
}

SelectDropdown.prototype.remove_elements = function(filter){
    var new_list_items = [];
    for (var idx=0; idx<this.list_items.length; idx++){
        if (!filter(this.list_items[idx]))
            new_list_items.push(this.list_items[idx]);
    }
    this.list_items = new_list_items;
    this.refresh_list();
}


// add functionality to jquery ($.fn)
$.fn.select_dropdown = function(option, val){
    var $this = $(this);
    var data = $this.data('select_dropdown');
    var options = typeof option === 'object' && option;
    if (!data){
        $this.data('select_dropdown', new SelectDropdown(this, $.extend({}, options)));
        return;
    }

    if (option == 'destroy'){
        data['destroy']();
        $this.data('select_dropdown', null);
        return;
    }
    if (typeof option === 'string'){
        return data[option].apply(data, [].slice.call(arguments,1));//(val);
    }
    return $this.data('select_dropdown');
};

$.fn.select_dropdown.Constructor = SelectDropdown;
