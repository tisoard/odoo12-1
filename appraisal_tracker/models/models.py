# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class apprisal_tracker_vendor(models.Model):

    _inherit = "purchase.order"

    tier1_retail = fields.Monetary(compute="_value_broker_margin", store=False, string="Tier 1 Retail")
    tier2_retail = fields.Monetary(compute="_value_broker_margin", store=False, string="Tier 2 Retail")
    less_than_40_retail = fields.Monetary(compute="_value_broker_margin", store=False, string="< 40% Retail")
    broker_margin = fields.Char(compute="_value_broker_margin", store=False)
    cust_type_appraisal = fields.Char(compute="_value_broker_margin", store=False,string="Type")

    tier1_margin = fields.Char(compute="_value_broker_margin", store=False, string="Tier 1 Margin")
    tier2_margin = fields.Char(compute="_value_broker_margin", store=False, string="Tier 2 Margin")
    less_than_40_margin = fields.Char(compute="_value_broker_margin", store=False, string="< 40% Margin")

    color = fields.Integer(compute="_value_broker_margin", store=False)

    t1color = fields.Integer(compute="_value_broker_margin", store=False)
    t2color = fields.Integer(compute="_value_broker_margin", store=False)
    lscolor = fields.Integer(compute="_value_broker_margin", store=False)


    @api.onchange('broker_margin')
    def _value_broker_margin(self):
        # for order in self:
        #
        #     tier1_retail_temp = 0
        #     tier2_retail_temp = 0
        #     tier1_offer_temp = 0
        #     tier2_offer_temp = 0
        #     less_than_40_retail = 0
        #
        #     for line in order.order_line:
        #         if line.product_id.tier.code == '1':
        #             tier1_retail_temp = tier1_retail_temp + line.product_retail
        #             tier1_offer_temp = tier1_offer_temp + line.price_subtotal
        #         if line.product_id.tier.code == '2':
        #             tier2_retail_temp = tier2_retail_temp + line.product_retail
        #             tier2_offer_temp = tier2_offer_temp + line.price_subtotal
        #
        #
        #         if tier1_retail_temp > 0 :
        #             t1_margin = round(tier1_offer_temp/tier1_retail_temp,2)
        #         if tier2_retail_temp > 0:
        #             t2_margin = round(tier2_offer_temp/tier2_retail_temp,2)
        #         if order.partner_id.is_wholesaler == True:
        #             if line.product_id.tier.code == '1':
        #                 amt = t1_margin
        #
        #                 if(abs(float(amt - 1)) < 0.4):
        #                     order.update({
        #                         'tier1_margin': 'Margin < 40%',
        #                         't1color': 1
        #                     })
        #
        #                 elif ((abs(float(amt - 1)) >= 0.4) and (abs(float(amt - 1)) < 0.48)):
        #                     order.update({
        #                         'tier1_margin': 'T2 Wholesaler',
        #                         't1color': 2
        #                     })
        #
        #                 elif ((abs(float(amt - 1)) >= 0.48) ):
        #                     order.update({
        #                         'tier1_margin': 'T1 Wholesaler',
        #                         't1color': 3
        #                     })
        #
        #             if line.product_id.tier.code == '2':
        #
        #                 amt = t2_margin
        #
        #                 if(abs(float(amt - 1)) < 0.4):
        #                     order.update({
        #                         'tier2_margin': 'Margin < 40%',
        #                         't2color': 1
        #                     })
        #
        #                 elif ((abs(float(amt - 1)) >= 0.4)):
        #                     order.update({
        #                         'tier2_margin': 'T2 Wholesaler',
        #                         't2color': 2
        #                     })
        #
        #         order.update({
        #             'tier1_retail': tier1_retail_temp,
        #             'tier2_retail': tier2_retail_temp,
        #             'less_than_40_retail': less_than_40_retail
        #         })
        #
        #     if order.partner_id.is_wholesaler == False:
        #
        #         if(order.rt_price_total_amt!=0):
        #             if (abs(float(((order.amount_total) / float(order.rt_price_total_amt)) - 1)) < 0.4):
        #                 order.update({
        #                     'less_than_40_margin': 'Margin < 40%',
        #                     'lscolor': 1
        #                 })
        #             elif order.partner_id.is_broker:
        #                 if (abs(float(order.amount_total / order.rt_price_total_amt)) < 0.52):
        #                     order.update({
        #                         'less_than_40_margin': 'T1 BROKER',
        #                         'lscolor': 2
        #                     })
        #                 elif (abs(float(order.amount_total / order.rt_price_total_amt)) > 0.52):
        #                     order.update({
        #                         'less_than_40_margin': 'T2 BROKER',
        #                         'lscolor': 3
        #                     })

            for order in self:
                tier1_retail_temp = 0
                tier2_retail_temp = 0
                less_than_40_retail = 0

                if order.partner_id.is_wholesaler == True:

                    order.cust_type_appraisal = 'Wholesaler'
                    for line in order.order_line:

                        amt = line.product_offer_price / line.product_unit_price

                        if (line.product_id.tier.code == '1') and \
                                (abs(float(amt - 1)) >= 0.48):
                            tier1_retail_temp = tier1_retail_temp + line.product_unit_price

                        if (((line.product_id.tier.code == '1') and \
                             ((abs(float(amt - 1)) >= 0.4) and (abs(float(amt - 1)) < 0.48)))
                                or (line.product_id.tier.code == '2' and (abs(float(amt)) >= 0.4))
                        ):
                            tier2_retail_temp = tier2_retail_temp + line.product_unit_price

                        if abs(float(amt - 1)) < 0.4:
                            less_than_40_retail = less_than_40_retail + line.product_unit_price
                        order.update({
                            'tier1_retail': tier1_retail_temp,
                            'tier2_retail': tier2_retail_temp,
                            'less_than_40_retail': less_than_40_retail
                        })

                elif order.partner_id.is_broker == True:

                    order.cust_type_appraisal = 'Broker'

                    for line in order.order_line:

                        amt = line.product_offer_price/line.product_unit_price

                        if (line.product_id.tier.code == '1') and \
                                (abs(float(amt - 1)) >= 0.48):

                            tier1_retail_temp = tier1_retail_temp + line.product_unit_price

                        if (((line.product_id.tier.code == '1') and \
                                ((abs(float(amt - 1)) >= 0.4) and (abs(float(amt - 1)) < 0.48)))
                                or (line.product_id.tier.code == '2' and (abs(float(amt)) >= 0.4))
                                ):

                            tier2_retail_temp = tier2_retail_temp + line.product_unit_price

                        if abs(float(amt - 1)) < 0.4:
                            less_than_40_retail = less_than_40_retail + line.product_unit_price

                    order.update({
                        'tier1_retail': tier1_retail_temp,
                        'tier2_retail': tier2_retail_temp,
                        'less_than_40_retail': less_than_40_retail
                    })

                else:
                    order.cust_type_appraisal = 'Traditional'
                    for line in order.order_line:
                        if line.product_id.tier.code == '1':
                            tier1_retail_temp = tier1_retail_temp + line.product_unit_price
                        if line.product_id.tier.code == '2':
                            tier2_retail_temp = tier2_retail_temp + line.product_unit_price

                    order.update({
                        'tier1_retail': tier1_retail_temp,
                        'tier2_retail': tier2_retail_temp,
                        'less_than_40_retail': less_than_40_retail
                    })


class CustomerAsWholesaler(models.Model):
    _inherit = 'res.partner'

    is_wholesaler = fields.Boolean(string="Is a Wholesaler?")

    @api.onchange('is_wholesaler', 'is_broker')
    def _check_wholesaler_setting(self):
        warning = {}
        val = {}
        if self.is_broker == True and self.is_wholesaler == True:
            val.update({'is_broker': False})
            warning = {
                'title': _('Warning'),
                'message': _('Customer can be either Wholesaler or Broker , not both'),
            }
        return {'value': val, 'warning': warning}






