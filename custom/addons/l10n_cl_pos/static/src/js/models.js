odoo.define('l10n_pe_pos.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var qweb = core.qweb;

    var _super_Order = models.Order.prototype;
    var _super_PosModel = models.PosModel.prototype;

    models.load_fields('res.company', ['street', 'city', 'state_id', 'zip']);
    models.load_fields('res.partner', ['name','street','city_id','state_id','country_id','vat', 'phone','zip','mobile','email','barcode','write_date',
        'property_account_position_id','property_product_pricelist', 'l10n_cl_res_region_id', 'l10n_cl_document_type_id', 'l10n_cl_document_number']);
    models.load_fields('account.journal', ['type', 'sequence', 'l10n_cl_document_type_id', 'l10n_cl_sii_code']);

    models.load_models([{
        model:  'l10n_cl.res.region',
        fields: ['name', 'code', 'country_id'],
        domain: function(self){ return [['country_id','=',self.company.country_id[0]]]; },
        loaded: function(self, regions){
            self.regions = regions;
        },
    },{
        model:  'res.country.state',
        fields: ['name', 'code', 'country_id', 'l10n_cl_region_id'],
        domain: function(self){ return [['country_id','=',self.company.country_id[0]]]; },
        loaded: function(self, states){
            self.states = states;
        },
    },{
        model:  'res.city',
        fields: ['name', 'zipcode', 'state_id'],
        loaded: function(self, cities){
            self.cities = cities;
        },
    },{
        model: 'account.journal',
        fields: [],
        domain: function (self) {
            return [['id', 'in', self.config.invoice_journal_ids]];
        },
        loaded: function (self, journals) {
            self.journals = journals;
            self.journal_by_id = {};
            for (var i = 0; i < journals.length; i++) {
                self.journal_by_id[journals[i]['id']] = journals[i];
            }
        }
    },{
        model: 'l10n_cl.sii.data',
        fields: ['name', 'code', 'sii_code'],
        domain: [['table_code', '=', 'sii_table_01']],
        loaded: function (self, partner_document_types) {
            self.partner_document_types = partner_document_types;
        }
    }
    ]);

    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            _super_Order.initialize.apply(this, arguments);
            if (this.pos.config.pos_auto_invoice) {
                this.to_invoice = true;
            }
        },
        init_from_JSON: function (json) {
            var res = _super_Order.init_from_JSON.apply(this, arguments);
            if (json.to_invoice) {
                this.to_invoice = json.to_invoice;
            }
            if (json.invoice_journal_id) {
                this.invoice_journal_id = json.invoice_journal_id;
            }
            return res;
        },
        export_as_JSON: function () {
            var json = _super_Order.export_as_JSON.apply(this, arguments);
            if (this.invoice_journal_id) {
                json.invoice_journal_id = this.invoice_journal_id;
            }
            return json;
        }
    });

    models.Orderline = models.Orderline.extend({
        set_quantity_by_amount: function (amount) {
            this.set_quantity(amount);
            this.trigger('change',this);
        }
    });

    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function (model) {
                return model.model === 'res.partner';
            });
            partner_model.fields.push('vat');
            _super_PosModel.initialize.apply(this, arguments);
        },
        push_and_invoice_pos_order: function (order) {
            var self = this;
            var invoiced = new $.Deferred();

            if (!order.get_client()) {
                invoiced.reject({code: 400, message: 'Missing Customer', data: {}});
                return invoiced;
            }
            var order_id = this.db.add_order(order.export_as_JSON());
            this.flush_mutex.exec(function () {
                var done = new $.Deferred(); // holds the mutex
                var transfer = self._flush_orders([self.db.get_order(order_id)], {timeout: 30000, to_invoice: true});
                transfer.fail(function (error) {
                    invoiced.reject(error);
                    done.reject();
                });
                transfer.pipe(function (order_server_id) {
                    invoiced.resolve();
                    done.resolve();
                });
                return done;
            });
            return invoiced;
        },
        set_state_by_regions: function(states){
            this.state_by_regions  = states;
        },
        push_and_invoice_order: function () {
            var self = this;
            return self.push_and_invoice_pos_order.apply(this, arguments).then(function () {
                var order = self.get_order();
                self.order = order;
                if (order.is_to_invoice()) {
                    return rpc.query({
                        model: 'pos.order',
                        method: 'search_read',
                        domain: [['pos_reference', '=', order['name']]],
                        fields: ['invoice_id'],
                    }).then(function (orders) {
                        if (orders.length >= 1) {
                            var invoice = orders[0]['invoice_id'];
                            return rpc.query({
                                model: 'account.invoice',
                                method: 'search_read',
                                domain: [['id', '=', invoice[0]]],
                                fields: ['number', 'journal_id'],
                            }).then(function (invoices) {
                                if (invoices.length >= 1) {
                                    self.order.invoice_number = invoices[0]['number'];
                                    return rpc.query({
                                        model: 'account.journal',
                                        method: 'search_read',
                                        domain: [['id', '=', invoices[0]['journal_id'][0]]],
                                        fields: ['l10n_cl_sii_code', 'name'],
                                    }).then(function (journals) {
                                        self.order.l10n_cl_sii_code = journals[0]['l10n_cl_sii_code'];
                                        self.order.journal_name = journals[0]['name']
                                    }).fail(function (error) {
                                    })
                                }
                            }).fail(function (error) {
                                console.log(error);
                            })
                        }
                    }).fail(function (error) {
                        console.log(error);
                    })
                }
            });
        }
    });
});