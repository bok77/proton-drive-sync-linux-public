import assert from 'node:assert/strict';
import {consumeEvents} from './sdk_event_iterator.mjs';
const lines=[];
async function* synthetic(scope){yield {type:'node_created',treeEventScopeId:scope,eventId:'e1',nodeUid:'n1',secret:'DROP_THIS'};}
await consumeEvents({iterateEvents:synthetic,scopeId:'scope',cursor:'base',signal:new AbortController().signal,
 emit:async event=>lines.push(JSON.stringify({type:'sdk_event',scope:'scope',event}))});
assert.equal(lines.length,1);
assert.equal(JSON.parse(lines[0]).event.eventId,'e1');
assert.ok(!lines[0].includes('DROP_THIS'));
console.log('SDK_EVENT_IPC_ENVELOPE_PASS');
