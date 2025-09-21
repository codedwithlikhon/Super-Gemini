package com.supergemini

import android.app.Application
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            SuperGeminiTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainScreen()
                }
            }
        }
    }
}

@Composable
fun MainScreen() {
    var input by remember { mutableStateOf("") }
    var output by remember { mutableStateOf("") }
    val scope = rememberCoroutineScope()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Input field
        OutlinedTextField(
            value = input,
            onValueChange = { input = it },
            label = { Text("Enter command") },
            modifier = Modifier.fillMaxWidth()
        )
        
        // Execute button
        Button(
            onClick = {
                scope.launch {
                    output = executeInTermux(input)
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Execute")
        }
        
        // Output display
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f),
            color = MaterialTheme.colorScheme.surfaceVariant
        ) {
            Text(
                text = output,
                modifier = Modifier.padding(8.dp)
            )
        }
    }
}

suspend fun executeInTermux(command: String): String {
    // This would interact with Termux through its API
    return try {
        // Launch Termux with the command
        val intent = Intent("com.termux.RUN_COMMAND")
            .putExtra("command", command)
        // Handle response through a callback
        "Command executed in Termux"
    } catch (e: Exception) {
        "Error: ${e.message}"
    }
}

class SuperGeminiApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // Initialize Termux integration
        checkTermuxInstallation()
    }
    
    private fun checkTermuxInstallation() {
        val termuxPackage = "com.termux"
        try {
            packageManager.getPackageInfo(termuxPackage, 0)
        } catch (e: Exception) {
            // Prompt to install Termux
            val intent = Intent(Intent.ACTION_VIEW).apply {
                data = Uri.parse("https://f-droid.org/packages/com.termux/")
            }
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            startActivity(intent)
        }
    }
}