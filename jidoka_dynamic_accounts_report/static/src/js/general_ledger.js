odoo.define('jidoka_dynamic_accounts_report.general_ledger', function (require) {
    'use strict';
    var GeneralLedger = require("dynamic_cash_flow_statements.general_ledger");
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var _t = core._t;

    window.click_num = 0;
    var GeneralLedgerCustom = GeneralLedger.include({
        start: function() {
            var self = this;
            self.initial_render = false;
            if (this.searchModel.config.domain.length != 0) {
                var searchModeDomain = this.searchModel.config.domain;
                var filter_data_selected = {};
                // CEK DOMAIN
                if (searchModeDomain[0][2] !== ''){
                    filter_data_selected.account_ids = [searchModeDomain[0][2]] 
                }
                if (searchModeDomain[1][2] !== '') {
                    var dateString = searchModeDomain[1][2];
                    filter_data_selected.date_from = dateString;
                }
                if (searchModeDomain[2][2] !== '') {
                    var dateString = searchModeDomain[2][2];
                    filter_data_selected.date_to = dateString;
                }
                if (searchModeDomain[3][2] !== '' && typeof(searchModeDomain[3][2]) === 'string') {
                    filter_data_selected.target_move = searchModeDomain[3][2].toLowerCase();
                }
                rpc.query({
                    model: 'account.general.ledger',
                    method: 'create',
                    args: [filter_data_selected]
                }).then(function(t_res) {
                    self.wizard_id = t_res;
                    self.load_data(self.initial_render);
                })
            }else{
            rpc.query({
                    model: 'account.general.ledger',
                    method: 'create',
                    args: [{

                    }]
                }).then(function(t_res) {
                    self.wizard_id = t_res;
                    self.load_data(self.initial_render);
                })
            }
        },
        
        load_data: function (initial_render = true) {
            var self = this;
            self.$(".categ").empty();
            try {
                var self = this;
                var action_title = self._title
                self._rpc({
                    model: 'account.general.ledger',
                    method: 'view_report',
                    args: [[this.wizard_id], action_title],
                }).then(function(datas) {
                    // datas['report_lines'][0]['move_lines'].sort((a, b) => new Date(a.ldate) - new Date(b.ldate));
                    _.each(datas['report_lines'], function(rep_lines) {
                        rep_lines['move_lines'].sort((a, b) => new Date(a.ldate) - new Date(b.ldate));
                        rep_lines.debit = self.format_currency(datas['currency'],rep_lines.debit);
                        rep_lines.credit = self.format_currency(datas['currency'],rep_lines.credit);
                        rep_lines.balance = self.format_currency(datas['currency'],rep_lines.balance);
                    });

                    if (initial_render) {
                        self.$('.filter_view_tb').html(QWeb.render('GLFilterView', {
                            filter_data: datas['filters'],
                            title : datas['name'],
                        }));
                        self.$el.find('.journals').select2({
                            placeholder: ' Journals...',
                        });
                        self.$el.find('.account').select2({
                            placeholder: ' Accounts...',
                        });
                        self.$el.find('.analytics').select2({
                            placeholder: 'Analytic Accounts...',
                        });
                        self.$el.find('.analytic_tags').select2({
                            placeholder: 'Analytic Tags...',
                        });
                        self.$el.find('.target_move').select2({
                            placeholder: 'Target Move...',
                        });
                    } else{
                        self.$('.filter_view_tb').html(QWeb.render('GLFilterView', {
                            filter_data: datas['filters'],
                            title : datas['name'],
                        }));
                    }
                    var child=[];

                    self.$('.table_view_tb').html(QWeb.render('GLTable', {
                        report_lines : datas['report_lines'],
                        filter : datas['filters'],
                        currency : datas['currency'],
                        credit_total : datas['credit_total'],
                        debit_total : datas['debit_total'],
                        debit_balance : datas['debit_balance']
                    }));
                });
            }
            catch (el) {
                window.location.href
            }
        },

        show_drop_down: function(event) {
            event.preventDefault();
            var self = this;
            var account_id = $(event.currentTarget).data('account-id');
            var offset = 0;
            var td = $(event.currentTarget).next('tr').find('td');
            if (td.length == 1) {
                var action_title = self._title
                self._rpc({
                    model: 'account.general.ledger',
                    method: 'view_report',
                    args: [
                        [self.wizard_id], action_title
                    ],
                }).then(function(data) {
                    _.each(data['report_lines'], function(rep_lines) {
                        // console.log(rep_lines['move_lines']);
                        rep_lines['move_lines'].sort((a, b) => new Date(a.ldate) - new Date(b.ldate));
                        _.each(rep_lines['move_lines'], function(move_line) {
                            move_line.debit = self.format_currency(data['currency'],move_line.debit);
                            move_line.credit = self.format_currency(data['currency'],move_line.credit);
                            move_line.balance = self.format_currency(data['currency'],move_line.balance);
                        });
                    });

                    for (var i = 0; i < data['report_lines'].length; i++) {
                        if (account_id == data['report_lines'][i]['id'] ) {
                            $(event.currentTarget).next('tr').find('td .gl-table-div').remove();
                            $(event.currentTarget).next('tr').find('td ul').after(
                                QWeb.render('SubSection', {
                                    account_data: data['report_lines'][i]['move_lines'],
                                    currency_symbol : data.currency[0],
                                    currency_position : data.currency[1],

                                }));
                            $(event.currentTarget).next('tr').find('td ul li:first a').css({
                                'background-color': '#00ede8',
                                'font-weight': 'bold',
                            });
                        }
                    }

                });
            }
        },
    });

    return GeneralLedgerCustom;
});