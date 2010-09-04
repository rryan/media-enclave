package menclave.android.aenclave;

import android.app.Activity;
import android.app.ListActivity;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ListAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;


public class SearchActivity extends ListActivity {
  /** Called when the activity is first created. */
  @Override
  public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    setListAdapter(new SongAdapter(this));

    ListView lv = getListView();
    lv.setTextFilterEnabled(true);

    lv.setOnItemClickListener(new OnItemClickListener() {
      public void onItemClick(AdapterView<?> parent, View view, int position,
                              long id) {
        Toast.makeText(getApplicationContext(), SONGS[position].getTitle(),
                       Toast.LENGTH_SHORT).show();
      }
    });
  }

  static final Song[] SONGS = new Song[] {
    new Song("Glorious Dawn",       "", "Carl Sagan"),
    new Song("Semi-Charmed",        "", "Third Eye Blind"),
    new Song("Rainbow Stalin",      "", "The Similou"),
    new Song("Double Rainbow Song", "", "Double Rainbow Guy"),
    new Song("Rapist Song",         "", "Antoine Dodson")
  };

  class SongAdapter extends ArrayAdapter<Song> {
    private Activity context;

    SongAdapter(Activity context) {
      super(context, R.layout.song, R.id.songName, SONGS);
      this.context = context;
    }

    public View getView(int position, View convertView, ViewGroup parent) {
      Song song = SONGS[position];
      View songView = context.getLayoutInflater().inflate(R.layout.song, null);
      TextView songName = (TextView)songView.findViewById(R.id.songName);
      songName.setText(song.getTitle());
      TextView artistName = (TextView)songView.findViewById(R.id.artistName);
      artistName.setText(song.getArtist());
      return songView;
    }
  }
}
