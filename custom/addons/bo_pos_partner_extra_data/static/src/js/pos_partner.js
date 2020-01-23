odoo.define('bo_pos_partner_extra_data.pos_partner', function (require) {
"use strict";

var models = require('point_of_sale.models');
var core = require('web.core');
var _t = core._t;

var PosModelSuper = models.PosModel;

models.load_fields("res.partner", ["birthdate", "occupation", "gender", "ref"]);

models.PosModel = models.PosModel.extend({
    initialize: function(session, attributes) {
        var res = PosModelSuper.prototype.initialize.apply(this, arguments);
        this.genders = [{'gender': 'male', 'name': _t('Male')}, {'code': 'female', 'name': _t('Female')}];
        return res;
    },
});

});
