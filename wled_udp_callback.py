# me - this DAT
#
# dat - the DAT that received the data
# rowIndex - is the row number the data was placed into
# message - an ascii representation of the data
#           Unprintable characters and unicode characters will
#           not be preserved. Use the 'bytes' parameter to get
#           the raw bytes that were sent.
# bytes - a byte array of the data received
# peer - a Peer object describing the originating message
#   peer.close()    #close the connection
#   peer.owner  #the operator to whom the peer belongs
#   peer.address    #network address associated with the peer
#   peer.port       #network port associated with the peer
#

# wled_nodes = {}

# see void sendSysInfoUDP() in C:\Users\dmitrym\YandexDisk\coding_leisure\Arduino\WLED\wled00\udp.cpp
def parse_bts(bts):
	d = dict()
	return 

def insert_or_update(box, index, row, sort=None):
	if box.row(index):
		box.replaceRow(index, row)
	else:
		box.insertRow(row, 0, sort=sort)

def delete_empty_rows(box):
	try:
		first_empty = op("wled_nodes_table").col(0).index("")
		num_rows = op("wled_nodes_table").numRows
		op("wled_nodes_table").deleteRows(list(range(first_empty, num_rows)))
	except ValueError:
		pass


def onReceive(dat, rowIndex, message, bts, peer):
	name = bts[6:6+32].decode("utf-8").rstrip('\x00')
	delete_empty_rows(op("wled_nodes_table"))
	new_row = [peer.address, peer.port, name]
	new_row += [f"http://{peer.address}"]
	insert_or_update(op("wled_nodes_table"), peer.address, new_row, 0)
	return peer.address

	