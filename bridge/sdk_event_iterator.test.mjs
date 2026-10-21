import assert from 'node:assert/strict';
import {consumeEvents} from './sdk_event_iterator.mjs';
const signal = new AbortController().signal;
const received=[];
async function* events(scope,cursor){assert.equal(scope,'test-scope');assert.equal(cursor,'verified');yield {type:'node_updated',treeEventScopeId:scope,nodeUid:'n',eventId:'e2',private:'NEVER_ECHO'};}
assert.equal(await consumeEvents({iterateEvents:events,scopeId:'test-scope',cursor:'verified',emit:async e=>received.push(e),signal}),1);
assert.equal(JSON.stringify(received).includes('NEVER_ECHO'),false);
async function* invalid(){yield {type:'fast_forward',treeEventScopeId:'test-scope',eventId:'e3'};}
await assert.rejects(consumeEvents({iterateEvents:invalid,scopeId:'test-scope',cursor:'verified',emit:async()=>{},signal}),/SDK_ITERATOR_BLOCKED/);
await assert.rejects(consumeEvents({iterateEvents:events,scopeId:'test-scope',cursor:'',emit:async()=>{},signal}),/iterator_configuration_required/);
console.log('SDK_EVENT_ITERATOR_ISOLATED_PASS');
