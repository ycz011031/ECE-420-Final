package com.manikbora.multiscreenapp


import android.content.Intent
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.io.File
import java.io.IOException


class SecondActivity : AppCompatActivity() {

    private var mRecorder: MediaRecorder? = null
    private var mPlayer: MediaPlayer? = null
    private var mFileName: String? = null

    companion object {
        const val REQUEST_AUDIO_PERMISSION_CODE = 1
    }

    private var isRecording = false
    private var isPlayingUser = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second)

        val btnFirstActivity = findViewById<Button>(R.id.btnFirstActivity)
        btnFirstActivity.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }


        findViewById<Button>(R.id.btn_Go).setOnClickListener {

        }

        findViewById<Button>(R.id.btn_record).setOnClickListener {
            if (!isRecording) {
                startRecording()
            } else {
                pauseRecording()
            }
            isRecording = !isRecording
        }

        findViewById<Button>(R.id.btn_voice).setOnClickListener {
            if (!isPlayingUser) {
                playAudio()
            } else {
                pausePlaying()
            }
            isPlayingUser = !isPlayingUser
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_AUDIO_PERMISSION_CODE) {
            if (grantResults.isNotEmpty()) {
                val permissionToRecord = grantResults[0] == PackageManager.PERMISSION_GRANTED
                val permissionToStore = grantResults[1] == PackageManager.PERMISSION_GRANTED
                if (permissionToRecord && permissionToStore) {
                    Toast.makeText(applicationContext, "Permission Granted", Toast.LENGTH_LONG)
                        .show()
                } else {
                    Toast.makeText(applicationContext, "Permission Denied", Toast.LENGTH_LONG)
                        .show()
                }
            }
        }
    }

    private fun checkPermissions(): Boolean {
        val result = ContextCompat.checkSelfPermission(
            applicationContext,
            android.Manifest.permission.WRITE_EXTERNAL_STORAGE
        )
        val result1 = ContextCompat.checkSelfPermission(
            applicationContext,
            android.Manifest.permission.RECORD_AUDIO
        )
        return result == PackageManager.PERMISSION_GRANTED && result1 == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermissions() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(
                android.Manifest.permission.RECORD_AUDIO,
                android.Manifest.permission.WRITE_EXTERNAL_STORAGE
            ),
            REQUEST_AUDIO_PERMISSION_CODE
        )
    }

    private fun startRecording() {
        val storageDir = getExternalFilesDir(null) // Gets app-specific storage directory
        mFileName = File(storageDir, "AudioRecording.3gp").absolutePath

        if (checkPermissions()) {
            mRecorder?.release()
            mRecorder = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
                setAudioEncoder(MediaRecorder.AudioEncoder.AMR_NB)
                setOutputFile(mFileName)
                try {
                    prepare()
                    start()
                } catch (e: IOException) {
                    Log.e("TAG", "prepare() failed")
                }
            }
        } else {
            requestPermissions()
        }
    }

    private fun pauseRecording() {
        mRecorder?.apply {
            stop()
            release()
        }
        mRecorder = null
    }

    private fun pausePlaying() {
        mPlayer?.release()
        mPlayer = null
    }

    fun playAudio() {
        // Using media player class to play our recorded audio
        mPlayer = MediaPlayer().apply {
            try {
                // Setting the data source to our file name
                setDataSource(mFileName)

                // Preparing the media player
                prepare()

                // Starting the media player
                start()
            } catch (e: IOException) {
                Log.e("TAG", "prepare() failed", e)
            }
        }
    }
}