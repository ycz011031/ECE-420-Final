package com.manikbora.multiscreenapp

import com.arthenica.mobileffmpeg.FFmpeg

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.io.File
import java.io.IOException

import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.io.FileInputStream
import java.io.FileOutputStream




class SecondActivity : AppCompatActivity() {

    private var mRecorder: MediaRecorder? = null
    private var mPlayer: MediaPlayer? = null
    private var mFileName: String? = null

    external fun repet(inputArray: IntArray, outputArray1: IntArray, outputArray2: IntArray)


    companion object {
        const val REQUEST_AUDIO_PERMISSION_CODE = 1
        init{
            System.loadLibrary("echo")
        }
    }

    private var isRecording = false
    private var isPlayingUser = false


    // Gets app-specific storage directory
    private var mFileName_m : File? = null
    private var mFileName_v : File? = null

    override fun onCreate(savedInstanceState: Bundle?) {


        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second)


        val btnFirstActivity = findViewById<Button>(R.id.btnFirstActivity)
        btnFirstActivity.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }



        findViewById<Button>(R.id.btn_Go).setOnClickListener {

            val storageDir = getExternalFilesDir(null) // Gets app-specific storage directory
            val Filewav = File(storageDir, "Targetrecording.wav")

            var wavBytes = decodeAudioToSamples(Filewav.absolutePath)

            if (wavBytes != null) {
                //var input_c = convertShortArrayToIntArray(wavBytes)
                var output_v_c = IntArray(wavBytes.size)
                var output_m_c = IntArray(wavBytes.size)




                repet(wavBytes, output_v_c, output_m_c)
                val storageDir = getExternalFilesDir(null)

                if (output_m_c == null){
                    Log.e("TAG","Error, empty output from c")
                }

                mFileName_m = File(storageDir, "BGMprocessed.wav")
                mFileName_v = File(storageDir,"Voiceprocessed.wav")



                encodeSamplesToFile(output_m_c, mFileName_m!!.absolutePath)
                encodeSamplesToFile(output_v_c, mFileName_v!!.absolutePath)
            }


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
                playAudio(mFileName_m!!.absolutePath)
            } else {
                pausePlaying()
            }
            isPlayingUser = !isPlayingUser
        }

        findViewById<Button>(R.id.btn_BGM).setOnClickListener {
            if (!isPlayingUser) {
                playAudio(mFileName_v!!.absolutePath)
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
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        )
        val result1 = ContextCompat.checkSelfPermission(
            applicationContext,
            Manifest.permission.RECORD_AUDIO
        )
        return result == PackageManager.PERMISSION_GRANTED && result1 == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermissions() {
        ActivityCompat.requestPermissions(
            this,
            arrayOf(
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            ),
            REQUEST_AUDIO_PERMISSION_CODE
        )
    }

    private fun startRecording() {

        val storageDir = getExternalFilesDir(null) // Gets app-specific storage directory
        mFileName = File(storageDir, "Targetrecording.wav").absolutePath

        if (checkPermissions()) {
            mRecorder?.release()
            mRecorder = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setAudioChannels(1)
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

    fun playAudio(datapath : String) {
        // Using media player class to play our recorded audio
        mPlayer = MediaPlayer().apply {
            try {
                // Setting the data source to our file name
                setDataSource(datapath)

                // Preparing the media player
                prepare()

                // Starting the media player
                start()
            } catch (e: IOException) {
                Log.e("TAG", "prepare() failed", e)
            }
        }
    }


    fun decodeAudioToSamples(inputFilePath: String): IntArray? {
        val outputFilePath = inputFilePath.replace(".wav", "_temp.pcm")

        // Decode AAC to PCM
        val command = "-y -i $inputFilePath -f s16le -acodec pcm_s16le $outputFilePath"
        val rc = FFmpeg.execute(command)
        if (rc != 0) {
            Log.e("TAG", "FFmpeg failed with exit code $rc")
            return null
        }

        // Read PCM data from file
        try {
            FileInputStream(outputFilePath).use { fis ->
                val byteBuffer = ByteBuffer.allocateDirect(fis.available()).order(ByteOrder.LITTLE_ENDIAN)
                fis.channel.read(byteBuffer)
                byteBuffer.flip()

                // Assuming 16-bit samples, convert byte data to IntArray
                val intArray = IntArray(byteBuffer.remaining() / 2)
                for (i in intArray.indices) {
                    intArray[i] = byteBuffer.short.toInt()
                }
                return intArray
            }
        } catch (e: IOException) {
            Log.e("TAG", "Error reading PCM file: ${e.message}")
            return null
        } finally {
            File(outputFilePath).delete() // Clean up the temporary file
        }
    }

    fun encodeSamplesToFile(samples: IntArray, outputFilePath: String) {
        val tempPcmPath = outputFilePath.replace(".wav", ".pmc")

        // Write IntArray to PCM file
        try {
            FileOutputStream(tempPcmPath).use { fos ->
                val buffer = ByteBuffer.allocate(samples.size * 2).order(ByteOrder.LITTLE_ENDIAN)
                for (sample in samples) {
                    buffer.putShort(sample.toShort())
                }
                buffer.flip()
                fos.channel.write(buffer)
            }
        } catch (e: Exception) {
            Log.e("TAG", "Failed to write PCM data: ${e.message}")
            return
        }

        // Encode PCM to AAC using FFmpeg
        val command = "-y -f s16le -ar 44100 -ac 2 -i $tempPcmPath -c:a aac -b:a 192k $outputFilePath"
        val rc = FFmpeg.execute(command)
        if (rc == 0) {
            Log.i("TAG", "Successfully encoded the audio to $outputFilePath")
        } else {
            Log.e("TAG", "FFmpeg encoding failed with exit code $rc")
        }

        // Clean up the temporary PCM file
        File(tempPcmPath).delete()
    }




}