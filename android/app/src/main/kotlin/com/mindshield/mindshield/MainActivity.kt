package com.mindshield.mindshield

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.ContactsContract
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity : FlutterActivity() {
    private val CHANNEL = "com.mindshield/sms_receiver"
    private val CONTACTS_CHANNEL = "com.mindshield/contacts"
    private val ACTIONS_CHANNEL = "com.mindshield/actions"
    private var methodChannel: MethodChannel? = null
    
    private val smsReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent != null && intent.action == "com.mindshield.SMS_RECEIVED") {
                val data = mapOf(
                    "id" to intent.getStringExtra("id"),
                    "sender" to intent.getStringExtra("sender"),
                    "body" to intent.getStringExtra("body"),
                    "timestamp" to intent.getLongExtra("timestamp", 0L)
                )
                methodChannel?.invokeMethod("onSmsReceived", data)
            }
        }
    }

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        methodChannel = MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CONTACTS_CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "fetchContacts") {
                val contacts = getAllContacts()
                result.success(contacts)
            } else {
                result.notImplemented()
            }
        }

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, ACTIONS_CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "launchSms" -> {
                    val number = call.argument<String>("number")
                    if (number != null) {
                        launchSms(number)
                        result.success(true)
                    } else {
                        result.error("BAD_ARGS", "Phone number is null", null)
                    }
                }
                "launchDialer" -> {
                    val number = call.argument<String>("number")
                    if (number != null) {
                        launchDialer(number)
                        result.success(true)
                    } else {
                        result.error("BAD_ARGS", "Phone number is null", null)
                    }
                }
                "shareText" -> {
                    val text = call.argument<String>("text")
                    if (text != null) {
                        shareText(text)
                        result.success(true)
                    } else {
                        result.error("BAD_ARGS", "Text is null", null)
                    }
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun launchSms(number: String) {
        try {
            val intent = Intent(Intent.ACTION_SENDTO).apply {
                data = Uri.parse("smsto:$number")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(intent)
        } catch (e: Exception) {
            // Safe fallback
        }
    }

    private fun launchDialer(number: String) {
        try {
            val intent = Intent(Intent.ACTION_DIAL).apply {
                data = Uri.parse("tel:$number")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(intent)
        } catch (e: Exception) {
            // Safe fallback
        }
    }

    private fun shareText(text: String) {
        try {
            val intent = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_TEXT, text)
            }
            val chooser = Intent.createChooser(intent, "Share message").apply {
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            startActivity(chooser)
        } catch (e: Exception) {
            // Safe fallback
        }
    }

    private fun getAllContacts(): Map<String, String> {
        val contacts = mutableMapOf<String, String>()
        val uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
        val projection = arrayOf(
            ContactsContract.CommonDataKinds.Phone.NUMBER,
            ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME
        )
        try {
            contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
                val numberIdx = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                val nameIdx = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
                if (numberIdx != -1 && nameIdx != -1) {
                    while (cursor.moveToNext()) {
                        val number = cursor.getString(numberIdx)
                        val name = cursor.getString(nameIdx)
                        if (number != null && name != null) {
                            val normalized = number.replace(Regex("[\\s\\-()]+"), "").lowercase()
                            contacts[normalized] = name
                        }
                    }
                }
            }
        } catch (e: Exception) {
            // Permission denied or query error
        }
        return contacts
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val filter = IntentFilter("com.mindshield.SMS_RECEIVED")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(smsReceiver, filter, Context.RECEIVER_EXPORTED)
        } else {
            registerReceiver(smsReceiver, filter)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            unregisterReceiver(smsReceiver)
        } catch (e: Exception) {
            // Ignore if not registered
        }
    }
}
