package com.aniteve

import com.facebook.react.ReactActivity
import com.facebook.react.ReactActivityDelegate
import com.facebook.react.defaults.DefaultNewArchitectureEntryPoint.fabricEnabled
import com.facebook.react.defaults.DefaultReactActivityDelegate
import android.os.Bundle
import android.util.Log
import android.view.KeyEvent
import android.widget.Toast
import com.facebook.react.ReactPackage
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.NativeModule
import com.facebook.react.uimanager.ViewManager
import com.facebook.react.bridge.ReactMethod

var promise: Promise? = null
var hasGetUp = true
class TestNativeModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {
  

  init {
    Log.d("TestNativeModule", "TestNativeModule created")
    promise = null
  }

  override fun getName(): String {
    return "TestNativeModule"
  }

  @ReactMethod
  fun resolveTest(newPromise: Promise) {
    promise = newPromise
    Log.d("TestNativeModule", "Promise set")
  }
}

class MyNativeModulePackage : ReactPackage {

  override fun createNativeModules(reactContext: ReactApplicationContext): List<NativeModule> {
    val modules = listOf(TestNativeModule(reactContext))
    return modules
  }

  override fun createViewManagers(reactContext: ReactApplicationContext): List<ViewManager<*, *>> {
    return emptyList()
  }
}

class MainActivity : ReactActivity() {

  /**
   * Returns the name of the main component registered from JavaScript. This is used to schedule
   * rendering of the component.
   */
  override fun getMainComponentName(): String = "Aniteve"

  /**
   * Returns the instance of the [ReactActivityDelegate]. We use [DefaultReactActivityDelegate]
   * which allows you to enable New Architecture with a single boolean flags [fabricEnabled]
   */
  override fun createReactActivityDelegate(): ReactActivityDelegate =
      DefaultReactActivityDelegate(this, mainComponentName, fabricEnabled)

  override fun onKeyDown(keyCode: Int, event: KeyEvent): Boolean {
    if (!hasGetUp)
      return true
    hasGetUp = false
    promise?.resolve("$keyCode")
    Log.d("MainActivity", "Promise : $promise")
    return true
  }

  override fun onKeyUp(keyCode: Int, event: KeyEvent): Boolean {
    hasGetUp = true
    return true
  }
}
