import sqlite3

netDbSource = sqlite3.connect('javainfantrys1.db')
netDb = netDbSource.cursor()
pyDbSource = sqlite3.connect('../../javsdt_collect/javainfantrys.db')
pyDb = pyDbSource.cursor()
print("打开数据库！")

listRows = pyDb.execute("SELECT NumPref, Status from Statistics")
for row in listRows:
    numPref = row[0]
    Status = row[1]
    if Status:
        netDb.execute('UPDATE Statistics set Status = ' + Status + ' where NumPref="' + numPref + '"')
        # netDb.execute('UPDATE Statistics set Status = 4 where NumPref= "NHDTA"')

netDbSource.commit()
netDbSource.close()
pyDb.close()