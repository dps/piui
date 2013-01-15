package org.davidsingleton.piui;

import java.net.InetAddress;

interface PiPollerAddressListener {
	void onPiFoundAtAddress(InetAddress addr);
}