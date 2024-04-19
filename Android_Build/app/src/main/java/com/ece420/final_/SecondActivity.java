package com.ece420.final_;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.support.v4.app.ActivityCompat;
import android.view.WindowManager;
import android.widget.Button;

import com.ece420.final_.MainActivity;
import com.ece420.final_.R;

public class SecondActivity extends Activity
        implements ActivityCompat.OnRequestPermissionsResultCallback {

    // UI Variables
    Button Button1, Button2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        setContentView(R.layout.activity_1);
        super.setRequestedOrientation (ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);

        // Google NDK Stuff
        Button1 = (Button)findViewById((R.id.second_activity_next_button));
        Button2 = (Button)findViewById((R.id.second_activity_previous_button));

    }
}
