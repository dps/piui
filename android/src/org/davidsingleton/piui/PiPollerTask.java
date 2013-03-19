package org.davidsingleton.piui;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.URL;
import java.net.UnknownHostException;

import android.os.AsyncTask;

class PiPollerTask extends AsyncTask<Void, Void, InetAddress> {

	private PiPollerAddressListener listener;
	private boolean stop;
	private static final long POLL_DELAY_MS = 2000;
	private Thread appCheck;

	PiPollerTask(PiPollerAddressListener listener) {
		this.listener = listener;
	}

	@Override
	protected void onPostExecute(final InetAddress result) {
		if (result != null) {
			if (listener != null) {
				listener.onPiFoundAtAddress(result);
			}
			startAppCheckPolling(result);
		}
	}

	private void startAppCheckPolling(final InetAddress result) {
		appCheck = new Thread(new Runnable() {

			@Override
			public void run() {
				boolean appFound = false;
				while (!appFound && !stop) {
					try {
						URL url = new URL("http://" + result.getHostAddress() + "/ping");
						InputStream is = (InputStream) url.getContent();
						String resp = (new BufferedReader(new InputStreamReader(is)))
						    .readLine();
						if (resp.equals("pong")) {
							appFound = true;
							listener.onAppFound();
						}
					} catch (IOException e) {
						// pass
					}
					try {
						Thread.sleep(POLL_DELAY_MS);
					} catch (InterruptedException e) {
					}
				}
			}
		});
		appCheck.start();
	}

	@Override
	protected InetAddress doInBackground(Void... params) {
		InetAddress addr = null;
		while (addr == null && !stop) {
			try {
				addr = InetAddress.getByName("piui");
			} catch (UnknownHostException e) {
				try {
					Thread.sleep(POLL_DELAY_MS);
				} catch (InterruptedException e1) {
					// no matter, continue.
				}
			}
		}
		return addr;
	}

	public void stop() {
		stop = true;
		if (appCheck != null) {
			try {
				appCheck.join();
			} catch (InterruptedException e) {
			}
		}
	}

}