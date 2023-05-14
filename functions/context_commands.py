import pickle as pkl
import urllib.request
import urllib.parse
import webbrowser
import re
import os
import subprocess

# open hash
context_table = pkl.load(open('data\context_table.pkl', 'rb'))

# standard program list
#std_program = ["task manager", "explorer", "file explorer", "edge", "notepad"]

def get_context(intent):
	return context_table[intent]

def process_expression(expr):
	
	# 0. Maximum 50 characters allowed
	
	if len(expr) > 50:
		return -1
	
	# 1. Separate operators (if required)
	
	new_expr = expr
	if "+" in new_expr and not " + " in new_expr:
		new_expr = new_expr.replace("+", " + ")
	if "-" in new_expr and not " - " in new_expr:
		new_expr = new_expr.replace("-", " - ")
	if "/" in new_expr and not " / " in new_expr:
		new_expr = new_expr.replace("/", " / ")
	if "*" in new_expr and not " * " in new_expr:
		new_expr = new_expr.replace("*", " * ")
	
	
	# 2. Deal with power
	
	pwr_count = 0
	for factor in new_expr.split(" "):
		if "^" in factor:
			pwr_count = sum([1 for chr in factor if chr == "^"])
		else:
			pwr_count = 0
		
		if pwr_count > 2:
			return -1
	
	# 3. Check factor size
	
	for factor in new_expr.split(" "):
		if len(factor) > 10:
			return -1
	
	# 4. Replace "^" with "**"
	
	new_expr = new_expr.replace("^", "**")
	
	return new_expr

def context_commands(user_input, context):
	
	# runs different commands depending on the context
	
	if context == "google": # search on google task
	
		# get search item
		search_item = user_input.split("about")[1].strip()
		search_item = search_item[:-1] if search_item[-1] == "?" else search_item
            
		url = 'https://www.google.com/search'

		values = {'q':search_item}

		data = urllib.parse.urlencode(values) # getting web page data and encoding it to URL format

		webbrowser.open(url + '?' + str(data))
	
	elif context == "wikipedia": # search on wikipedia task
	
		# get search item
		search_item = user_input.split("about")[1].strip()
		search_item = search_item[:-1] if search_item[-1] == "?" else search_item
            
		url = 'https://en.wikipedia.org/wiki/'

		data = re.sub(" ", "_", search_item) # getting web page data and encoding it to URL format

		webbrowser.open(url + str(data))
	
	elif context == "program_open_std": # opening standard Windows program task
	
		program_item = user_input.lower().split("open")[1].strip()
		program_item = program_item[:-1] if program_item[-1] == "?" else program_item
		
		#if program_item in std_program:
		if "task manager" in program_item:
			subprocess.run(["powershell", "-Command", "taskmgr"])
		elif "explorer" in program_item:
			os.system("cmd /c explorer")
		elif "edge" in program_item:
			os.system("cmd /c start msedge")
		elif "notepad" in program_item:
			subprocess.run(["powershell", "-Command", "notepad"])
	
	elif context == "expression_calc": # calculating math expression task
	
		if "expression" in user_input:
			expr = user_input.lower().split("expression")[1].strip()
		else:
			expr = user_input.lower().split("calculate")[1].strip()
		expr = expr[:-1] if expr[-1] == "?" else expr
		
		return eval(process_expression(expr))
	
	else: # if no task is found to given input
	
		return -1

if __name__ == "__main__":
	
	expr = process_expression("144 + 277^123 - 785142^329^448 + 6^41")
	print(expr)