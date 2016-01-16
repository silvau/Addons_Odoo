openerp.pos_computed_discount = function(instance) {
    var module = instance.point_of_sale;
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision
    var _t = instance.web._t;

    module.PosModel = module.PosModel.extend({
        load_server_data: function(){
            var self = this;

            var loaded = self.fetch('res.users',['name','company_id'],[['id','=',this.session.uid]])
                .then(function(users){
                    self.set('user',users[0]);

                    return self.fetch('res.company',
                    [
                        'currency_id',
                        'email',
                        'website',
                        'company_registry',
                        'vat',
                        'name',
                        'phone',
                        'partner_id',
                    ],
                    [['id','=',users[0].company_id[0]]]);
                }).then(function(companies){
                    self.set('company',companies[0]);

                    return self.fetch('res.partner',['contact_address'],[['id','=',companies[0].partner_id[0]]]);
                }).then(function(company_partners){
                    self.get('company').contact_address = company_partners[0].contact_address;

                    return self.fetch('product.uom', null, null);
                }).then(function(units){
                    self.set('units',units);
                    var units_by_id = {};
                    for(var i = 0, len = units.length; i < len; i++){
                        units_by_id[units[i].id] = units[i];
                    }
                    self.set('units_by_id',units_by_id);

                    return self.fetch('product.packaging', null, null);
                }).then(function(packagings){
                    self.set('product.packaging',packagings);

                    return self.fetch('res.users', ['name','ean13'], [['ean13', '!=', false]]);
                }).then(function(users){
                    self.set('user_list',users);

                    return self.fetch('res.partner', ['name','ean13'], [['ean13', '!=', false]]);
                }).then(function(partners){
                    self.set('partner_list',partners);

                    return self.fetch('account.tax', ['amount', 'price_include', 'type']);
                }).then(function(taxes){
                    self.set('taxes', taxes);

                    return self.fetch(
                        'pos.session',
                        ['id', 'journal_ids','name','user_id','config_id','start_at','stop_at'],
                        [['state', '=', 'opened'], ['user_id', '=', self.session.uid]]
                    );
                }).then(function(sessions){
                    self.set('pos_session', sessions[0]);

                    return self.fetch(
                        'pos.config',
                        ['name','journal_ids','shop_id','journal_id',
                         'iface_self_checkout', 'iface_led', 'iface_cashdrawer',
                         'iface_payment_terminal', 'iface_electronic_scale', 'iface_barscan', 'iface_vkeyboard',
                         'iface_print_via_proxy','iface_cashdrawer','state','sequence_id','session_ids',
                         'discount_amount', 'discount_journal_id', 'discount_percent',
                         'discount_inapam_percent', 'discount_quantity', 'discount_quantity_percent',
                         'special_discount_password'],
                        [['id','=', self.get('pos_session').config_id[0]]]
                    );
                }).then(function(configs){
                    var pos_config = configs[0];
                    self.set('pos_config', pos_config);
                    self.iface_electronic_scale    =  !!pos_config.iface_electronic_scale;
                    self.iface_print_via_proxy     =  !!pos_config.iface_print_via_proxy;
                    self.iface_vkeyboard           =  !!pos_config.iface_vkeyboard;
                    self.iface_self_checkout       =  !!pos_config.iface_self_checkout;
                    self.iface_cashdrawer          =  !!pos_config.iface_cashdrawer;

                    return self.fetch('sale.shop',[],[['id','=',pos_config.shop_id[0]]]);
                }).then(function(shops){
                    self.set('shop',shops[0]);

                    return self.fetch('product.pricelist',['currency_id'],[['id','=',self.get('shop').pricelist_id[0]]]);
                }).then(function(pricelists){
                    self.set('pricelist',pricelists[0]);

                    return self.fetch('res.currency',['symbol','position','rounding','accuracy'],[['id','=',self.get('pricelist').currency_id[0]]]);
                }).then(function(currencies){
                    self.set('currency',currencies[0]);

                    return self.fetch('product.packaging',['ean','product_id']);
                }).then(function(packagings){
                    self.db.add_packagings(packagings);

                    return self.fetch('pos.category', ['id','name','parent_id','child_id','image'])
                }).then(function(categories){
                    self.db.add_categories(categories);

                    return self.fetch(
                        'product.product',
                        ['name', 'list_price','price','pos_categ_id', 'taxes_id', 'ean13', 'default_code', 'variants',
                         'to_weight', 'uom_id', 'uos_id', 'uos_coeff', 'mes_type', 'description_sale', 'description'],
                        [['sale_ok','=',true],['available_in_pos','=',true]],
                        {pricelist: self.get('shop').pricelist_id[0]} // context for price
                    );
                }).then(function(products){
                    self.db.add_products(products);

                    return self.fetch(
                        'account.bank.statement',
                        ['account_id','currency','journal_id','state','name','user_id','pos_session_id'],
                        [['state','=','open'],['pos_session_id', '=', self.get('pos_session').id]]
                    );
                }).then(function(bank_statements){
                    var journals = new Array();
                    _.each(bank_statements,function(statement) {
                        journals.push(statement.journal_id[0])
                    });
                    self.set('bank_statements', bank_statements);
                    return self.fetch('account.journal', undefined, [['id','in', journals]]);
                }).then(function(journals){
                    self.set('journals',journals);

                    // associate the bank statements with their journals.
                    var bank_statements = self.get('bank_statements');
                    for(var i = 0, ilen = bank_statements.length; i < ilen; i++){
                        for(var j = 0, jlen = journals.length; j < jlen; j++){
                            if(bank_statements[i].journal_id[0] === journals[j].id){
                                bank_statements[i].journal = journals[j];
                                bank_statements[i].self_checkout_payment_method = journals[j].self_checkout_payment_method;
                            }
                        }
                    }
                    self.set({'cashRegisters' : new module.CashRegisterCollection(self.get('bank_statements'))});

                    return self.fetch('hr.employee', undefined, [['active', '=', true], ['seller', '=', true]]);
                }).then(function(sellers){
                    self.set('sellers', sellers);
                });

            return loaded;
        },
        // Copied from: addons/point_of_sale/static/src/js/models.js:262
        flush: function() {
            //TODO make the mutex work
            //this makes sure only one _int_flush is called at the same time
            /*
            return this.flush_mutex.exec(_.bind(function() {
                return this._flush(0);
            }, this));
            */
            this._flush(0);
        },
        // Copied from: addons/point_of_sale/static/src/js/models.js:275
        _flush: function(index){
            var self = this;
            var orders = this.db.get_orders();
            self.set('nbr_pending_operations',orders.length);

            var order  = orders[index];
            if(!order){
                return;
            }
            if (order === this.flushing_order) {
                return;
            }
            this.flushing_order = order;

            //try to push an order to the server
            // shadow : true is to prevent a spinner to appear in case of timeout
            (new instance.web.Model('pos.order')).call('create_from_ui',[[order]],undefined,{ shadow:true })
                .fail(function(unused, event){
                    //don't show error popup if it fails
                    event.preventDefault();
                    console.error('Failed to send order:',order);
                    self.flushing_order = false;
                    self._flush(index+1);
                })
                .done(function(){
                    //remove from db if success
                    self.db.remove_order(order.id);
                    self.flushing_order = false;
                    self._flush(index);
                });
        },
    });

    module.Order = module.Order.extend({
        addProduct: function(product, options){
            options = options || {};
            var self = this;
            if (options.seller_id) {
                self._addProduct(product, options);
            } else {
                self.trigger('pos-show-salesman-popup', {product: product, options: options});
            }
        },
        _addProduct: function(product, options) {
            var attr = product.toJSON();
            attr.pos = this.pos;
            attr.order = this;

            var line = new module.Orderline({}, {
                pos: this.pos, order: this, product: product,
                seller_id: options.seller_id
            });

            var config = this.pos.get('pos_config');

            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }
            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }

            var last_orderline = this.getLastOrderline();
            if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
                last_orderline.merge(line);
            }else{
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
        },
        recompute_discounts: function(using_discount_journal, apply_discounts) {
            var config = this.pos.get('pos_config');
            var order = this.pos.get('selectedOrder');
            var lines = order.get('orderLines').models;
            
            // Group lines by product and compute base_total (without taxes or discounts)
            var base_total = 0;
            var grouped_qty = {};
            var grouped_lines = {};
            for (var i in lines) {
                var product_id = lines[i].product.id;
                if (!(product_id in grouped_lines)) {
                    grouped_qty[product_id] = 0;
                    grouped_lines[product_id] = [];
                }

                base_total += lines[i].get_all_prices().priceWithoutTax;
                grouped_qty[product_id] += lines[i].quantity;
                grouped_lines[product_id].push(lines[i]);

                // Reset discount
                console.log("is return", lines[i].is_return);
                if(lines[i].is_return !== true){
                  lines[i].set_discount(0.0);
                }
            }

            // Update discounts
            if(apply_discounts !== false) {
                if (base_total >= config.discount_amount && using_discount_journal) {
                    for (var i in lines) {
                        if(lines[i].is_return === true) continue
                        if (!lines[i].is_auction) {
                            lines[i].set_discount(config.discount_percent);
                        }
                    }
                } else if (order.is_customer_inapam) {
                    for (var i in lines) {
                        if(lines[i].is_return === true) continue
                        if (!lines[i].is_auction) {
                            lines[i].set_discount(config.discount_inapam_percent);
                        }
                    }
                } else {
                    for (var product_id in grouped_lines) {
                        if (grouped_qty[product_id] >= config.discount_quantity) {
                            discount = config.discount_quantity_percent;
    
                            for (var i in grouped_lines[product_id]) {
                                if(lines[i].is_return === true) continue
                                if (!grouped_lines[product_id][i].is_auction) {
                                    grouped_lines[product_id][i].set_discount(discount);
                                }
                            }
                        }
                    }
                }
            }
        },
    });

    module.Orderline = module.Orderline.extend({
        initialize: function(attr,options){
            var self = this;

            this.pos = options.pos;
            this.order = options.order;
            this.product = options.product;
            this.price   = options.product.get('price');
            this.quantity = 1;
            this.quantityStr = '1';
            this.discount = 0;
            this.discountStr = '0';
            this.type = 'unit';
            this.selected = false;
            this.seller_id = options.seller_id;
            this.is_auction = false;
            this.specialDiscountType = 'amount';
            this.specialDiscount = 0;

            if (this.product.get('pos_categ_id')) {
                var pos_categ_id = this.product.get('pos_categ_id')[0];
                new instance.web.Model('pos.category').call('read', [pos_categ_id, ['is_auction']]).then(function(result) {
                    self.is_auction = result.is_auction;
                });
            }
        },
        get_discount: function(){
            if(this.special_discount != 0){
                var first_discount = this.discount;
                var second_discount = 0;
                if(this.specialDiscountType === 'amount'){
                    var price_unit = this.get_unit_price();
                    if(first_discount){
                        price_unit = price_unit - price_unit * (first_discount/100)
                    }
                    second_discount = this.specialDiscount * 100 / price_unit;
                }else if(this.specialDiscountType === 'percent'){
                    second_discount = this.specialDiscount;
                }
                var first_fraction = 100 - first_discount;
                var total_fraction = first_fraction - (second_discount / 100) * first_fraction;
                return 100 - total_fraction;
            }else{
                return this.discount;
            }
        },
        get_discount_str: function(){
            if(this.specialDiscount != 0){
                var specialDiscountStr = this.specialDiscountType==='amount'? '$' + this.specialDiscount : this.specialDiscount + '%';
                //return this.discountStr + " más " + specialDiscountStr + " de descuento";
                return this.discountStr + "(+ descuento especial)";
            }else{
                return this.discountStr;
            }
        },
        export_as_JSON: function() {
            var product = this.get_product();
            return {
                qty: this.get_quantity(),
                price_unit: this.get_unit_price(),
                discount: this.get_discount(),
                product_id: product.get('id'),
                prodlot_id: product.get('prodlot_id'),
                supervisor_id: this.supervisor_id,
                supervisor_tum_id: this.supervisor_tum_id,
                supervisor_tum_card_id: this.supervisor_tum_card_id,
                tax_ids: [[6, 0, product.get('taxes_id')]],
                return_line_id: this.return_line_id,
                seller_id: this.seller_id,
            };
        },
        can_be_merged_with: function(orderline){
            if( this.get_product().get('id') !== orderline.get_product().get('id')){    //only orderline of the same product can be merged
                return false;
            }else if(this.get_product_type() !== orderline.get_product_type()){
                return false;
            }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
                return false;
            }else if(this.price !== orderline.price){
                return false;
            }else if(this.seller_id !== orderline.seller_id) {
                return false;
            }else{
                return true;
            }
        },
    });

    module.ScreenSelector = module.ScreenSelector.extend({
        show_popup: function(name, settings){
            if(this.current_popup){
                this.close_popup();
            }
            this.current_popup = this.popup_set[name];
            this.current_popup.show(settings);
        },
    });

    module.OrderWidget = module.OrderWidget.extend({
        set_value: function(val) {
            var order = this.pos.get('selectedOrder');
            if (order.get('orderLines').length !== 0) {
                var mode = this.numpadState.get('mode');
                if( mode === 'quantity'){
                    order.getSelectedLine().set_quantity(val);
                    order.recompute_discounts();
                }else if( mode === 'discount'){
                    order.getSelectedLine().set_discount(val);
                }else if( mode === 'price'){
                    order.getSelectedLine().set_unit_price(val);
                    order.recompute_discounts();
                }
            } else {
                this.pos.get('selectedOrder').destroy();
            }
        },
        change_selected_order: function() {
            this.currentOrderLines.unbind();
            this.bind_orderline_events();
            this.renderElement();
            this.pos_widget.extra_btn.renderElement();
        },
    });

    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
        recompute_discounts: function() {
            var discount_journal = this.pos.get('pos_config').discount_journal_id[0];
            var using_discount_journal = true;
            if (this.currentPaymentLines.length < 1) {
                using_discount_journal = false;
            }
            
            var apply_discounts = true;
            var not_participant_journals = [];
            for(var i in this.pos.get("journals")){
                var journal = this.pos.get("journals")[i]; 
                if(!journal.aplica_descuento){
                    not_participant_journals.push(journal.id);
                }
            }
            
            for(var i in this.currentPaymentLines.models){
                var payment_line = this.currentPaymentLines.models[i];
                
                var journal_id = payment_line.cashregister.get('journal_id')[0];

                if (journal_id != discount_journal) {
                    using_discount_journal = false;
                }
                
                if ($.inArray(journal_id, not_participant_journals) !== -1) {
                    apply_discounts = false;
                }
            }
            this.pos.get('selectedOrder').recompute_discounts(using_discount_journal, apply_discounts);
        },
        addPaymentLine: function(newPaymentLine) {
            var self = this;
            var l = new module.PaymentlineWidget(this, {
                    payment_line: newPaymentLine,
            });
            l.on('delete_payment_line', self, function(r) {
                self.deleteLine(r);
            });
            l.appendTo(this.$('#paymentlines'));
            this.paymentlinewidgets.push(l);
            if(this.numpadState){
                this.numpadState.resetValue();
            }
            this.line_refocus(l);
            this.recompute_discounts();
        },
        deleteLine: function(lineWidget) {
            this.pos.get('selectedOrder').recompute_discounts(
                lineWidget.payment_line.cashregister.attributes.journal_id[0]
            )
            this.currentPaymentLines.remove([lineWidget.payment_line]);
            lineWidget.destroy();
            this.recompute_discounts();
        },
    });


    module.PaypadExtraButtonWidget = module.PosBaseWidget.extend({
        template: 'PaypadExtraButtonWidget',
        init: function(parent, options){
            this._super(parent, options);
            this.action = options.action;
            this.title = options.title;
        },
        renderElement: function() {
            var self = this;
            this._super();
            $(this.$el[0]).text(this.title);
            this.$el.find('paypad-button').text(this.title);
            this.$el.click(function(){
                self.action();
            });
        },
    });

    module.ExtraButtonWidget = module.PosBaseWidget.extend({
        template: 'PaypadExtraWidget',
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get('selectedOrder');
            var button = new module.PaypadExtraButtonWidget(self,{
                pos: self.pos,
                pos_widget : self.pos_widget,
                title: 'INAPAM/Distinguished',
                action: function() {
                    var button = self.$el.find('button');
                    if (!button.hasClass('active')) {
                        order.is_customer_inapam = true;
                        button.addClass('active');
                    } else {
                        order.is_customer_inapam = false;
                        button.removeClass('active');
                    }
                    order.recompute_discounts();
                },
            });
            button.appendTo(self.$el);

            var button_el = self.$el.find('button');
            if (order.is_customer_inapam) {
                button_el.addClass('active');
            } else {
                button_el.removeClass('active');
            }
        },
    });
    
    module.ExtraButtonWidget2 = module.PosBaseWidget.extend({
        template: 'PaypadExtraWidget',
        renderElement: function() {
            var self = this;
            this._super();
            var order = this.pos.get('selectedOrder');
            var button = new module.PaypadExtraButtonWidget(self,{
                pos: self.pos,
                pos_widget : self.pos_widget,
                title: 'Descuento Especial',
                action: function() {
                    var button = self.$el.find('button');
                    var order = self.pos.get("selectedOrder");
                    if(order.getSelectedLine().specialDiscount!=0){
                        order.getSelectedLine().specialDiscount = 0;
                        order.recompute_discounts();
                    }else{
                        self.pos_widget.screen_selector.show_popup('pos-special-discount-popup');
                    }
                },
            });
            button.appendTo(self.$el);
        },
    });

    module.SalesmanPopupWidget = module.PopUpWidget.extend({
        template: 'SalesmanPopupWidget',
        renderElement: function(options){
            this._super();
            var self = this;

            var sellers = this.pos.get('sellers');
            var i;
            for (i in sellers) {
                $(self.$el.find('#seller_id')).append(
                    '<option value="' + sellers[i].id + '">' + sellers[i].name + '</option>'
                );
            }

            this.pos.get('orders').bind('pos-show-salesman-popup', _.bind(function(settings) {
                self.pos_widget.screen_selector.show_popup('pos-salesman-popup', settings);
            }), this);

            this.$el.find('.salesman-cancel').off('click').on('click', function() {
                self.pos_widget.screen_selector.close_popup();
            });
            
        },
        add_product: function(settings) {
            var seller_id = this.$el.find('#seller_id').val();
            settings.options.seller_id = seller_id;

            this.pos.get('selectedOrder').addProduct(
                settings.product, settings.options);

            this.pos_widget.screen_selector.close_popup();
            this.pos_widget.screen_selector.set_current_screen('products');
        },
        show: function(settings) {
            var self = this;
            this._super();

            this.$el.find('.salesman-confirm').off('click').on('click', function(e) {
                self.add_product(settings);
            });
            this.$el.find('#seller_id').focus();
            console.log(document.activeElement);
            this.$el.unbind("keypress");
            this.$el.keypress(function(e) {
                if(e.which == 13) {
                    self.add_product(settings);
                }
            });
        },
        reset_seller: function() {
            this.$el.find('#seller_id').val(0);
        },
        close: function() {
            this.__parentedParent.$('.searchbox input').val('').focus();
            console.log(document.activeElement);
            this._super();
            this.reset_seller();
        }
    });
    
    module.SpecialDiscountPopupWidget = module.PopUpWidget.extend({
        template: 'SpecialDiscountPopupWidget',
        renderElement: function(options){
            this._super();
            var self = this;

            this.$el.find('.special-discount-cancel').off('click').on('click', function() {
                self.pos_widget.screen_selector.close_popup();
            });
        },
        set_special_discount: function(settings){
            var order = this.pos.get('selectedOrder');
            var orderLine = order.getSelectedLine();
            if(this.$el.find('#special_discount_password').val()===this.pos.get("pos_config").special_discount_password){
                orderLine.specialDiscountType = this.$el.find('#special_discount_type').val();
                orderLine.specialDiscount = parseFloat(this.$el.find('#special_discount_amount').val() || 0);
                order.recompute_discounts();
            }
            else
                alert("Password incorrecto");
            this.pos_widget.screen_selector.close_popup();
        },
        show: function(settings) {
            var self = this;
            this._super();
            this.$el.find('#special_discount_type').val('amount');
            this.$el.find('#special_discount_amount').val(0);
            this.$el.find('#special_discount_password').val('');

            this.$el.find('.special-discount-confirm').off('click').on('click', function(e) {
                self.set_special_discount(settings);
            });
            this.$el.unbind("keypress");
            this.$el.keypress(function(e) {
                if(e.which == 13) {
                    self.set_special_discount(settings);
                }
            });
        },
        close: function() {
            this._super();
        }
    });

    module.PosWidget = module.PosWidget.extend({
        build_widgets: function() {
            var self = this;
            this._super();

            this.extra_btn = new module.ExtraButtonWidget(this, {});
            this.extra_btn.replace($('#placeholder-ExtraButtonWidget'));
            this.extra_btn2 = new module.ExtraButtonWidget2(this, {});
            this.extra_btn2.replace($('#placeholder-ExtraButtonWidget2'));

            this.salesman_popup = new module.SalesmanPopupWidget(this, {});
            this.salesman_popup.appendTo($('.point-of-sale'));
            this.salesman_popup.hide();
            
            this.special_discount_popup = new module.SpecialDiscountPopupWidget(this, {});
            this.special_discount_popup.appendTo($('.point-of-sale'));
            this.special_discount_popup.hide();

            this.screen_selector.popup_set['pos-salesman-popup'] = this.salesman_popup;
            this.screen_selector.popup_set['pos-special-discount-popup'] = this.special_discount_popup;
        }
    });


    module.ProductCategoriesWidget = module.ProductCategoriesWidget.extend({
    
        clear_search: function(){
             var self = this;
            this._super();
 
            this.__parentedParent.__parentedParent.$('#seller_id').focus();
        },



    });
}
