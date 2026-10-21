// Synthetic provider-independent fixture. Prints exactly one redacted event line.
import {consumeEvents} from './sdk_event_iterator.mjs';
async function* fixture(scope){yield {type:'node_updated',treeEventScopeId:scope,eventId:'fixture-next',nodeUid:'fixture-node',private:'NEVER_ECHO'};}
await consumeEvents({iterateEvents:fixture,scopeId:'fixture-scope',cursor:'fixture-base',signal:new AbortController().signal,
 emit:async event=>process.stdout.write(JSON.stringify({type:'sdk_event',scope:'fixture-scope',event})+'\n')});
