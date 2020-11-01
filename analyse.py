import json						#for parsing
import os						#for relative path
import matplotlib.pyplot as plt	#for pie chart
import argparse					#for command line args

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

def split_date(date:str) -> tuple:
		return (date[0:4],date[5:7],date[8:10])

def compare_date(a:str,b:str)->bool:
	'''
	Takes two datetime Strings a and b in the form
	"yyyy-mm-dd hh:mm:ss UTC"
	and returns whether a is on an earlier calendar
	day than b
	'''
	if(b.strip() == ""): return True
	if(a.strip() == ""): return False
	yearA,monthA,dayA = split_date(a)
	yearB,monthB,dayB = split_date(b)
	if yearA<yearB: return True
	if yearB<yearA: return False
	if monthA<monthB: return True
	if monthB<monthA: return False
	if dayA<dayB: return True
	return False
	#this is so clearly bad code but idk how to fix...
	
class parser:
	def __init__(self):
		self.minDate = "3000-12-31"
		self.maxDate = "0000-01-01"
		self.stats = {}
		self.hasParsed = False
		self.total_snaps = 0

	def parse_hist(self, cont : dict):
		'''
		take some parsed xxxx_history.json files content as
		dict and count through the snaps in it
		'''
		keys = []
		for k in cont.keys():
			keys.append(k)
		rec_history = cont[keys[0]]
		sent_history = cont[keys[1]]
		self.count_occur(rec_history,True)
		self.count_occur(sent_history,False)
		self.hasParsed = True

	def count_occur(self,history : list, isReceived : bool):
		'''
		main method that evaluates list of snap entries passed by parse_hist()
		- stores number of snaps per username in self.stats
		- stores total amount of evaluated snaps in self.total_snaps
		'''
		keyword = ("To","From")[isReceived]
		lastUser = lastTime = "" #used to filter out some strange duplicate entries in json files
		for snap in history: #snaps are dicts with keys "From" "Media Type"(useless) "Created" (date, can be compared with dateCompare method)
			user = snap[keyword].lower()
			date = snap["Created"]

			if(user == lastUser and date == lastTime): continue#filter apparent double snaps??
			lastUser, lastTime = user,date
			self.update_date_range(date)
			if user in self.stats.keys():
				self.stats[user] += 1
			else:
				self.stats[user] = 1
			self.total_snaps +=1

	def update_date_range(self,newDate:str):
		'''
		called with a datetime string, if necessary updates
		earliest/latest seen calendar date
		'''
		if compare_date(self.maxDate,newDate): self.maxDate = newDate
		if compare_date(newDate, self.minDate): self.minDate = newDate

	def get_sorted(self)->list:
		'''
		return list of tuples of form
		"(username,self.stats[username])"
		sorted by value (#of snaps)
		'''
		res = []
		for uname in sorted(self.stats,key = self.stats.get,reverse=True):
			res.append((uname,self.stats[uname]))
		return res

	
	
	def export(self, fname:str = f"snapExport"):
		'''
		write stats to valid csv file in working directory,
		will be saved as "{fname}.csv"
		'''
		if not self.hasParsed:
			raise RuntimeError("Cant export without parsing")
		fname= f"{SCRIPT_PATH}/{fname}.csv"
		sorted_stats = self.get_sorted()
		out = open(fname,'w')
		out.write(f"Snap data from {self.minDate} to {self.maxDate}\n")
		for (uname,value) in sorted_stats:
			out.write(f"{uname},{value}\n")
		out.close()

	def makePie(self, fname=f"pieExport"):
		'''
		Creates pie chart of data in self.stats
		using matplotlib, exports the image
		as [fname].png to the directory of the
		json files (SCRIPT_PATH)
		'''
		fname= f"{SCRIPT_PATH}/{fname}.png" #parse filename
		fig_X = 15
		fig_Y = 10
		plt.style.use('dark_background') #darkmode is superior
		sorted_stats = self.get_sorted() 
		data = []
		labels = []
		explode = []
		control_total = 0 # trust issues lmao

		for (uname,value) in sorted_stats:
			control_total+=value
			data.append(value)
			labels.append(f"{uname} ({value})")
			explode.append((1-value/self.total_snaps)/5)
		
		if self.total_snaps != control_total:
			raise ValueError("nonononono something went horribly wrong")

		explode.append(0) #dummy entries for total at bottom of legend
		data.append(0)
		labels.append(f"Total: {self.total_snaps}")

		fig = plt.figure(figsize = (fig_X,fig_Y)) #create plot
		plt.pie(data,explode=explode)	#draw pie chart
		plt.legend(labels,bbox_to_anchor=(1.01,1)) #position names (=legend)
		plt.savefig(fname)	#export

	def __repr__(self) -> str:
		'''
		never used, but makes sure
		print(parser) returns something
		sensible
		'''
		sorted_stats = self.get_sorted()
		res = f"Snap stats from {self.minDate} to {self.maxDate} \n"
		for (uname,value) in sorted_stats:
			res+=(f"username: {uname}\t{value} \n")
		return res



def main():
	'''
	main method, gets executed when
	script is called from command line
	'''
	#pass args -> sole purpose of being able to specifying custom dir
	arg_parser = argparse.ArgumentParser(description="Get pie chart from snap data :)")
	arg_parser.add_argument(
		'--dir',
		metavar = '/some/path',
		type=str,
		default=SCRIPT_PATH,
		help='directory of json files and output dir for png and csv',
		)
	args = arg_parser.parse_args()

	SCRIPT_PATH = args.dir

	worker = parser() #intialize

	failcounter = 0 #keep track of how many errors excepted

	try:
		chat_hist = json.load(open(f"{SCRIPT_PATH}/chat_history.json"))
		worker.parse_hist(chat_hist)
	except FileNotFoundError:
		failcounter+=1
		print("[Warning] chat_history.json not found -> ignoring")

	try:
		snap_hist = json.load(open(f"{SCRIPT_PATH}/snap_history.json"))
		worker.parse_hist(snap_hist)
	except FileNotFoundError:
		failcounter+=1
		print("[Warning] snap_history.json not found -> ignoring")

	if(failcounter>1):
		print("[FATAL] neither file found, nothing to process\n shutting down...\n")
	else:
		worker.export() #exports .csv file with usernames and number of snaps
		worker.makePie() #exports  pieExport.png with pie graph :)
