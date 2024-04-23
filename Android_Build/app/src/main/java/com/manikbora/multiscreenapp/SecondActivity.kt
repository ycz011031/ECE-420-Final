package com.manikbora.multiscreenapp

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.media.MediaPlayer
import android.net.Uri


class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_second)

        val btnFirstActivity = findViewById<Button>(R.id.btnFirstActivity)
        btnFirstActivity.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        var play = findViewById<Button>(R.id.btn_Play)
        var mp=MediaPlayer()

        play.setOnClickListener{
            mp.setDataSource(this,Uri.parse("android.resource://"+this.packageName+"/"+R.raw.output_final_synthesized))
            mp.prepare()
            mp.start()
        }
    }
}