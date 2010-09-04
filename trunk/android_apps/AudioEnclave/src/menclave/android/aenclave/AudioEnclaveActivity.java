package menclave.android.aenclave;

import android.app.Activity;
import android.app.TabActivity;
import android.content.Intent;
import android.content.res.Resources;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.TabHost;
import android.widget.TextView;
import android.widget.Toast;


public class AudioEnclaveActivity extends TabActivity
{
  /** Called when the activity is first created. */
  @Override
  public void onCreate(Bundle savedInstanceState)
  {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.main);

    Resources res = getResources();
    TabHost tabHost = getTabHost();
    TabHost.TabSpec spec;
    Intent intent;

    // Register search intent.
    intent = new Intent().setClass(this, SearchActivity.class);
    spec = tabHost.newTabSpec("search");
    spec.setIndicator("Search", res.getDrawable(R.drawable.ic_tab_search));
    spec.setContent(intent);
    tabHost.addTab(spec);

    // Register roulette intent.
    intent = new Intent().setClass(this, RouletteActivity.class);
    spec = tabHost.newTabSpec("roulette");
    spec.setIndicator("Roulette", res.getDrawable(R.drawable.ic_tab_search));
    spec.setContent(intent);
    tabHost.addTab(spec);
  }
}
