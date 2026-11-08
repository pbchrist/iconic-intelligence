const assert = require('assert');
const state = require('../static/chat-state.js');
const memory = new Map();
const storage = {
  setItem: (key,value)=>memory.set(key,value),
  getItem: (key)=>memory.has(key)?memory.get(key):null
};
const north = [{q:'Was it 97%?', a:'Scorecard says 97% [2].', sources:[
  {n:2,id:11,rel:'vendors/scorecard.md',title:'Vendor scorecard',
   snippet:'Do not persist private document excerpt'}]}];
assert(state.save(storage,'northline-supply',{history:north,html:'',sources:{},picked:true}));
assert(state.save(storage,'hollis-reyes',{history:[{q:'Hi',a:'Hello'}],html:'',sources:{},picked:true}));
const recovered=state.load(storage,'northline-supply');
assert.deepStrictEqual(recovered.history[0].sources,[{n:2,id:11,rel:'vendors/scorecard.md',title:'Vendor scorecard'}]);
assert(!JSON.stringify(recovered).includes('Do not persist private'));
assert(!JSON.stringify(state.load(storage,'hollis-reyes')).includes('scorecard'));
console.log('CHAT_SOURCE_MAPPING_PERSISTS_PER_WORKSPACE_PASS');
