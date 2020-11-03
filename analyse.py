import json  # for parsing
import os # for relative path
import matplotlib.pyplot as plt  # for pie chart
import argparse # for command line args

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
OUT_PATH = SCRIPT_PATH
SHOWCASE = False

def compare_date(a: str, b: str) -> bool:
	'''
	Takes two datetime Strings a and b in the form
	"yyyy-mm-dd hh:mm:ss UTC"
	and returns whether a is on an earlier calendar
	day than b
	'''
	if(b.strip() == "" or a.strip() == ""):
		raise ValueError("Empty String cant be compared")
	return a[:10] < b[:10]


class parser:
	#TODO refactor whole counting stuff so it stores person objects with their properties
	def __init__(self,cmap="plasma"):
		'''
		initialize starting values of instance variables
		'''
		self.minDate = "3000-12-31"
		self.maxDate = "0000-01-01"
		self.stats = {}
		self.hasParsed = False
		self.total_snaps = 0
		self.cmap = cmap

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
				self.stats[user].add_snap(isReceived)
			else:
				self.stats[user] = person(user, numRec=isReceived, numSen= not isReceived)
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
		names = list(self.stats.keys())
		names.sort(key = lambda x: self.stats[x].total_snaps, reverse=True)
		res = []
		for key in names:
			res.append(self.stats[key])
		return res

	def export(self, fname: str = f"SnapVisualizer_csv_data"):
		'''
		write stats to valid csv file in working directory,
		will be saved as "{fname}.csv"
		'''
		if not self.hasParsed:
			raise RuntimeError("Cant export without parsing!")
		fname = f"{OUT_PATH}/{fname}.csv"
		sorted_stats = self.get_sorted()
		out = open(fname, 'w')
		out.write(f"Snap data from {self.minDate} to {self.maxDate},total,received,sent\n")
		for person_object in sorted_stats:
			uname = person_object.username
			if SHOWCASE:
				uname = "*****"
			out.write(f"{uname},{person_object.total_snaps},{person_object.rec_from},{person_object.sent_to}\n")
		out.close()

	def make_pie(self, fname=f"SnapVisualizer_pie_chart"):
		'''
		Creates pie chart of data in self.stats
		using matplotlib, exports the image
		as [fname].png to the directory of the
		json files (SCRIPT_PATH)
		'''
		outer_size = 0.3
		if not self.hasParsed:
			raise RuntimeError("Cant evaluate without parsing!")
		fname = f"{OUT_PATH}/{fname}.png"  # parse filename
		fig_Y = 16
		fig_X = fig_Y+3
		plt.style.use('dark_background')  # darkmode is superior
		sorted_stats = self.get_sorted()
		data = []
		data2 = []
		labels = []
		explode = []
		explode2 = []
		control_total = 0  # trust issues lmao
		cmap = plt.get_cmap(self.cmap)
		in_col_src =  ((10,20),(50,60),(90,100))
		out_col_src = (0,40,80)
		out_cols = []
		in_cols = []
		
		iter_count = 0
		for person_object in sorted_stats:
			uname = person_object.username

			if SHOWCASE:
				uname = "*******"

			control_total += person_object.total_snaps

			data.append(person_object.total_snaps)
			labels.append(f"{uname} ({person_object.total_snaps})")
			data2.append(person_object.rec_from)
			data2.append(person_object.sent_to)

		#	explode.append((1-person_object.total_snaps/self.total_snaps)/5)
			out_cols.append(out_col_src[iter_count%len(out_col_src)])
			in_cols.append(in_col_src[iter_count%len(in_col_src)][0])
			in_cols.append(in_col_src[iter_count%2][1])

			iter_count+=1

		if self.total_snaps != control_total:
			print(self.total_snaps,control_total)
			#raise ValueError("nonononono something went horribly wrong")

		#explode.append(0)  # dummy entries for total at bottom of legend
		data.append(0)
		labels.append(f"Total: {self.total_snaps}")

		fig = plt.figure(figsize=(fig_X, fig_Y))  # create plot
		plt.title(
			f"Snap Stats from {self.minDate[:10]} to {self.maxDate[:10]}")
		
		plt.pie(
			data,
			colors=cmap(out_cols),
			radius =1,
			wedgeprops=dict(
				width=outer_size,
				#edgecolor="k"
				)
			)  # draw pie chart
		plt.pie(
			data2,
			colors=cmap(in_cols),
			radius =1-outer_size,
			wedgeprops=dict(
				width=outer_size,
				#edgecolor="k"
				)
			)
		
		plt.legend(labels, bbox_to_anchor=(1, 1.1))
		
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
	global OUT_PATH
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
		OUT_PATH = SCRIPT_PATH
	elif args.o == ".":
		OUT_PATH = args.o
	else:
		OUT_PATH = args.o

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
		worker.make_pie()  # exports  pieExport.png with pie graph :)



class person:
	def __init__(self,name,numRec:int = 0, numSen:int = 0):
		self.username = name
		self.sent_to = numSen
		self.rec_from = numRec
		self.total_snaps = self.sent_to+self.rec_from
	
	def add_snap(self,received : bool):
		self.total_snaps +=1
		if received:
			self.rec_from +=1
		else:
			self.sent_to +=1
	def __repr__(self) -> str:
		return f"user: {self.username},\n\treceived snaps from this user: {self.rec_from},\n\tsent to this user: {self.sent_to}\n\ttotal: {self.total_snaps}"


if __name__ == '__main__':
	main()

