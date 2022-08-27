from odoo import fields, models, api, _

import io
import json
from odoo.exceptions import AccessError, UserError, AccessDenied

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

import logging

_logger = logging.getLogger(__name__)

class BalanceSheetViewinherit(models.TransientModel):
    _inherit = 'dynamic.balance.sheet.report'

    def get_dynamic_xlsx_report(self, options, response, report_data, dfr_data):
        i_data = str(report_data)
        filters = json.loads(options)
        j_data = dfr_data
        rl_data = json.loads(j_data)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        head = workbook.add_format()
        head.set_align('center')
        head.set_bold()
        head.set_font_size(20)

        sub_heading = workbook.add_format()
        sub_heading.set_align('center')
        sub_heading.set_bold()
        sub_heading.set_font_size(10)
        sub_heading.set_border(1)
        sub_heading.set_border_color('black')

        side_heading_main = workbook.add_format()
        side_heading_main.set_align('left')
        side_heading_main.set_bold()
        side_heading_main.set_font_size(10)
        side_heading_main.set_border(1)
        side_heading_main.set_border_color('black')

        side_heading_sub = workbook.add_format()
        side_heading_sub.set_align('left')
        side_heading_sub.set_bold()
        side_heading_sub.set_font_size(10)
        side_heading_sub.set_border(1)
        side_heading_sub.set_border_color('black')
        side_heading_sub.set_indent(1)


        txt = workbook.add_format()
        txt.set_font_size(10)
        txt.set_border(1)

        txt_name = workbook.add_format()
        txt_name.set_font_size(10)
        txt_name.set_border(1)
        txt_name.set_indent(3)

        txt_name_bold = workbook.add_format()
        txt_name_bold.set_font_size(10)
        txt_name_bold.set_border(1)
        txt_name_bold.set_bold()
        txt_name_bold.set_indent(2)

        sheet.merge_range('A2:D3',
                          filters.get('company_name') + ' : ' + i_data,
                          head)

        date_head = workbook.add_format()
        date_head.set_align('center')
        date_head.set_bold()
        date_head.set_font_size(10)
        date_head.set_align('vcenter')
        date_head.set_text_wrap()
        date_head.set_shrink()

        date_head_left = workbook.add_format()
        date_head_left.set_align('left')
        date_head_left.set_bold()
        date_head_left.set_font_size(10)
        date_head_left.set_indent(1)

        date_head_right = workbook.add_format()
        date_head_right.set_align('right')
        date_head_right.set_bold()
        date_head_right.set_font_size(10)
        date_head_right.set_indent(1)

        if filters.get('date_from'):
            sheet.merge_range('A4:B4', 'From: ' + filters.get('date_from'),
                              date_head_left)
        if filters.get('date_to'):
            sheet.merge_range('C4:D4', 'To: ' + filters.get('date_to'),
                              date_head_right)

        sheet.merge_range('A5:D6', '  Accounts: ' + ', '.join(
            [lt or '' for lt in
             filters['accounts']]) + ';  Journals: ' + ', '.join(
            [lt or '' for lt in
             filters['journals']]) + ';  Account Tags: ' + ', '.join(
            [lt or '' for lt in
             filters['account_tags']]) + ';  Analytic Tags: ' + ', '.join(
            [lt or '' for lt in
             filters['analytic_tags']]) + ';  Analytic: ' + ', '.join(
            [at or '' for at in
             filters['analytics']]) + ';  Target Moves: ' + filters.get(
            'target_move').capitalize(), date_head)

        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 15)
        sheet.set_column(3, 3, 15)

        row = 5
        col = 0

        row += 2
        sheet.write(row, col, '', sub_heading)
        if i_data == 'Profit and Loss':
            sheet.write(row, col + 1, 'Debit', sub_heading)
            sheet.write(row, col + 2, 'Credit', sub_heading)
            sheet.write(row, col + 3, 'Balance', sub_heading)
        elif i_data == 'Balance Sheet':
            sheet.write(row, col + 1, 'Balance', sub_heading)
        if rl_data:
            if i_data == 'Profit and Loss':
                for fr in rl_data:
                    row += 1
                    if fr['level'] == 1:
                        sheet.write(row, col, fr['name'], side_heading_main)
                    elif fr['level'] == 2:
                        sheet.write(row, col, fr['name'], side_heading_sub)
                    else:
                        if fr['report_type'] != 'accounts':
                            sheet.write(row, col, fr['name'], txt_name_bold)
                        else:
                            sheet.write(row, col, fr['name'], txt_name)
                    if fr['report_type'] != 'sum' and fr['report_type'] != 'account_type':
                        sheet.write(row, col + 1, fr['debit'], txt)
                        sheet.write(row, col + 2, fr['credit'], txt)
                        sheet.write(row, col + 3, fr['balance'], txt)
                    else:
                        sheet.write(row, col + 1, '', txt)
                        sheet.write(row, col + 2, '', txt)
                        sheet.write(row, col + 3, '', txt)

            elif i_data == 'Balance Sheet':
                for fr in rl_data:
                    row += 1
                    if fr['level'] == 1:
                        sheet.write(row, col, fr['name'], side_heading_main)
                    elif fr['level'] == 2:
                        sheet.write(row, col, fr['name'], side_heading_sub)
                    else:
                        if fr['report_type'] != 'accounts':
                            sheet.write(row, col, fr['name'], txt_name_bold)
                        else:
                            sheet.write(row, col, fr['name'], txt_name)
                    if fr['report_type'] != 'sum' and fr['report_type'] != 'account_type':
                        sheet.write(row, col + 1, fr['balance'], txt)
                    else:
                        sheet.write(row, col + 1, '', txt)
    
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
    
    @api.model
    def view_report(self, option, tag):
        r = self.env['dynamic.balance.sheet.report'].search(
            [('id', '=', option[0])])
        data = {
            'display_account': r.display_account,
            'model': self,
            'journals': r.journal_ids,
            'target_move': r.target_move,
            'accounts': r.account_ids,
            'account_tags': r.account_tag_ids,
            'analytics': r.analytic_ids,
            'analytic_tags': r.analytic_tag_ids,
        }
        if r.date_from:
            data.update({
                'date_from': r.date_from,
            })
        if r.date_to:
            data.update({
                'date_to': r.date_to,
            })

        company_id = self.env.company
        company_domain = [('company_id', '=', company_id.id)]
        if r.account_tag_ids:
            company_domain.append(
                ('tag_ids', 'in', r.account_tag_ids.ids))
        if r.account_ids:
            company_domain.append(('id', 'in', r.account_ids.ids))

        new_account_ids = self.env['account.account'].search(company_domain)
        data.update({'accounts': new_account_ids, })
        filters = self.get_filter(option)
        records = self._get_report_values(data)

        if filters['account_tags'] != ['All']:
            tag_accounts = list(map(lambda x: x.code, new_account_ids))

            def filter_code(rec_dict):
                if rec_dict['code'] in tag_accounts:
                    return True
                else:
                    return False

            new_records = list(filter(filter_code, records['Accounts']))
            records['Accounts'] = new_records

        account_report_id = self.env['account.financial.report'].search([
            ('name', 'ilike', tag)])

        new_data = {'id': self.id, 'date_from': False,
                    'enable_filter': True,
                    'debit_credit': True,
                    'date_to': False, 'account_report_id': account_report_id,
                    'target_move': filters['target_move'],
                    'view_format': 'vertical',
                    'company_id': self.company_id,
                    'used_context': {'journal_ids': False,
                                     'state': filters['target_move'].lower(),
                                     'date_from': filters['date_from'],
                                     'date_to': filters['date_to'],
                                     'strict_range': False,
                                     'company_id': self.company_id,
                                     'lang': 'en_US'}}

        account_lines = self.get_account_lines(new_data)
        report_lines = self.view_report_pdf(
            account_lines, new_data)['report_lines']
        move_line_accounts = []
        move_lines_dict = {}

        for rec in records['Accounts']:
            move_line_accounts.append(rec['code'])
            move_lines_dict[rec['code']] = {}
            move_lines_dict[rec['code']]['debit'] = rec['debit']
            move_lines_dict[rec['code']]['credit'] = rec['credit']
            move_lines_dict[rec['code']]['balance'] = rec['balance']

        report_lines_move = []
        parent_list = []

        def filter_movelines_parents(obj):
            for each in obj:
                if each['report_type'] == 'accounts':
                    if 'code' in each and each['code'] in move_line_accounts:
                        report_lines_move.append(each)
                        parent_list.append(each['p_id'])

                elif each['report_type'] == 'account_report':
                    report_lines_move.append(each)
                else:
                    report_lines_move.append(each)

        filter_movelines_parents(report_lines)
        for rec in report_lines_move:
            if rec['report_type'] == 'accounts':
                if rec['code'] in move_line_accounts:
                    rec['debit'] = move_lines_dict[rec['code']]['debit']
                    rec['credit'] = move_lines_dict[rec['code']]['credit']
                    rec['balance'] = move_lines_dict[rec['code']]['balance']

        parent_list = list(set(parent_list))
        max_level = 0
        for rep in report_lines_move:
            if rep['level'] > max_level:
                max_level = rep['level']

        def get_parents(obj):
            for item in report_lines_move:
                for each in obj:
                    if item['report_type'] != 'account_type' and \
                            each in item['c_ids']:
                        obj.append(item['r_id'])
                if item['report_type'] == 'account_report':
                    obj.append(item['r_id'])
                    break

        get_parents(parent_list)
        for i in range(max_level):
            get_parents(parent_list)

        parent_list = list(set(parent_list))
        final_report_lines = []

        for rec in report_lines_move:
            if rec['report_type'] != 'accounts':
                if rec['r_id'] in parent_list:
                    final_report_lines.append(rec)
            else:
                final_report_lines.append(rec)

        def filter_sum(obj):
            sum_list = {}
            for pl in parent_list:
                sum_list[pl] = {}
                sum_list[pl]['s_debit'] = 0
                sum_list[pl]['s_credit'] = 0
                sum_list[pl]['s_balance'] = 0

            for each in obj:
                if each['p_id'] and each['p_id'] in parent_list:
                    sum_list[each['p_id']]['s_debit'] += each['debit']
                    sum_list[each['p_id']]['s_credit'] += each['credit']
                    sum_list[each['p_id']]['s_balance'] += each['balance']
            return sum_list

        def assign_sum(obj):
            for each in obj:
                if each['r_id'] in parent_list and \
                        each['report_type'] != 'account_report':
                    each['debit'] = sum_list_new[each['r_id']]['s_debit']
                    each['credit'] = sum_list_new[each['r_id']]['s_credit']

        for p in range(max_level):
            sum_list_new = filter_sum(final_report_lines)
            assign_sum(final_report_lines)

        company_id = self.env.company
        currency = company_id.currency_id
        symbol = currency.symbol
        rounding = currency.rounding
        position = currency.position

        for rec in final_report_lines:
            rec['debit'] = round(rec['debit'], 2)
            rec['credit'] = round(rec['credit'], 2)
            rec['balance'] = rec['debit'] - rec['credit']
            rec['balance'] = round(rec['balance'], 2)
            if (rec['balance_cmp'] < 0 and rec['balance'] > 0) or (
                    rec['balance_cmp'] > 0 and rec['balance'] < 0):
                rec['balance'] = rec['balance'] * -1

            if position == "before":
                rec['m_debit'] = symbol + " " + "{:,}".format(int(rec['debit']))
                rec['m_credit'] = symbol + " " + \
                    "{:,}".format(int(rec['credit']))
                rec['m_balance'] = symbol + " " + "{:,}".format(
                    int(rec['balance']))
            else:
                rec['m_debit'] = "{:,}".format(int(rec['debit'])) + " " + symbol
                rec['m_credit'] = "{:,}".format(
                    int(rec['credit'])) + " " + symbol
                rec['m_balance'] = "{:,}".format(
                    int(rec['balance'])) + " " + symbol
        
        final_lines_with_total = []
        temp_at = {}
        temp_sum = {}
        for line in final_report_lines:
            if 'code' in line:
                acc_parent = temp_at[line['p_id']]
                if acc_parent['p_id'] != False:
                    sum_1 = temp_sum[acc_parent['p_id']]
                if sum_1['p_id'] != False:
                    sum_2 = temp_sum[sum_1['p_id']]
                final_lines_with_total.append(line)
                acc_parent['count_child'] = acc_parent['count_child'] + 1

                if acc_parent['count_child'] == acc_parent['total_child']:
                    final_lines_with_total.append(acc_parent)
                    sum_1['count_child'] = sum_1['count_child'] + 1
                if sum_1['count_child'] == sum_1['total_child']:
                    final_lines_with_total.append(sum_1)
                    sum_2['count_child'] = sum_2['count_child'] + 1
                if sum_2['count_child'] == sum_2['total_child']:
                    final_lines_with_total.append(sum_2)
            else:
                if line['report_type'] == 'account_type':
                    final_lines_with_total.append(line)
                    temp_at[line['r_id']] = line.copy()
                    at_total_child = 0
                    for c in final_report_lines:
                        if c['report_type'] == 'accounts' and c['p_id'] == line['r_id']:
                            at_total_child += 1
                    temp_at[line['r_id']]['id'] = 'Total' + temp_at[line['r_id']]['id']
                    temp_at[line['r_id']]['name'] = 'Total ' + temp_at[line['r_id']]['name']
                    temp_at[line['r_id']]['report_type'] = 'total'
                    temp_at[line['r_id']]['count_child'] = 0
                    temp_at[line['r_id']]['total_child'] = at_total_child

                elif line['report_type'] == 'sum':
                    final_lines_with_total.append(line)
                    temp_sum[line['r_id']] = line.copy()
                    # sum_total_child = len(line['c_ids'])
                    sum_total_child = 0
                    for c in final_report_lines:
                        if c['p_id'] == line['r_id']:
                            sum_total_child += 1
                    temp_sum[line['r_id']]['id'] = 'Total' + temp_sum[line['r_id']]['id']
                    temp_sum[line['r_id']]['name'] = 'Total ' + temp_sum[line['r_id']]['name']
                    temp_sum[line['r_id']]['report_type'] = 'total'
                    temp_sum[line['r_id']]['count_child'] = 0
                    temp_sum[line['r_id']]['total_child'] = sum_total_child

                elif line['report_type'] == 'account_report':
                    final_lines_with_total.append(line)
                    if line['p_id'] != False:
                        parent_1 = temp_sum[line['p_id']]
                        parent_1['count_child'] = parent_1['count_child'] + 1
                    if parent_1['count_child'] == parent_1['total_child']:
                        final_lines_with_total.append(parent_1)
                        if parent_1['p_id'] != False:
                            parent_2 = temp_sum[parent_1['p_id']]
                            parent_2['count_child'] = parent_2['count_child'] + 1
                            if parent_2['count_child'] == parent_2['total_child']:
                                final_lines_with_total.append(parent_2)
        
        return {
            'name': tag,
            'type': 'ir.actions.client',
            'tag': tag,
            'filters': filters,
            'report_lines': records['Accounts'],
            'debit_total': records['debit_total'],
            'credit_total': records['credit_total'],
            'debit_balance': records['debit_balance'],
            'currency': currency,
            'bs_lines': final_lines_with_total,
        }
