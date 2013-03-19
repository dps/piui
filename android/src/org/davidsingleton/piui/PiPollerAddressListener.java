package org.davidsingleton.piui;

import java.net.InetAddress;

interface PiPollerAddressListener {
	void onPiFoundAtAddress(InetAddress addr);
	void onStatusUpdate(String status);
	void onConnectionLost();
	void onAppFound();
}