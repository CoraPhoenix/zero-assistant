import json
import pickle as pkl

intents = json.loads(open('intent_en.json').read())

context_trigger = {}

for intent in intents['intents']:
	tag = intent["tag"]
	context = intent["context_set"]
	
	context_trigger[tag] = context
	
pkl.dump(context_trigger, open('context_table.pkl', 'wb'))