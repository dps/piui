package org.davidsingleton.piui;



import java.net.InetAddress;

import android.app.Activity;
import android.os.Bundle;
import android.view.Menu;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity implements PiPollerAddressListener {

	private WebView webView;
	private String WAITING_HTML = "<h2>Waiting for Raspberry Pi...</h2>";


	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		
		webView = (WebView)findViewById(R.id.webView);
		webView.getSettings().setJavaScriptEnabled(true);
		webView.setWebViewClient(new WebViewClient());
		
		webView.loadData(WAITING_HTML, "text/html", "utf-8");

		PiPollerTask poller = new PiPollerTask(this, this);
		poller.execute(null, null);
	}

	
	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.activity_main, menu);
		return true;
	}


	@Override
  public void onPiFoundAtAddress(InetAddress addr) {
		webView.loadUrl("http://" + addr.toString() + ":9999/");
  }

}
