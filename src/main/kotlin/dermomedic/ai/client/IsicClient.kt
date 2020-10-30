package dermomedic.ai.client

import com.google.gson.GsonBuilder
import com.google.gson.LongSerializationPolicy
import dermomedic.ai.service.ktor.Analyse
import java.io.File
import io.ktor.client.*
import io.ktor.client.request.forms.*
import io.ktor.http.*
import io.ktor.utils.io.streams.*

/**
 * Main entrypoint of the executable that starts a Netty webserver at port 8080
 * and registers the [module].
 *
 * This is a hello-world application, while the important part is that the build.gradle
 * includes all the available artifacts and serves to use as module for a scratch or to autocomplete APIs.
 */
suspend fun main(args: Array<String>) {

    val client = HttpClient()
    val imageName = "ISIC_0015719.jpg"
    val imageDir = File("/run/media/fabien/Data/Datasets/ISIC/Deotte/1024/train/")
    val imageFile = File(imageDir,imageName)

    println(ContentType.Image.JPEG.toString())

    val headersBuilder = HeadersBuilder()
    headersBuilder[HttpHeaders.ContentType] = ContentType.Image.JPEG.toString()
    headersBuilder[HttpHeaders.ContentDisposition] = "filename=$imageName"

    val formData = formData {
        appendInput("image",
                headersBuilder.build()
        ) { imageFile.inputStream().asInput() }
    }

    val json: String = client.submitFormWithBinaryData("http://localhost:8080/upload", formData)
    println(json)

    val gson = GsonBuilder()
            .disableHtmlEscaping()
            .serializeNulls()
            .setLongSerializationPolicy(LongSerializationPolicy.STRING)
            .create()
    val analyse = gson.fromJson(json, Analyse::class.java)
    println(analyse.idx)

}