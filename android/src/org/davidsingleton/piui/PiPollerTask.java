package org.davidsingleton.piui;

import java.io.IOException;
import java.net.InetAddress;
import java.net.UnknownHostException;

import javax.jmdns.JmDNS;
import javax.jmdns.ServiceEvent;
import javax.jmdns.ServiceInfo;
import javax.jmdns.ServiceListener;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;

class PiPollerTask extends AsyncTask<Void, Void, InetAddress> {

	private PiPollerAddressListener taskListener;
	private String TAG = "PiUi";
	private Context context;

	PiPollerTask(PiPollerAddressListener taskListener, Context ctx) {
		this.taskListener = taskListener;
		this.context = ctx;
	}

	@Override
	protected void onPostExecute(InetAddress result) {
		Log.d(TAG, "Found Pi at " + result.toString());

		if (taskListener != null) {
			taskListener.onPiFoundAtAddress(result);
		}
	}

	private static final long POLL_DELAY_MS = 2000;

	@Override
	protected InetAddress doInBackground(Void... params) {
		InetAddress addr = resolve(this.context);
		return addr;

	}

	private String type = "_workstation._tcp.local.";
	private JmDNS jmdns = null;

	android.net.wifi.WifiManager.MulticastLock lock;
	android.os.Handler handler = new android.os.Handler();

	private InetAddress resolve(Context ctx) {
		android.net.wifi.WifiManager wifi = (android.net.wifi.WifiManager) ctx
		    .getSystemService(android.content.Context.WIFI_SERVICE);
		lock = wifi.createMulticastLock("mylockthereturn");
		lock.setReferenceCounted(true);
		lock.acquire();
		try {
			jmdns = JmDNS.create();

			while (true) {
				Log.d("PiUi", "listing...");
				for (ServiceInfo info : jmdns.list(type)) {
					Log.d("PiUi", info.getName() + " " + info.getHostAddress());
					if (info.getName().startsWith("raspberrypi")) {
						return info.getInetAddress();
					}
				}
			}
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
	}

}