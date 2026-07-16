package com.mindshield.mindshield

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import android.content.ContentValues
import java.io.File
import java.util.UUID

class SmsReceiver : BroadcastReceiver() {
    companion object {
        private const val TAG = "SmsReceiver"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            if (messages.isNotEmpty()) {
                val sms = messages[0]
                val sender = sms.displayOriginatingAddress ?: ""
                val body = messages.joinToString("") { it.displayMessageBody ?: "" }
                val timestamp = sms.timestampMillis

                Log.d(TAG, "Received SMS from $sender: $body")

                // Insert into SQLite database as "pending"
                val id = insertPendingSms(context, sender, body, timestamp)

                // Send local broadcast to notify MainActivity if it's active
                val localIntent = Intent("com.mindshield.SMS_RECEIVED").apply {
                    putExtra("id", id)
                    putExtra("sender", sender)
                    putExtra("body", body)
                    putExtra("timestamp", timestamp)
                }
                context.sendBroadcast(localIntent)
            }
        }
    }

    private fun insertPendingSms(context: Context, sender: String, body: String, timestamp: Long): String {
        val id = "sms_" + UUID.randomUUID().toString()
        try {
            val dbPath = context.getDatabasePath("mindshield.db")
            // Ensure databases directory exists
            dbPath.parentFile?.mkdirs()

            // Open or create the database
            val db = context.openOrCreateDatabase("mindshield.db", Context.MODE_PRIVATE, null)
            
            // Ensure table is created if it hasn't been initialized by Flutter yet
            db.execSQL("""
                CREATE TABLE IF NOT EXISTS sms_messages (
                    id TEXT PRIMARY KEY,
                    sender TEXT NOT NULL,
                    body TEXT NOT NULL,
                    timestamp INTEGER NOT NULL,
                    ai_status TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    confidence_score REAL,
                    detected_threats TEXT NOT NULL,
                    is_spam INTEGER NOT NULL DEFAULT 0,
                    spam_risk_level TEXT,
                    spam_attack_type TEXT,
                    spam_status TEXT,
                    quarantined_at INTEGER
                )
            """.trimIndent())

            val values = ContentValues().apply {
                put("id", id)
                put("sender", sender)
                put("body", body)
                put("timestamp", timestamp)
                put("ai_status", "pending")
                put("is_read", 0)
                put("detected_threats", "[]")
                put("is_spam", 0)
            }

            db.insert("sms_messages", null, values)
            db.close()
            Log.d(TAG, "Successfully inserted pending SMS $id into SQLite.")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to insert pending SMS into SQLite: ${e.message}", e)
        }
        return id
    }
}
