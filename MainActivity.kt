package com.example.sleeptracker

import android.app.TimePickerDialog
import android.content.Context
import android.os.Bundle
import android.os.SystemClock
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var chronometer: Chronometer
    private lateinit var sleepStage: TextView
    private lateinit var avgSleep: TextView

    private var startTime: Long = 0
    private var running = false

    private var goalHours = 8

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        chronometer = findViewById(R.id.chronometer)
        sleepStage = findViewById(R.id.sleepStage)
        avgSleep = findViewById(R.id.avgSleep)

        val startBtn = findViewById<Button>(R.id.startBtn)
        val stopBtn = findViewById<Button>(R.id.stopBtn)
        val resetBtn = findViewById<Button>(R.id.resetBtn)
        val settingsBtn = findViewById<Button>(R.id.settingsBtn)

        loadAverage()

        // START BUTTON
        startBtn.setOnClickListener {

            if (!running) {

                startTime = System.currentTimeMillis()

                chronometer.base = SystemClock.elapsedRealtime()
                chronometer.start()

                running = true

                Toast.makeText(this,"Sleep Tracking Started",Toast.LENGTH_SHORT).show()
            }
        }

        // STOP BUTTON
        stopBtn.setOnClickListener {

            if (!running) {
                Toast.makeText(this,"Tracking not started",Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            chronometer.stop()
            running = false

            val duration = System.currentTimeMillis() - startTime
            val hours = duration / (1000 * 60 * 60)

            updateAverage(hours)

            if (hours >= goalHours) {
                Toast.makeText(this,"Goal Achieved!",Toast.LENGTH_LONG).show()
            } else {
                val diff = goalHours - hours
                Toast.makeText(this,"You slept $diff hour less than goal",Toast.LENGTH_LONG).show()
            }
        }

        // RESET BUTTON
        resetBtn.setOnClickListener {

            chronometer.base = SystemClock.elapsedRealtime()
            chronometer.stop()

            sleepStage.text = "Sleep Stage: Awake"

            running = false
        }

        // SETTINGS BUTTON
        settingsBtn.setOnClickListener {

            val picker = TimePickerDialog(this,
                { _, hour, _ ->
                    goalHours = hour
                    Toast.makeText(this,"Goal set to $goalHours hours",Toast.LENGTH_SHORT).show()
                },
                goalHours,
                0,
                true)

            picker.show()
        }

        // SLEEP STAGE DETECTION
        chronometer.setOnChronometerTickListener {

            val elapsed = System.currentTimeMillis() - startTime
            val seconds = elapsed / 1000

            if (seconds >= 5) {
                sleepStage.text = "Sleep Stage: Deep Sleep"
            } else {
                sleepStage.text = "Sleep Stage: Light Sleep"
            }
        }
    }

    // UPDATE AVERAGE SLEEP
    private fun updateAverage(hours: Long) {

        val prefs = getSharedPreferences("sleepData", Context.MODE_PRIVATE)

        var total = prefs.getLong("total",0)
        var days = prefs.getLong("days",0)

        total += hours
        days += 1

        prefs.edit()
            .putLong("total",total)
            .putLong("days",days)
            .apply()

        val avg = total / days

        avgSleep.text = "Avg Sleep: $avg h"
    }

    // LOAD SAVED AVERAGE
    private fun loadAverage(){

        val prefs = getSharedPreferences("sleepData", Context.MODE_PRIVATE)

        val total = prefs.getLong("total",0)
        val days = prefs.getLong("days",0)

        if(days>0){
            val avg = total / days
            avgSleep.text = "Avg Sleep: $avg h"
        }
    }
}