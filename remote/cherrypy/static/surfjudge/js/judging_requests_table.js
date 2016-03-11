

var JudgingRequests = function(element, options){
    this.element = $(element);
    this.heat_id = options.heat_id;
    this.judging_requests = [];

    this.init();
}

JudgingRequests.prototype.constructor = JudgingRequests;

JudgingRequests.prototype.init = function(){

    this.element.find('.judging_requests_table').bootstrapTable({
        rowStyle: function rowStyle(row, index){
            if (row['status'] === 'confirmed')
                return {classes: 'confirmed'};
            else if (row['status'] === 'missing')
                return {classes: 'missing'};
            else
                return {classes: 'pending'}
        }
    });
    this.register_events();
    this.refresh_from_server();
}

JudgingRequests.prototype.register_events = function(){
    var _this = this;
    this.element.find('.judging_requests_table').on('click', '.missing a', function(){
        _this.delete_judge_activity($(this).data('judgeid'));
    });
    this.element.find('.judging_requests_table').on('click', '.confirmed a', function(){
        _this.delete_judge_activity($(this).data('judgeid'));
    });
    this.element.find('.judging_requests_table').on('click', '.pending a', function(){
        _this.confirm_judge_activity($(this).data('judgeid'));
    });

}

JudgingRequests.prototype.get_data_from_server = function(){
    var _this = this;
    this.judging_requests = [];
    var deferred_judging_requests = $.getJSON('/do_get_judging_requests', {heat_id: _this.heat_id});
    return $.when(deferred_judging_requests).done(function(ev_judging_requests){
        var data = ev_judging_requests;
        for (var idx in data){
            var param_str = data[idx]['heat_id'] + ',' + data[idx]['judge_id'];
            data[idx]['action'] = '';
            if (data[idx]['status']==='pending'){
                data[idx]['action'] ='<a href="#" data-judgeid=' + data[idx]['judge_id'] + '><button class="btn btn-success"><span class="glyphicon glyphicon-ok"></span></button></a>';
            } else if (data[idx]['status'] === 'confirmed') {
                data[idx]['action'] ='<a href="#" data-judgeid=' + data[idx]['judge_id'] + '><button class="btn btn-default"><span class="glyphicon glyphicon-remove"></span></button></a>';
            } else if (data[idx]['status'] === 'missing') {
                data[idx]['action'] ='<a href="#" data-judgeid=' + data[idx]['judge_id'] + '><button class="btn btn-danger"><span class="glyphicon glyphicon-remove"></span></button></a>';
            }
        }
        _this.judging_requests = data;
    });
}

JudgingRequests.prototype.refresh_from_server = function(){
    var _this = this;
    this.get_data_from_server().done(function(){
        _this.refresh_judging_requests_table();
    });
}


JudgingRequests.prototype.refresh_judging_requests_table = function(){
    var _this = this;

    _this.element.find('.judging_requests_table').bootstrapTable('load', this.judging_requests);
}


JudgingRequests.prototype.confirm_judge_activity = function(judge_id){
    var _this = this;
    $.get('tournament_admin/do_set_active_judges', {heat_id: _this.heat_id, judge_ids: JSON.stringify([judge_id]), append: true}, function(){
        _this.refresh_from_server();
     });
}


JudgingRequests.prototype.delete_judge_activity = function(judge_id){
    var _this = this;
     $.get('tournament_admin/do_delete_active_judge', {heat_id: _this.heat_id, judge_id: judge_id}, function(){
         _this.refresh_from_server();
     });
 }




// add functionality to jquery ($.fn)
// if option is an object, this means, that a new JudgingRequests object is generated and put to the elements "data"
// if it is a string, a function of the JudgingRequests object is called
$.fn.judging_requests = function(option, val){
    var $this = $(this);
    var data = $this.data('judging_requests');
    var options = typeof option === 'object' && option;
    if (!data)
        $this.data('judging_requests', new JudgingRequests(this, $.extend({}, options)));
    if (typeof option === 'string')
        data[option].apply($this.data('heat'), [].slice.call(arguments,1));//(val);
};

$.fn.judging_requests.Constructor = JudgingRequests;
