package com.manikbora.multiscreenapp;

import com.arthenica.mobileffmpeg.FFmpeg;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.Toast;
import android.widget.AdapterView;
import android.media.MediaPlayer;
import androidx.appcompat.app.AppCompatActivity;

import android.content.pm.PackageManager;
import android.media.MediaRecorder;
import android.util.Log;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import static android.Manifest.permission.RECORD_AUDIO;
import static android.Manifest.permission.WRITE_EXTERNAL_STORAGE;

import java.io.FileInputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.File;



public class ThirdActivity extends AppCompatActivity {

    static {
        System.loadLibrary("echo");
    }

    public native void tune(int[] array1, int[] array2, int[] array3);

    String[] item = {"Set fire to the rain", "pre-record 2", "Live Record"};

    AutoCompleteTextView autoCompleteTextView;
    ArrayAdapter<String> adapterItems;

    private MediaRecorder mRecorder = null;

    private MediaPlayer mPlayer;

    private static String mFileName = null;
    private static String mFileName_r = null;
    private static String mFileName_m = null;

    private static String mFileName_u = null;

    public static final int REQUEST_AUDIO_PERMISSION_CODE =1;

    boolean is_recording = false;

    boolean is_playing_usr = false;






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

        Button btnvoice = findViewById(R.id.btn_process);
        btnvoice.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {

                File storageDir = getExternalFilesDir(null);
                mFileName_u = new File(storageDir, "Voiceprocessed.mp4").getAbsolutePath();
                mFileName = new File(storageDir,"Usersing.mp4").getAbsolutePath();
                mFileName_m = new File(storageDir,"BGMprocessed.mp4").getAbsolutePath();
                int[] BGM = decodeFileToSamples(mFileName_m);
                int[] input_voiced = decodeFileToSamples(mFileName_u);
                int[] input_user = decodeFileToSamples(mFileName);
                int[] output = BGM.clone();

                tune(input_user,input_voiced,output);


                mFileName_r = new File(storageDir, "Result.mp4").getAbsolutePath();
                encodeSamplesToFile(output,mFileName_r);
            }
        });

        Button btnmusic = findViewById(R.id.btn_music);
        btnmusic.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                musicsound.start();
            }
        });

        Button btnrecord = findViewById(R.id.btn_record);
        btnrecord.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (!is_recording){
                    startRecording();
                    File storageDir = getExternalFilesDir(null);
                    mFileName_m = new File(storageDir, "BGMprocessed.mp4").getAbsolutePath();
                    playAudio(mFileName_m);

                }
                else{
                    pauseRecording();
                    pausePlaying();
                }
                is_recording = !is_recording;
            }
        });

        Button btnplay = findViewById(R.id.btn_play_trg);
        btnplay.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if (!is_playing_usr){
                    //AudioPlayer();
                    File storageDir = getExternalFilesDir(null);
                    mFileName_r = new File(storageDir, "Result.mp4").getAbsolutePath();
                    playAudio(mFileName_r);
                }
                else{
                    pausePlaying();
                }
                is_playing_usr = !is_playing_usr;
            }
        });
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        // this method is called when user will
        // grant the permission for audio recording.
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        switch (requestCode) {
            case REQUEST_AUDIO_PERMISSION_CODE:
                if (grantResults.length > 0) {
                    boolean permissionToRecord = grantResults[0] == PackageManager.PERMISSION_GRANTED;
                    boolean permissionToStore = grantResults[1] == PackageManager.PERMISSION_GRANTED;
                    if (permissionToRecord && permissionToStore) {
                        Toast.makeText(getApplicationContext(), "Permission Granted", Toast.LENGTH_LONG).show();
                    } else {
                        Toast.makeText(getApplicationContext(), "Permission Denied", Toast.LENGTH_LONG).show();
                    }
                }
                break;
        }
    }

    public boolean CheckPermissions() {
        // this method is used to check permission
        int result = ContextCompat.checkSelfPermission(getApplicationContext(), WRITE_EXTERNAL_STORAGE);
        int result1 = ContextCompat.checkSelfPermission(getApplicationContext(), RECORD_AUDIO);
        return result == PackageManager.PERMISSION_GRANTED && result1 == PackageManager.PERMISSION_GRANTED;
    }

    private void RequestPermissions() {
        // this method is used to request the
        // permission for audio recording and storage.
        ActivityCompat.requestPermissions(ThirdActivity.this, new String[]{RECORD_AUDIO, WRITE_EXTERNAL_STORAGE}, REQUEST_AUDIO_PERMISSION_CODE);
    }

    public void startRecording() {
        File storageDir = getExternalFilesDir(null); // Gets app-specific storage directory
        mFileName = new File(storageDir, "Usersing.mp4").getAbsolutePath();


        if (mRecorder != null) {
            mRecorder.release();
        }

        mRecorder = new MediaRecorder();
        mRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        mRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
        mRecorder.setAudioChannels(1);
        mRecorder.setOutputFile(mFileName);

        try {
            mRecorder.prepare();
            mRecorder.start();
        } catch (IOException e) {
            Log.e("TAG", "prepare() failed", e);
        }

    }

    public void pauseRecording() {

        mRecorder.stop();
        mRecorder.release();
        mRecorder = null;

    }

    public void pausePlaying() {
        // this method will release the media player
        // class and pause the playing of our recorded audio.
        mPlayer.release();
        mPlayer = null;
    }


    public void playAudio(String datapath) {
        File file = new File(datapath);
        if (!file.exists()) {
            Log.e("TAG", "File does not exist: " + datapath);
            return;
        }

        mPlayer = new MediaPlayer();
        try {
            mPlayer.setDataSource(datapath); // Setting the data source to our file name
            mPlayer.prepare(); // Preparing the media player
            mPlayer.start(); // Starting the media player
        } catch (IOException e) {
            Log.e("TAG", "prepare() failed", e);
        }
    }


    public static int[] decodeFileToSamples(String inputFilePath) {
        String tempPcmPath = inputFilePath.replace(".mp4", ".pcm");

        // Decode AAC to PCM using FFmpeg
        String command = "-y -i " + inputFilePath + " -f s16le -acodec pcm_s16le " + tempPcmPath;
        int rc = FFmpeg.execute(command);
        if (rc == 0) {
            System.out.println("Successfully decoded the audio to " + tempPcmPath);
        } else {
            System.err.println("FFmpeg decoding failed with exit code " + rc);
            return null;
        }

        // Read PCM data from file and convert to IntArray
        try {
            FileInputStream fis = new FileInputStream(tempPcmPath);
            FileChannel channel = fis.getChannel();
            ByteBuffer buffer = ByteBuffer.allocate((int) channel.size()).order(ByteOrder.LITTLE_ENDIAN);
            channel.read(buffer);
            buffer.flip();

            ArrayList<Integer> samples = new ArrayList<>();
            while (buffer.hasRemaining()) {
                short sample = buffer.getShort();
                samples.add((int) sample);
            }

            // Optionally convert ArrayList to IntArray if needed
            int[] samplesArray = samples.stream().mapToInt(i -> i).toArray();
            return samplesArray;}catch (Exception e) {
            System.err.println("Failed to read PCM data: " + e.getMessage());
        }


        // Clean up the temporary PCM file
        new File(tempPcmPath).delete();
        return null;

    }

    public static void encodeSamplesToFile(int[] samples, String outputFilePath) {
        String tempPcmPath = outputFilePath.replace(".mp4", ".pcm");

        // Write IntArray to PCM file
        try (FileOutputStream fos = new FileOutputStream(tempPcmPath);
             FileChannel channel = fos.getChannel()) {
            ByteBuffer buffer = ByteBuffer.allocate(samples.length * 2).order(ByteOrder.LITTLE_ENDIAN);
            for (int sample : samples) {
                buffer.putShort((short) sample);
            }
            buffer.flip();
            channel.write(buffer);
        } catch (Exception e) {
            Log.e("TAG", "Failed to write PCM data: " + e.getMessage());
            return;
        }

        // Encode PCM to AAC using FFmpeg
        String command = "-y -f s16le -ar 44100 -ac 1 -i " + tempPcmPath + " -c:a aac -b:a 192k " + outputFilePath;
        int rc = FFmpeg.execute(command);
        if (rc == 0) {
            Log.i("TAG", "Successfully encoded the audio to " + outputFilePath);
        } else {
            Log.e("TAG", "FFmpeg encoding failed with exit code " + rc);
        }

        // Clean up the temporary PCM file
        new File(tempPcmPath).delete();
    }

}
