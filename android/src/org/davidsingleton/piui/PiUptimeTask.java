package org.davidsingleton.piui;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.UnknownHostException;

import android.os.AsyncTask;

class PiUptimeTask extends AsyncTask<InetAddress, String, Boolean> {

	private PiPollerAddressListener listener;
	private boolean stop;

	PiUptimeTask(PiPollerAddressListener listener) {
		this.listener = listener;
	}
	
	@Override
  protected void onPostExecute(Boolean result) {
		listener.onConnectionLost();
  }
	
	@Override
  protected void onProgressUpdate(String... values) {
		listener.onStatusUpdate(values[0]);
  }
	
	private static final long POLL_DELAY_MS = 30000;
	private Thread bg;
	
	@Override
	protected Boolean doInBackground(InetAddress... addresses) {
		final InetAddress addr = addresses[0];
		bg = new Thread(new Runnable() {
			@Override
      public void run() {
				while (!stop) {
					try {
						URL url = new URL("http://" + addr.getHostAddress() + "/sup/uptime");
						InputStream is = (InputStream) url.getContent();
						String uptime = (new BufferedReader(new InputStreamReader(is))).readLine();
						publishProgress(uptime);
						try {
		          Thread.sleep(POLL_DELAY_MS);
		        } catch (InterruptedException e1) {
		        	// no matter, continue.
		        }
					} catch (UnknownHostException e) {
		        break;				
					} catch (MalformedURLException e) {
			      break;
		      } catch (IOException e) {
			      break;
		      }
				}
      }});

		bg.start();
		return false;
	}

	public void stop() {
		if (bg != null) {
			stop = true;
			try {
	      bg.join();
      } catch (InterruptedException e) {
      }
		}
  }

}