import json
import matplotlib.pyplot as plt 


def split_date(date:str) -> tuple:
		return (date[0:4],date[5:7],date[8:10])

def compare_date(a:str,b:str)->bool:
	'''
	Takes two Strings a,b that represent dates in the form yyyy-mm-dd hh:mm:ss UTC and returns if a is on an earlier calendar day than b
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

	#this is so definitely bad code but idk how to fix...
	
class parser:
	def __init__(self):
		self.minDate = "3000-12-31"
		self.maxDate = "0000-01-01"
		self.stats = {}
		self.hasParsed = False
		self.total_snaps = 0
		

	def parse_hist(self, cont : dict):
		keys = []
		for k in cont.keys():
			keys.append(k)
		rec_history = cont[keys[0]]
		sent_history = cont[keys[1]]
		self.count_occur(rec_history,True)
		self.count_occur(sent_history,False)
		self.hasParsed = True

	def count_occur(self,history : list, isReceived : bool):
		doublecount = 0
		keyword = ("To","From")[isReceived]
		lastUser = lastTime = ""
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
		if compare_date(self.maxDate,newDate): self.maxDate = newDate
		if compare_date(newDate, self.minDate): self.minDate = newDate

	def get_sorted(self):
		res = []
		for uname in sorted(self.stats,key = self.stats.get,reverse=True):
			res.append((uname,self.stats[uname]))
		return res

	
	
	def export(self, fname:str = "snapExport"):
		'''
		write stats to valid csv file in working directory, will be saved as "{fname}.csv"
		'''

		fname+=".csv"
		sorted_stats = self.get_sorted()
		out = open(fname,'w')
		out.write(f"Snap data from {self.minDate} to {self.maxDate}\n")
		for (uname,value) in sorted_stats:
			out.write(f"{uname},{value}\n")
		out.close()

	def makePie(self, fname="pieExport.png"):
		fig_X = 15
		fig_Y = 10
		plt.style.use('dark_background')
		sorted_stats = self.get_sorted()
		data = []
		labels = []
		explode = []
		for (uname,value) in sorted_stats:
			data.append(value)
			labels.append(f"{uname}\t ({value})")
			explode.append((1-value/self.total_snaps)/8)
		fig = plt.figure(figsize = (fig_X,fig_Y))

		plt.pie(data,explode=explode)
		plt.legend(labels,bbox_to_anchor=(1.01,1))
		#plt.show()
		plt.savefig(fname)



	def __repr__(self) -> str:
		sorted_stats = self.get_sorted()
		res = f"Snap stats from {self.minDate} to {self.maxDate} \n"
		for (uname,value) in sorted_stats:
			res+=(f"username: {uname}\t {value} \n")
		return res



chat_hist = json.load(open("chat_history.json"))
snap_hist = json.load(open("snap_history.json"))

worker = parser()
worker.parse_hist(snap_hist)
#worker.parse_hist(chat_hist)
worker.export()
worker.makePie()
