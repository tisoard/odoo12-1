# See LICENSE file for full copyright and licensing details.

import werkzeug
from odoo import fields, http
from odoo.http import request
import odoo.addons.website_sale.controllers.main
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import TableCompute, QueryURL

PPG = 20
PPR = 4


#
# '/shop', '/shop/page/<int:page>',
#                  '/shop/category/<model("product.public.category"):category>',
#                  '/shop/category/<model("product.public.category"):category>\
#
class WebsiteSale(odoo.addons.website_sale.controllers.main.WebsiteSale):
    @http.route(['/page/<int:page>', '/shop/brands'], type='http',
                auth='public', website=True)
    def shopBrand(self, page=0, category=None, search='', brand=None, **post):
        values = {}
        domain = request.website.sale_product_domain()
        if search:
            domain += ['|', '|', '|',
                       ('name', 'ilike', search),
                       ('description', 'ilike', search),
                       ('description_sale', 'ilike', search),
                       ('product_variant_ids.default_code', 'ilike', search)]
        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split('-')) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])
        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]

            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]
        keep = QueryURL('/shop', category=category and int(category),
                        search=search, attrib=attrib_list)

        pricelist_context = dict(request.env.context)
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(
                pricelist_context['pricelist'])

        product_obj = request.env['product.template']

        # Brand's product search
        if brand:
            values.update({'brand': brand})
            product_designer_obj = request.env['product.brand']
            brand_ids = product_designer_obj.search([('id', '=', int(brand))])
            domain += [('product_brand_id', 'in', brand_ids.ids)]
        url = '/shop'
        product_count = product_obj.search_count(domain)
        if search:
            post['search'] = search
        if category:
            category = request.env['product.public.category']. \
                browse(int(category))
            url = '/shop/category/%s' % slug(category)
        pager = request.website. \
            pager(url=url, total=product_count, page=page, step=PPG,
                  scope=7, url_args=post)
        products = product_obj. \
            search(domain, limit=PPG, offset=pager['offset'],
                   order='website_published desc, website_sequence desc')
        style_obj = request.env['product.style']
        styles = style_obj.search([])
        category_obj = request.env['product.public.category']
        categories = category_obj.search([])
        categs = filter(lambda x: not x.parent_id, categories)
        if category:
            selected_id = int(category)
            children_ids = category_obj. \
                search([('parent_id', '=', selected_id)])
            values.update({'child_list': children_ids})
        attributes_obj = request.env['product.attribute']
        attributes = attributes_obj.search([])
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = self.currency_compute(from_currency, to_currency)
        values.update({'search': search,
                       'category': category,
                       'attrib_values': attrib_values,
                       'attrib_set': attrib_set,
                       'pager': pager,
                       'pricelist': pricelist,
                       'products': products,
                       'bins': TableCompute().process(products),
                       'rows': PPR,
                       'styles': styles,
                       'categories': categs,
                       'attributes': attributes,
                       'compute_currency': compute_currency,
                       'keep': keep,
                       'style_in_product':
                           lambda style, product: style.id in [
                               s.id for s in product.website_style_ids],
                       'attrib_encode': lambda attribs: werkzeug.url_encode
                       ([('attrib', i) for i in attribs])})

        # ---------------------- CSTM ------------------------

        productMaxMinDates = {}
        productProduct = request.env['product.product'].search([('product_tmpl_id', 'in', products.ids)])
        for val in productProduct:
            val.env.cr.execute(
                "SELECT min(use_date), max (use_date) FROM public.stock_production_lot where product_id = %s",
                (val.id,))
            query_result = val.env.cr.dictfetchone()
            productMaxMinDates[val.id] = {"min": fields.Datetime.from_string(query_result['min']),
                                                          "max": fields.Datetime.from_string(query_result['max'])}

        values['productExpiration'] = productMaxMinDates;
        values['isVisibleWebsiteExpirationDate'] = request.env['ir.config_parameter'].sudo().get_param(
            'website_sales.website_expiration_date')

        porductRows = []
        porductRows.append([])
        i = 1
        for val in products:
            porductRows[-1].append(val)
            if i % 4 == 0:
                porductRows.append([])
            i += 1

        values['porductRows'] = porductRows

        return request.render('website_sale.products', values)

    def currency_compute(self, from_currency, to_currency):
        return lambda price: from_currency.compute(price,
                                                   to_currency)

    # Method to get the brands.
    @http.route(['/page/product_brands'], type='http', auth='public',
                website=True)
    def product_brands(self, **post):
        brand_values = []
        brand_obj = request.env['product.brand']
        domain = []
        if post.get('search'):
            domain += [('name', 'ilike', post.get('search'))]
        brand_ids = brand_obj.search(domain)
        for brand_rec in brand_ids:
            brand_values.append(brand_rec)

        keep = QueryURL('/page/product_brands', brand_id=[])
        values = {'brand_rec': brand_values, 'keep': keep}
        if post.get('search'):
            values.update({'search': post.get('search')})
        return request.render('website_product_brand.product_brands', values)
