openerp.pos_session_sequence = function(instance) {
  var module = instance.point_of_sale;
  
  console.log("pos session sequence");
  
  module.PosModel = module.PosModel.extend({
    initialize: function(session, arguments){
      var self = this;
      this.session_seq_ready = $.Deferred();
      
      module.PosModel.__super__.initialize.call(self, session, arguments)
      
      self.ready
        .done(function(){
          self.fetch(
            'pos.config',
            ["session_seq_next", "session_seq_prefix", "session_seq_fill","journal_id"],
            [['id', '=', self.get("pos_session").config_id[0]]]
          ).then(function(configs){
            var pos_config = configs[0];
            self.session_seq_next   = pos_config.session_seq_next;
            self.session_seq_prefix = pos_config.session_seq_prefix;
            self.session_seq_fill   = pos_config.session_seq_fill;
            return self.fetch('account.journal',["lugar"],[['id', '=', pos_config.journal_id[0]]])
          }).then(function(journals){
            var journal = journals[0];
            console.log(journal.lugar);
            self.lugar  = journal.lugar;
            console.log("El self.lugar:"+self.lugar);
            self.session_seq_ready.resolve();
          })

        });
    },
    
    /*_flush: function(index){
      var self = this;
      (new instance.web.Model('pos.config').call('update_sequence', {
        id:  self.get("pos_session").config_id[0],
        seq: self.session_seq_next
      }, undefined, { shadow:true }))
        .fail(function(unused, event){
          event.preventDefault();
        });
      return module.PosModel.__super__._flush.call(self, index);
    }*/
  });
  
  module.Order = module.Order.extend({
  
    pad: function(n, width) {
      n = n + '';
      while(n.length<width)
        n = '0' + n;
      return n;
    },
    
    generateTicketName: function(next, prefix, fill){
      return prefix + this.pad(next, fill);
    },
    
    initialize: function(arguments){
      var self = this;
       
      console.log("override order initialize");
      module.Order.__super__.initialize.call(self, arguments);
      
      self.pos.session_seq_ready
        .done(function(){
          console.log(self.pos.session_seq_prefix);
          self.set({
            name: self.generateTicketName(self.pos.session_seq_next++, 
              self.pos.session_seq_prefix, self.pos.session_seq_fill)
          });   
          self.set({
            lugar: self.pos.lugar
          });
      });
      return this;
    }
  });
}
