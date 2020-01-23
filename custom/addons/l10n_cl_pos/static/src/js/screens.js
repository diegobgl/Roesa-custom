odoo.define('l10n_pe_pos.screens', function (require) {
    "use strict";

    var devices = require('point_of_sale.devices');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var screens = require('point_of_sale.screens');
    var qweb = core.qweb;

    screens.ReceiptScreenWidget.include({
        click_next: function(){
            this._super();
            if (this.pos.config.default_partner) {
                var partner = this.pos.db.get_partner_by_id(this.pos.config.default_partner[0]);
                this.pos.get_order().set_client(partner);
            }
        }
    });

    screens.PaymentScreenWidget.include({
        init: function(parent, options) {
            this._super(parent, options);
            if (this.pos.config.default_partner) {
                var partner = this.pos.db.get_partner_by_id(this.pos.config.default_partner[0]);
                this.pos.get_order().set_client(partner);
            }
        },
        click_invoice_journal: function (journal_id) {
            var order = this.pos.get_order();
            order['invoice_journal_id'] = journal_id;
            $('.journal').removeClass('highlight');
            $('.journal').addClass('lowlight');
            var $journal_selected = $("[data-id='" + journal_id + "']");
            $journal_selected.addClass('highlight');
        },
        render_invoice_journals: function () {
            var self = this;
            var methods = $(qweb.render('journal_list', {widget: this}));
            methods.on('click', '.journal', function () {
                self.click_invoice_journal($(this).data('id'));
            });
            return methods;
        },
        renderElement: function () {
            this._super();
            if (this.pos.config.invoice_journal_ids && this.pos.config.invoice_journal_ids.length > 0 && this.pos.journals) {
                var methods = this.render_invoice_journals();
                methods.appendTo(this.$('.invoice_journals'));
            }
        }
    });

    screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if( mode === 'quantity'){
                    order.get_selected_orderline().set_quantity(val);
                }else if( mode === 'discount'){
                    order.get_selected_orderline().set_discount(val);
                }else if( mode === 'quantity-by-price'){
                    order.get_selected_orderline().set_quantity_by_amount(val/order.get_selected_orderline().get_unit_price());
                }else if( mode === 'price'){
                    var selected_orderline = order.get_selected_orderline();
                    selected_orderline.price_manually_set = true;
                    selected_orderline.set_unit_price(val);
                }
            }
        }
    });

    screens.ClientListScreenWidget.include({
        change_l10n_cl_document_number: function(l10n_cl_document_type, l10n_cl_document_number) {
            function get_partner_data(document_number) {
                var name = document.getElementsByClassName("name")[0],
                    region = document.getElementsByClassName("client-address-region")[0],
                    state = document.getElementsByClassName("client-address-state")[0],
                    city = document.getElementsByClassName("client-address-city")[0],
                    address = document.getElementsByClassName("client-address-street")[0],
                    phone = document.getElementsByClassName("client-phone")[0],
                    email = document.getElementsByClassName("client-email")[0];
                rpc.query({
                    model: 'res.partner',
                    method: 'get_l10n_cl_partner_data',
                    args: [String(document_number)]
                }).then(function (result) {
                    name.value = result.name || '';
                    region.value = result.l10n_cl_res_region_id;
                    state.value = result.state_id;
                    city.value = result.city_id;
                    address.value = result.street || '';
                    phone.value = result.phone || '';
                    email.value = result.email || '';
                    document.getElementById("loading").classList.add('hide');
                }).fail(function (error) {
                    document.getElementById("loading").classList.add('hide');
                    alert("RUT: " + document_number + " No exists!.");
                });
            }
            let document_type =  $(l10n_cl_document_type).children("option:selected").attr("code");
            if(document_type == 81) {
                document.getElementById("loading").classList.remove('hide');
                let d_number = l10n_cl_document_number.value;
                get_partner_data(d_number);
            }
        },
        change_l10n_cl_res_region: function(l10n_cl_res_region, states, cities){
            let self = this;
            let region = $(l10n_cl_res_region).children("option:selected").val();
            $(states).children('option').each(function(){
                if ($(this).attr("region") != region ){
                   $(this).addClass("hide");
                }
                else{
                    $(this).removeClass('hide');
                    $(this).attr("selected","selected");
                }
            });
           self.change_res_state(states, cities);
        },
        change_res_state: function(states, cities){
            let self = this;
            let state = $(states).children("option:selected").val();
            $(cities).children('option').each(function(){
                if ($(this).attr("state") != state ){
                   $(this).addClass("hide");
                   $(this).prop("selected", false);
                }
                else{
                    $(this).removeClass('hide');
                    $(this).attr("selected","selected");
                }
            });
        },
        display_client_details: function(visibility,partner,clickpos){
            this._super(visibility,partner,clickpos);
            if (visibility === 'edit') {
                var contents = this.$('.client-details-contents');

                var l10n_cl_res_region = contents[0].childNodes[0].querySelector('.l10n_cl_res_region');
                var states = contents[0].childNodes[0].querySelector('.state');
                var cities = contents[0].childNodes[0].querySelector('.city');
                var l10n_cl_document_type = contents[0].childNodes[0].querySelector('.l10n_cl_document_type');
                var l10n_cl_document_number = contents[0].childNodes[0].querySelector('.l10n_cl_document_number');

                l10n_cl_res_region.addEventListener("change", (function() {
                    this.change_l10n_cl_res_region(l10n_cl_res_region, states, cities);
                }.bind(this)));
                states.addEventListener("change", (function() {
                    this.change_res_state(states, cities);
                }.bind(this)));
                l10n_cl_document_number.addEventListener("change", (function() {
                    this.change_l10n_cl_document_number(l10n_cl_document_type, l10n_cl_document_number);
                }.bind(this)));
            }
        }
    });
});