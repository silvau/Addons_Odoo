function openerp.qweb_pos_ticket(instance){ //module is instance.point_of_sale
    module=instance.point_of_sale;
    _t = instance.web._t;

    console.log("qweb pos ticket");
    module.PaymentScreenWidget=module.ScreenWidget.extend({

        show: function () {

             console.log("Click on back_buton");
             this._super();
             var self = this;

             this.back_button = this.add_action_button({
                    label: _t('Back'),
                    icon: '/point_of_sale/static/src/img/icons/png48/go-previous.png',
                    click: function(){  
                        self.pos_widget.screen_selector.set_current_screen(self.back_screen);
                        $('#numpad-return').removeAttr('disabled');
                    },
             });
    },

});

}


