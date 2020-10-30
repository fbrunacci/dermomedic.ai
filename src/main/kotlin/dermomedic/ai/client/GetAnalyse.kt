package dermomedic.ai.client

import com.google.gson.GsonBuilder
import com.google.gson.LongSerializationPolicy
import dermomedic.ai.service.ktor.Analyse
import io.ktor.client.HttpClient
import io.ktor.client.features.json.JsonFeature
import io.ktor.client.features.json.serializer.KotlinxSerializer
import io.ktor.client.request.HttpRequestBuilder
import io.ktor.client.request.get
import io.ktor.http.takeFrom
import kotlinx.serialization.json.Json
import java.io.File

suspend fun main(args: Array<String>) {

    val client = HttpClient()

    val gson = GsonBuilder()
            .disableHtmlEscaping()
            .serializeNulls()
            .setLongSerializationPolicy(LongSerializationPolicy.STRING)
            .create()


    val json: String = client.get("http://localhost:8080/analyse/json/1")
    val analyse = gson.fromJson(json, Analyse::class.java)
    println(analyse.malingantEvaluation)
}