// Shared by SNBT generation and the live server probe, so they test the same expression.
module.exports=spec=>{
  if(typeof spec==='string'&&spec.startsWith('#')) return 'item_tag('+spec.slice(1)+')';
  if(!spec?.any?.length)throw Error('Empty any-of filter');
  return 'or('+spec.any.map(id=>'item('+id+')').join('')+')';
};
