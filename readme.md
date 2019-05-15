![LBTC explorer](https://lbtc.io/img/logo-w-t-light.png "LBTC explorer")

[Lightning Bitcoin (LBTC)](https://lbtc.io) is a fully decentralized Internet-of-value protocol for global payments. Lightning Bitcoin is forked from [Bitcoin Core](https://bitcoin.org/). Lightning Bitcoin full node replaces PoW consensus of Bitcoin with DPoS, it means LBTC fully meets bitcoin standard expect consensus algorithm.

lbtc-explorer is a [LBTC blockchain explorer](https://lbtc.me) and a web based interface to the [LBTC API JSON-RPC](https://lbtc.me/lbtc/rpc). 

lbtc-explorer is currently being developed to  estimate the size of the LBTC network by finding all the reachable nodes in the network. The current methodology involves sending [getaddr](https://en.bitcoin.it/wiki/Protocol_specification#getaddr) messages recursively to find all the reachable nodes in the network, starting from a set of seed nodes.


