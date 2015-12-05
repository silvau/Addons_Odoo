openerp.pos_sidebar=function(instance){ //module is instance.point_of_sale

    module=instance.point_of_sale


    module.ReceiptScreenWidget.include({
        template: 'ReceiptScreenWidget',

        show_numpad:     true,
        show_leftpane:   false,

//        init: function(parent, options) {
//            this._super(parent,options);
//        },
    });


}
