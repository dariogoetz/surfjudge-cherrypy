/* =========================================================
 * heat_order.js
 * =========================================================
 * Copyright 2016 Dario Goetz
 * ========================================================= */

var HeatOrder = function(element, options){
    this.element = $(element);

    if (typeof options === 'undefined')
        options = {};

    this.tournament_id = options['id'];

    this.heat_list_element = null;

    this.initialized = this.init();
}

HeatOrder.prototype.constructor = HeatOrder;

HeatOrder.prototype.init = function(){
    this.init_html();

    this.register_events();
    var done = this.refresh_from_server();
    return done;
}


HeatOrder.prototype.destroy = function(){
    this.unregister_events();
    this.heat_list_element.remove();
}

HeatOrder.prototype.register_events = function(){
    // register events on elements of this module here
    // they should call methods of this class and not contain too much logic themselves
    // this.heat_list_element.on('click', '.heat_button', function(){});
}


HeatOrder.prototype.unregister_events = function(){
    // unregister events registered above
    //this.heat_list_element.off('click', '.heat_button');
}

HeatOrder.prototype.init_html = function(){
    var _this = this;
    html = [
        '<div>',
        'put',
        'your',
        'html code',
        'here',
        '</div>'
    ].join(' ');

    // add html to given element in web page
    this.element.append(html);

    // potentially initialize javascript objects, e.g. bootstraptables, here
}


HeatOrder.prototype.refresh_from_server = function(no_trigger){
    var _this = this;
    var done = $.Deferred();
    // retrieve heat order data from server and fill html elements in this.heat_order_list
    // if asynchronous code is performed here, call done.resolve() after finish
    return done.promise();
}



// add functionality to jquery ($.fn)
$.fn.heat_order = function(option, val){
    var $this = $(this);
    var data = $this.data('heat');
    var options = typeof option === 'object' && option;
    if (!data){
        $this.data('heat_order', new HeatOrder(this, $.extend({}, options)));
        return $this.data('heat_order');
    }
    if (option == 'destroy'){
        data['destroy']();
        $this.data('heat_order', null);
        return;
    }
    if (typeof option === 'string'){
        return data[option].apply(data, [].slice.call(arguments,1));//(val);
    }
    return $this.data('heat_order');
};

$.fn.heat_order.Constructor = HeatOrder;
