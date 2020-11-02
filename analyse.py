import json  # for parsing
import os
from os import O_PATH  # for relative path
import matplotlib.pyplot as plt  # for pie chart
import argparse

from matplotlib.pyplot import show  # for command line args

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
OUT_PATH = SCRIPT_PATH

def compare_date(a: str, b: str) -> bool:
	'''
	Takes two datetime Strings a and b in the form
	"yyyy-mm-dd hh:mm:ss UTC"
	and returns whether a is on an earlier calendar
	day than b
	'''
	if(b.strip() == "" or a.strip() == ""):
		raise ValueError("Empty String cant be compared")
	return a[:10]<b[:10]

class parser:
	def __init__(self):
		self.minDate = "3000-12-31"
		self.maxDate = "0000-01-01"
		self.stats = {}
		self.hasParsed = False
		self.total_snaps = 0

	def parse_hist(self, cont: dict):
		'''
		take some parsed xxxx_history.json files content as
		dict and count through the snaps in it
		'''
		keys = []
		for k in cont.keys():
			keys.append(k)
		rec_history = cont[keys[0]]
		sent_history = cont[keys[1]]
		self.count_occur(rec_history, True)
		self.count_occur(sent_history, False)
		self.hasParsed = True

	def count_occur(self, history: list, isReceived: bool):
		'''
		main method that evaluates list of snap entries passed by parse_hist()
		- stores number of snaps per username in self.stats
		- stores total amount of evaluated snaps in self.total_snaps
		'''
		keyword = ("To", "From")[isReceived]
		# used to filter out some strange duplicate entries in json files
		lastUser = lastTime = ""
		# snaps are dicts with keys "From" "Media Type"(useless) "Created" (date, can be compared with dateCompare method)
		for snap in history:
			user = snap[keyword].lower()
			date = snap["Created"]
			if(user == lastUser and date == lastTime):
				continue  # filter apparent double snaps??
			lastUser, lastTime = user, date
			self.update_date_range(date)
			if user in self.stats.keys():
				self.stats[user] += 1
			else:
				self.stats[user] = 1
			self.total_snaps += 1

	def update_date_range(self, newDate: str):
		'''
		called with a datetime string, if necessary updates
		earliest/latest seen calendar date
		'''
		if compare_date(self.maxDate, newDate):
			self.maxDate = newDate
		if compare_date(newDate, self.minDate):
			self.minDate = newDate

	def get_sorted(self) -> list:
		'''
		return list of tuples of form
		"(username,self.stats[username])"
		sorted by value (#of snaps)
		'''
		res = []
		for uname in sorted(self.stats, key=self.stats.get, reverse=True):
			res.append((uname, self.stats[uname]))
		return res

	def export(self, fname: str = f"snapExport"):
		'''
		write stats to valid csv file in working directory,
		will be saved as "{fname}.csv"
		'''
		if not self.hasParsed:
			raise RuntimeError("Cant export without parsing!")
		fname = f"{O_PATH}/{fname}.csv"
		sorted_stats = self.get_sorted()
		out = open(fname, 'w')
		out.write(f"Snap data from {self.minDate} to {self.maxDate}\n")
		for (uname, value) in sorted_stats:
			if SHOWCASE:
				uname = "*****"
			out.write(f"{uname},{value}\n")
		out.close()

	def makePie(self, fname=f"pieExport"):
		'''
		Creates pie chart of data in self.stats
		using matplotlib, exports the image
		as [fname].png to the directory of the
		json files (SCRIPT_PATH)
		'''
		if not self.hasParsed:
			raise RuntimeError("Cant evaluate without parsing!")
		fname = f"{O_PATH}/{fname}.png"  # parse filename
		fig_X = 17
		fig_Y = 12
		plt.style.use('dark_background')  # darkmode is superior
		sorted_stats = self.get_sorted()
		data = []
		labels = []
		explode = []
		control_total = 0  # trust issues lmao

		for (uname, value) in sorted_stats:
			if SHOWCASE:
				uname = "*******"
			control_total += value
			data.append(value)
			labels.append(f"{uname} ({value})")
			explode.append((1-value/self.total_snaps)/5)

		if self.total_snaps != control_total:
			raise ValueError("nonononono something went horribly wrong")

		explode.append(0)  # dummy entries for total at bottom of legend
		data.append(0)
		labels.append(f"Total: {self.total_snaps}")

		fig = plt.figure(figsize=(fig_X, fig_Y))  # create plot
		plt.title(f"Snap Stats from {self.minDate[:10]} to {self.maxDate[:10]}")
		plt.pie(data, explode=explode)  # draw pie chart
		plt.legend(labels, bbox_to_anchor=(1.01, 1.15))
		plt.savefig(fname)  # export

	def __repr__(self) -> str:
		'''
		never used, but makes sure
		print(parser) returns something
		sensible
		'''
		sorted_stats = self.get_sorted()
		res = f"Snap stats from {self.minDate} to {self.maxDate} \n"
		for (uname, value) in sorted_stats:
			res += (f"username: {uname}\t{value} \n")
		return res


def main():
	'''
	main method, gets executed when
	script is called from command line
	'''
	global SCRIPT_PATH
	global O_PATH
	global SHOWCASE
	NOTSETFLAG = "**NOTSET**"
	# pass args -> sole purpose of being able to specifying custom dir
	arg_parser = argparse.ArgumentParser(
		description="Get pie chart from snap data :)")
	arg_parser.add_argument(
		'--dir',
		metavar='PATH',
		type=str,
		default=SCRIPT_PATH,
		help='path to location of json files, defaults to script location',
	)
	arg_parser.add_argument(
		'--o',
		metavar='PATH',
		type=str,
		default=NOTSETFLAG,
		help='output directory for csv and png files, defaults to json directory',
	)
	arg_parser.add_argument(
		'--showcase',
		action='store_true',
		help='Dont show names, mainly to generate pics for README'
	)
	arg_parser.add_argument(
		'--csv',
		action='store_true',
		help='Generate a csv file with the computed stats'
	)
	args = arg_parser.parse_args()
	SHOWCASE = args.showcase

	orig_script_dir = SCRIPT_PATH
	SCRIPT_PATH = args.dir
	if args.o == NOTSETFLAG:
		O_PATH = SCRIPT_PATH
	elif args.o == ".":
		O_PATH = orig_script_dir
	else:
		O_PATH = args.o

	worker = parser()  # intialize

	failcounter = 0  # keep track of how many errors excepted

	try:
		chat_hist = json.load(open(f"{SCRIPT_PATH}/chat_history.json"))
		worker.parse_hist(chat_hist)
	except FileNotFoundError:
		failcounter += 1
		print("[Warning] chat_history.json not found -> ignoring")

	try:
		snap_hist = json.load(open(f"{SCRIPT_PATH}/snap_history.json"))
		worker.parse_hist(snap_hist)
	except FileNotFoundError:
		failcounter += 1
		print("[Warning] snap_history.json not found -> ignoring")

	if(failcounter > 1):
		print("[FATAL] neither file found, nothing to process\n shutting down...\n")
	else:
		if(args.csv):
			worker.export()  # exports .csv file with usernames and number of snaps
		worker.makePie()  # exports  pieExport.png with pie graph :)


if __name__ == '__main__':
	main()
