package com.manikbora.multiscreenapp;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.Toast;
import android.widget.AdapterView;
import android.media.MediaPlayer;
import android.net.Uri;
import androidx.appcompat.app.AppCompatActivity;

public class ThirdActivity extends AppCompatActivity {

    String[] item = {"Set fire to the rain", "pre-record 2", "Live Record"};

    AutoCompleteTextView autoCompleteTextView;
    ArrayAdapter<String> adapterItems;




    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_third);

        final MediaPlayer voicesound = MediaPlayer.create(this, R.raw.output_stage1_voice);
        final MediaPlayer musicsound = MediaPlayer.create(this, R.raw.output_stage1_music);

        autoCompleteTextView = findViewById((R.id.auto_complete_txt));
        adapterItems = new ArrayAdapter<String>(this,R.layout.list_item,item);

        autoCompleteTextView.setAdapter(adapterItems);
        autoCompleteTextView.setOnItemClickListener(new AdapterView.OnItemClickListener(){


            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                String item = adapterView.getItemAtPosition(i).toString();
                Toast.makeText(ThirdActivity.this, "item" + item, Toast.LENGTH_SHORT).show();
            }
        });

        Button btnFirstActivity = findViewById(R.id.btnFirstActivity);
        btnFirstActivity.setOnClickListener(view -> {
            Intent intent = new Intent(ThirdActivity.this, MainActivity.class);
            startActivity(intent);
        });

        Button btnvoice = findViewById(R.id.btn_voice);
        btnvoice.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                voicesound.start();
            }
        });

        Button btnmusic = findViewById(R.id.btn_music);
        btnmusic.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                musicsound.start();
            }
        });




    }
}