odoo.define(
  "jidoka_dynamic_accounts_report.financial_reports",
  function (require) {
    "use strict";
    var ProfitAndLoss = require("dynamic_accounts_report.financial_reports");
    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var field_utils = require("web.field_utils");
    var rpc = require("web.rpc");
    var session = require("web.session");
    var utils = require("web.utils");
    var QWeb = core.qweb;
    var _t = core._t;

    window.click_num = 0;
    var ProfitAndLossCustom = ProfitAndLoss.include({
      load_data: function (initial_render = true) {
        var self = this;
        var action_title = self._title;
        self.$(".categ").empty();
        try {
          var self = this;
          self
            ._rpc({
              model: "dynamic.balance.sheet.report",
              method: "view_report",
              args: [[this.wizard_id], action_title],
            })
            .then(function (datas) {
              console.log(datas);
              if (initial_render) {
                self.$(".filter_view_dfr").html(
                  QWeb.render("DfrFilterView", {
                    filter_data: datas["filters"],
                    title: datas["name"],
                  })
                );
                self.$el.find(".journals").select2({
                  placeholder: " Journals...",
                });
                self.$el.find(".account").select2({
                  placeholder: " Accounts...",
                });
                self.$el.find(".account-tag").select2({
                  placeholder: "Account Tag...",
                });
                self.$el.find(".analytics").select2({
                  placeholder: "Analytic Accounts...",
                });
                self.$el.find(".analytic-tag").select2({
                  placeholder: "Analytic Tag...",
                });
                self.$el.find(".target_move").select2({
                  placeholder: "Target Move...",
                });
              }
              var child = [];
              self.$(".table_view_dfr").html(
                QWeb.render("dfr_table", {
                  title: datas["name"],
                  report_lines: datas["report_lines"],
                  filter: datas["filters"],
                  currency: datas["currency"],
                  credit_total: datas["credit_total"],
                  debit_total: datas["debit_total"],
                  debit_balance: datas["debit_balance"],
                  bs_lines: datas["bs_lines"],
                })
              );
            });
        } catch (el) {
          window.location.href;
        }
      },

      show_gl: function (e) {
        var self = this;
        var account_id = $(e.target).attr("data-account-id");
        var options = {
          account_ids: [account_id],
        };
        var action = {
          type: "ir.actions.client",
          name: "GL View",
          tag: "g_l",
          target: "new",
          domain: [
            ["account_ids", "=", account_id],
            ['date_from', '=', $("#date_from").val()],
            ['date_to', '=', $("#date_to").val()],
            ['target_move', '=', $("#post_res").val()],
          ],
        };
        console.log("Ini Action")
        console.log(action);
        return this.do_action(action);
      },

      print_pdf: function (e) {
        e.preventDefault();
        var self = this;
        var action_title = self._title;
        self
          ._rpc({
            model: "dynamic.balance.sheet.report",
            method: "view_report",
            args: [[self.wizard_id], action_title],
          })
          .then(function (data) {
            var action = {
              type: "ir.actions.report",
              report_type: "qweb-pdf",
              report_name: "jidoka_dynamic_accounts_report.balance_sheet",
              report_file: "jidoka_dynamic_accounts_report.balance_sheet",
              data: {
                report_data: data,
                report_name: action_title,
              },
              context: {
                active_model: "dynamic.balance.sheet.report",
                landscape: 1,
                bs_report: true,
              },
              display_name: action_title,
            };
            console.log(action);
            return self.do_action(action);
          });
      },

      apply_filter: function (event) {
        event.preventDefault();
        var self = this;
        self.initial_render = false;
        var filter_data_selected = {};
        var account_ids = [];
        var account_text = [];
        var account_res = document.getElementById("acc_res");
        var account_list = $(".account").select2("data");
        for (var i = 0; i < account_list.length; i++) {
          if (account_list[i].element[0].selected === true) {
            account_ids.push(parseInt(account_list[i].id));
            if (account_text.includes(account_list[i].text) === false) {
              account_text.push(account_list[i].text);
            }
            account_res.value = account_text;
            account_res.innerHTML = account_res.value;
          }
        }
        if (account_list.length == 0) {
          account_res.value = "";
          account_res.innerHTML = "";
        }
        filter_data_selected.account_ids = account_ids;
  
        var journal_ids = [];
        var journal_text = [];
        var journal_res = document.getElementById("journal_res");
        var journal_list = $(".journals").select2("data");
        for (var i = 0; i < journal_list.length; i++) {
          if (journal_list[i].element[0].selected === true) {
            journal_ids.push(parseInt(journal_list[i].id));
            if (journal_text.includes(journal_list[i].text) === false) {
              journal_text.push(journal_list[i].text);
            }
            journal_res.value = journal_text;
            journal_res.innerHTML = journal_res.value;
          }
        }
        if (journal_list.length == 0) {
          journal_res.value = "";
          journal_res.innerHTML = "";
        }
        filter_data_selected.journal_ids = journal_ids;
  
        var account_tag_ids = [];
        var account_tag_text = [];
        var account_tag_res = document.getElementById("acc_tag_res");
  
        var account_tag_list = $(".account-tag").select2("data");
        for (var i = 0; i < account_tag_list.length; i++) {
          if (account_tag_list[i].element[0].selected === true) {
            account_tag_ids.push(parseInt(account_tag_list[i].id));
            if (account_tag_text.includes(account_tag_list[i].text) === false) {
              account_tag_text.push(account_tag_list[i].text);
            }
  
            account_tag_res.value = account_tag_text;
            account_tag_res.innerHTML = account_tag_res.value;
          }
        }
        if (account_tag_list.length == 0) {
          account_tag_res.value = "";
          account_tag_res.innerHTML = "";
        }
        filter_data_selected.account_tag_ids = account_tag_ids;
  
        var analytic_ids = [];
        var analytic_text = [];
        var analytic_res = document.getElementById("analytic_res");
        var analytic_list = $(".analytics").select2("data");
  
        for (var i = 0; i < analytic_list.length; i++) {
          if (analytic_list[i].element[0].selected === true) {
            analytic_ids.push(parseInt(analytic_list[i].id));
            if (analytic_text.includes(analytic_list[i].text) === false) {
              analytic_text.push(analytic_list[i].text);
            }
            analytic_res.value = analytic_text;
            analytic_res.innerHTML = analytic_res.value;
          }
        }
        if (analytic_list.length == 0) {
          analytic_res.value = "";
          analytic_res.innerHTML = "";
        }
        filter_data_selected.analytic_ids = analytic_ids;
  
        var analytic_tag_ids = [];
        var analytic_tag_text = [];
        var analytic_tag_res = document.getElementById("analic_tag_res");
        var analytic_tag_list = $(".analytic-tag").select2("data");
        for (var i = 0; i < analytic_tag_list.length; i++) {
          if (analytic_tag_list[i].element[0].selected === true) {
            analytic_tag_ids.push(parseInt(analytic_tag_list[i].id));
            if (analytic_tag_text.includes(analytic_tag_list[i].text) === false) {
              analytic_tag_text.push(analytic_tag_list[i].text);
            }
  
            analytic_tag_res.value = analytic_tag_text;
            analytic_tag_res.innerHTML = analytic_tag_res.value;
          }
        }
        if (analytic_tag_list.length == 0) {
          analytic_tag_res.value = "";
          analytic_tag_res.innerHTML = "";
        }
        filter_data_selected.analytic_tag_ids = analytic_tag_ids;
  
        var start_date_res = document.getElementById("start_date_res");
        var end_date_res = document.getElementById("end_date_res");
        var dates;
        if ($("#date_from").val()) {
          var dateString = $("#date_from").val();
          filter_data_selected.date_from = dateString;
          dates = dateString.split('-');
          start_date_res.innerHTML = dates[2] + '-' + dates[1] + '-' + dates[0];
        }
        if ($("#date_to").val()) {
          var dateString = $("#date_to").val();
          filter_data_selected.date_to = dateString;
          dates = dateString.split('-');
          end_date_res.innerHTML = dates[2] + '-' + dates[1] + '-' + dates[0];
        }
  
        if ($(".target_move").length) {
          var post_res = document.getElementById("post_res");
          filter_data_selected.target_move = $(".target_move")[1].value;
          post_res.value = $(".target_move")[1].value;
          post_res.innerHTML = post_res.value;
          if ($(".target_move")[1].value == "") {
            post_res.innerHTML = "posted";
          }
        }
        rpc
          .query({
            model: "dynamic.balance.sheet.report",
            method: "write",
            args: [self.wizard_id, filter_data_selected],
          })
          .then(function (res) {
            self.initial_render = false;
            self.load_data(self.initial_render);
          });
      },

    });

    return ProfitAndLossCustom;
  }
);
