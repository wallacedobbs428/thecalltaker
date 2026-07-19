(function(root,factory){
  var api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.TCTCheckoutState=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  var REQUIRED_CARD_FIELDS=['cardNumber','expirationDate','cvv'];

  function clean(value){return typeof value==='string'?value.trim():'';}

  function identityReady(identity){
    if(!identity)return false;
    var email=clean(identity.email);
    var phone=clean(identity.phone).replace(/\D/g,'').replace(/^1(?=\d{10}$)/,'');
    return Boolean(
      clean(identity.givenName)&&
      clean(identity.familyName)&&
      clean(identity.cardholderName)&&
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)&&
      phone.length===10
    );
  }

  function cardReady(cardFields){
    return Boolean(cardFields&&REQUIRED_CARD_FIELDS.every(function(field){return cardFields[field]===true;}));
  }

  function checkoutReady(state){
    return Boolean(
      state&&
      state.cardMounted===true&&
      cardReady(state.cardFields)&&
      identityReady(state.identity)&&
      state.consent===true&&
      state.submitting!==true
    );
  }

  function recordCardEvent(cardFields,event){
    var next=Object.assign({},cardFields||{});
    var detail=event&&event.detail?event.detail:event;
    if(detail&&REQUIRED_CARD_FIELDS.indexOf(detail.field)!==-1&&detail.currentState){
      next[detail.field]=detail.currentState.isCompletelyValid===true;
    }
    return next;
  }

  return {REQUIRED_CARD_FIELDS:REQUIRED_CARD_FIELDS.slice(),identityReady:identityReady,cardReady:cardReady,checkoutReady:checkoutReady,recordCardEvent:recordCardEvent};
});
