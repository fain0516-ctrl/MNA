const {add}=require('./math'); function search(list,q){return list.filter(x=>x.includes(q));}
module.exports={search,total:(a)=>a.reduce(add,0)};
