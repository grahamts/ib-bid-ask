from ib.ext.Contract import Contract
from ib.opt import ibConnection
from time import sleep
import csv
import datetime

now = datetime.datetime.now()
outfile = open("DailyBidAskSpread " + now.strftime("%m-%d-%y") + ".csv", "wb")
writer = csv.writer(outfile, delimiter = ' ')
contractDict = {}
bidAsk = {}
prettyBidAsk = {}

# print all messages from TWS
def watcher(msg):
    print msg

# param msg: message from IB with all the prices for a certain stock
def my_BidAsk(msg):
    if msg.field == 1:
        bidAsk[str([msg.tickerId][0]) + 'b'] =  msg.price
        print contractDict[msg.tickerId][0],"Bid", msg.price
    elif msg.field == 2:
        bidAsk[str([msg.tickerId][0]) + 'a'] =  msg.price
        print contractDict[msg.tickerId][0], "Ask", msg.price

# creates the stock contracts for every entry in the contractDict
# param contractTuple: tuple of the info needed to create one contract
def makeStkContract(contractTuple):
    newContract = Contract()
    newContract.m_symbol = contractTuple[0]
    newContract.m_secType = contractTuple[1]
    newContract.m_exchange = contractTuple[2]
    newContract.m_currency = contractTuple[3]
    return newContract

# makes a dictionary of all the contracts
def makeContractDict():
    i = 1
    with open("symbols.txt") as infile:
        for line in infile:
            contractDict[i] = (line.rstrip('\n'), 'CASH', 'IDEALPRO', 'USD')
            i = i + 1

def writeToFile():
    print "Writing to CSV..."
    writer.writerow(["Symbol,", "Bid,", "Ask,", "Spread"])
     
    for key, value in prettyBidAsk.items():
        writer.writerow([str(key) + "," + str(value[0]) + "," + str(value[1]) + "," + str(value[2])])
    outfile.close()
    print "Done"
    
def prettify():
    for i in range(1, (len(bidAsk)/2) + 1):
        prettyBidAsk[contractDict[i][0]] = (bidAsk[str(i) + 'b'], bidAsk[str(i) + 'a'], (bidAsk[str(i) + 'a']-bidAsk[str(i) + 'b']))
        
if __name__ == '__main__':
    now = datetime.datetime.now()
    con = ibConnection()
    con.registerAll(watcher)
    makeContractDict()
    showBidAskOnly = True  # set False to see the raw messages
    if showBidAskOnly:
        con.unregister(watcher, 'TickSize', 'TickPrice')
        con.register(my_BidAsk, 'TickPrice')
    con.connect()
    
    sleep(1)
    
    print '* * * * REQUESTING MARKET DATA * * * *'
    
    for tickId in range(1,len(contractDict) + 1):
        stkContract = makeStkContract(contractDict[tickId])
        con.reqMktData(tickId, stkContract, '', False)
    
    sleep(1)
    
    print '* * * * CANCELING MARKET DATA * * * *'
    
    for tickId in range(1,len(contractDict) + 1):
        con.cancelMktData(tickId)
    
    sleep(1)
    
    con.disconnect()
    
    sleep(1)
    prettify()
    writeToFile()