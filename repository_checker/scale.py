import yaml

DEBUG=False

def load_file(path):
	obj = {}
	with open(path) as fd:
		content = fd.read()
		obj = yaml.load(content, Loader=yaml.Loader)
	return obj

def print_debug(*args):
	if DEBUG:
		print(*args)

def compare_obj(left, right):
	if isinstance(left, type(right)) == False:
		return True
	if isinstance(left, dict):
		if len(right) != len(left):
			return True
		for k in left:
			if k not in right:
				print_debug (k, "wrong")
				return True
			print_debug (k, ">>")
			if compare_obj(left[k], right[k]):
				return True
			print_debug (k, "<<")
	elif isinstance(left, list):
		if len(right) != len(left):
			print_debug ("not same length", len(right), len(left))
			for i in range(len(left)):
				print_debug("EN", left[i]["name"])
			for i in range(len(right)):
				print_debug("other", right[i]["name"])

			return True
		for i in range(len(left)):
			print_debug (i, ">>")
			if compare_obj(left[i], right[i]):
				return True
			print_debug (i, "<<")
	return False

def compare(en_file_path, other_file_path):
	en_obj = load_file(en_file_path)
	other_obj = load_file(other_file_path)
	return compare_obj(en_obj, other_obj)
