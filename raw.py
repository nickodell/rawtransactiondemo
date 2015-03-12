from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging
from decimal import Decimal
from binascii import hexlify, unhexlify


# Login information for my node
rpc_user = "bitcoinrpc"
rpc_password = "87Y9A2gs25E9HDPGc9axqSqzxMR2MyTtrMkYc5KiZk2Z"

logging.basicConfig()
logging.getLogger("BitcoinRPC").setLevel(logging.DEBUG)

rpc = AuthServiceProxy("http://%s:%s@127.0.0.1:18332/" % (rpc_user, rpc_password))

first_unspent = rpc.listunspent()[0]
txid = first_unspent['txid']
vout = first_unspent['vout']
input_amount = first_unspent['amount']
SATOSHI = Decimal("0.00000001")
change_amount = input_amount - Decimal("0.005") - SATOSHI
# Marker address we're going to replace
# Produces a pattern that's easy to search for
mainnet = 0
if mainnet:
    dummy_address = "1111111111111111111114oLvT2"
else:
    dummy_address = "mfWxJ45yp2SFn7UciZyNpvDKrzbhyfKrY8"

# My change address
change_address = "mhZuYnuMCZLjZKeDMnY48xsR5qkjq7bAr9"


tx = rpc.createrawtransaction([{"txid": txid, "vout": vout}], \
                              {change_address: change_amount, \
                               dummy_address: SATOSHI})

# Pattern to replace
# Represents length of script, then OP_DUP OP_HASH160,
# then length of hash, then hash, OP_EQUALVERIFY OP_CHECKSIG
oldScriptPubKey = "1976a914000000000000000000000000000000000000000088ac"

# Data to insert
data = "Melons."
if len(data) > 75:
    raise Exception("Can't contain this much data-use OP_PUSHDATA1")

newScriptPubKey = "6a" + hexlify(chr(len(data))) + hexlify(data)

#Append int of length to start
newScriptPubKey = hexlify(chr(len(unhexlify(newScriptPubKey)))) + newScriptPubKey


if oldScriptPubKey not in tx:
    raise Exception("Something broke!")

tx = tx.replace(oldScriptPubKey, newScriptPubKey)
rpc.decoderawtransaction(tx)
tx = rpc.signrawtransaction(tx)['hex']
rpc.sendrawtransaction(tx)
