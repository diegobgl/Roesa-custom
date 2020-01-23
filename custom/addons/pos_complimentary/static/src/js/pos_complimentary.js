odoo.define('pos_complimentary.complimentary', function (require) {
    "use strict";
    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var QWeb = core.qweb;
    models.load_fields("pos.config", "complimentary_using_pin");
    var _super_orderline = models.Orderline.prototype;
    screens.PaymentScreenWidget.include({
        finalize_validation:function () {
            var order = this.pos.get_order();
            order.set_price_zero_orderlines();
            this._super();
        }
    });
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function(){
            var json = _super_orderline.export_as_JSON.apply(this,arguments);
            json.is_free = this.is_free;
            return json;
        },
        init_from_JSON: function(json){
            _super_orderline.init_from_JSON.apply(this,arguments);
            this.is_free = json.is_free;
        },
        get_price_without_tax: function(){
            if(this.is_free){return 0.0}
            return _super_orderline.get_price_without_tax.apply(this,arguments);
        },
        get_price_with_tax: function(){
            if(this.is_free){return 0.0}
            return _super_orderline.get_price_with_tax.apply(this,arguments);
        },
        get_base_price: function(){
            if(this.is_free){return 0.0}
            return _super_orderline.get_base_price.apply(this,arguments);
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function(){
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.all_free = this.all_free;
            return json;
        },
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.all_free = json.all_free;
        },
        get_subtotal : function(){
            if(this.all_free){return 0.0}
            return _super_order.get_subtotal.apply(this,arguments);
        },
        get_total_with_tax: function() {
            if(this.all_free){return 0.0}
            return _super_order.get_total_with_tax.apply(this,arguments);
        },
        get_total_without_tax: function() {
            if(this.all_free){return 0.0}
            return _super_order.get_total_without_tax.apply(this,arguments);
        },
        set_price_zero_orderlines:function () {
            var self = this;
            var orderlines = this.get_orderlines();
            orderlines.forEach(function (line) {
                if(self.all_free || line.is_free){
                    line.price = 0;
                }
            });
        },
    });
    var ComplimentaryButton = screens.ActionButtonWidget.extend({
        'template': 'ComplimentaryButton',
        button_click: function(){
            var self = this;
            var order = this.pos.get_order();
            if(this.pos.config.complimentary_using_pin && !order.get_selected_orderline().is_free){
                this.gui.show_popup('pin_number',{
                    'title':  'Enter PIN Number',
                    'after_certain':function(){
                        self.action_complimentary();
                    },
                })
            }else{
                self.action_complimentary();
            }
        },
        action_complimentary: function () {
            var order = this.pos.get_order();
            var orderline = order.get_selected_orderline();
            if(!orderline)return;
            orderline.is_free = !orderline.is_free;
            orderline.trigger('change',orderline);
        }
    });
    var AllComplimentaryButton = screens.ActionButtonWidget.extend({
        'template': 'AllComplimentaryButton',
        button_click: function(){
            var self = this;
            var order = this.pos.get_order();
            if(this.pos.config.complimentary_using_pin && !order.all_free){
                this.gui.show_popup('pin_number',{
                    'title':  'Enter PIN Number',
                    'after_certain':function(){
                        self.action_compilemtary_all();
                    },
                })
            }else{
                self.action_compilemtary_all();
            }
        },
        action_compilemtary_all:function () {
            var order = this.pos.get_order();
            order.all_free = !order.all_free;
            order.trigger('change',order);
            this.$el.toggleClass('active');
        }
    });

    screens.define_action_button({
        'name': 'button_complimentary',
        'widget': ComplimentaryButton,
    });
    screens.define_action_button({
        'name': 'button_all_complimentary',
        'widget': AllComplimentaryButton,
    });

    screens.OrderWidget.include({
        change_selected_order:function () {
            var order = this.pos.get_order();
            if(order){
                if(order.all_free===true){
                    this.gui.screen_instances.products.$('.btn.complimentary-all').addClass('active');
                }else{
                    this.gui.screen_instances.products.$('.btn.complimentary-all').removeClass('active');
                }
            }
            this._super();
        }
    });
    return {
        ComplimentaryButton: ComplimentaryButton,
        AllComplimentaryButton:AllComplimentaryButton,
    };
    
});
    