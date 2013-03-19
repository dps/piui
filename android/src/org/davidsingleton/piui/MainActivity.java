package org.davidsingleton.piui;

import java.net.InetAddress;

import android.annotation.SuppressLint;
import android.app.ActionBar;
import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.webkit.WebView;

/**
 * Main Activity for PiUi Android app.
 * 
 * This Activity is a small wrapper around a WebView, which hosts the main PiUi, adding
 *  - a PiPollerTask which periodically tries to connect to a connected RaspberryPi
 *    running PiUi (by looking for a response to http://piui/ping)
 *  - a PiUptimeTask which runs once webView has taken over hosting the PiUi to grab
 *    system uptime and load from the device periodically and show it in the title bar.
 *    
 * @author davidsingleton@gmail.com
 */
public class MainActivity extends Activity implements PiPollerAddressListener {

	private WebView webView;
	private PiPollerTask poller;
	private PiUptimeTask piup;
	private String piUrl;

	@SuppressLint("SetJavaScriptEnabled")
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		webView = (WebView) findViewById(R.id.webView);
		webView.getSettings().setJavaScriptEnabled(true);

		webView.loadUrl("file:///android_asset/loading.html");

		poller = new PiPollerTask(this);
		poller.execute(null, null);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}

	@Override
	public boolean onOptionsItemSelected(MenuItem item) {
		if (item.getItemId() == R.id.menu_refresh) {
			webView.reload();
			return true;
		} else {
			return super.onOptionsItemSelected(item);
		}
	}

	@Override
	public void onPiFoundAtAddress(InetAddress addr) {
		piUrl = "http://" + addr.getHostAddress() + "/";
		webView.loadUrl("file:///android_asset/connected.html");
		piup = new PiUptimeTask(this);
		piup.doInBackground(addr);
	}

	@Override
	public void onStatusUpdate(String status) {
		ActionBar ab = getActionBar();
		status = status.replace("load average", "load");
		status = status.replace("users", "u");
		ab.setTitle(status.substring(status.indexOf("up")));
	}

	@Override
	public void onConnectionLost() {

	}

	@Override
	public void onAppFound() {
		runOnUiThread(new Runnable() {
			@Override
			public void run() {
				webView.loadUrl(piUrl);
			}
		});
	}

	@Override
	protected void onDestroy() {
		super.onDestroy();
		Log.d("PiUi", "onDestroy");
		if (poller != null) {
			poller.stop();
		}
		if (piup != null) {
			piup.stop();
		}
	}

	@Override
	protected void onPause() {
		super.onPause();
		finish();
	}

}
