package dermomedic.ai.service.ktor

import io.ktor.application.*
import io.ktor.features.*
import io.ktor.http.*
import io.ktor.http.content.*
import io.ktor.locations.*
import io.ktor.request.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.sessions.*
import kotlinx.html.*
import dermomedic.ai.service.DermoAnalyser
import dermomedic.ai.service.Database
import java.io.*

/**
 * Register analyse-related routes: [Index] (/), [AnalysePage] (/analyse/page/{id}) and [ImageStream] (/analyse/{id})
 */
fun Route.analyses(database: Database, uploadDir: File) {
    /**
     * The index route that doesn't have any parameters, returns a HTML with a list of analyses linking to their pages
     * and displayed unlinked author names.
     */
    get<Index> {
        val session = call.sessions.get<AnalyseSession>()
        val topAnalyses = database.top()
        val etag = topAnalyses.joinToString { "${it.idx},${it.analysed()}" }.hashCode().toString() + "-" + session?.userId?.hashCode()
        val visibility = if (session == null) CacheControl.Visibility.Public else CacheControl.Visibility.Private

        call.respondDefaultHtml(listOf(EntityTagVersion(etag)), visibility) {
            div("posts") {
                when {
                    topAnalyses.isEmpty() -> {
                        h1("content-subhead") { +"No analyses" }
                        div {
                            +"You need to upload some analyses to watch them"
                        }
                    }
                    topAnalyses.size < 11 -> {
                        h1("content-subhead") { +"analyses" }
                    }
                    else -> {
                        h1("content-subhead") { +"Top 10 analyses" }
                    }
                }
                topAnalyses.forEach {
                    section("post") {
                        header("post-header") {
                            h3("post-title") {
                                a(href = locations.href(AnalysePage(it.idx))) { + "${it.idx}: ${it.fileName}" }
                            }
                        }
                    }
                }
            }
        }
    }

    /**
     * The [analysePage] returns an HTML with the information about a specified analyse by [analysePage.id]
     * including the analyse itself, being streamed by the [ImageStream] route.
     * If the analyse doens't exists, responds with a 404 [HttpStatusCode.NotFound].
     */
    get<AnalysePage> {
        val analyse = database.analyseById(it.id)

        if (analyse == null) {
            call.respond(HttpStatusCode.NotFound.description("analyse ${it.id} doesn't exist"))
        } else {
            call.respondDefaultHtml(listOf(EntityTagVersion(analyse.hashCode().toString())), CacheControl.Visibility.Public) {

                section("post") {
                    header("post-header") {
                        h3("post-title") {
                            a(href = locations.href(AnalysePage(it.id))) { +analyse.fileName }
                        }
                    }
                }
                p { +"malingantEvaluation: ${analyse.malingantEvaluation}" }
                img(classes = "dermo-img", src = call.url(ImageStream(it.id)))
            }
        }
    }

    get<AnalyseJson> {
        val analyse = database.analyseById(it.id)
        analyse?.let { call.respond(it) } ?: run {
            call.respond(HttpStatusCode.InternalServerError)
        }
    }

    /**
     * Returns the bits of the analyse specified by [ImageStream.id] or [HttpStatusCode.NotFound] if the analyse is not found.
     * It returns a [LocalFileContent] that works along the installed [PartialContent] feature to support getting chunks
     * of the content, and allowing the navigator to seek the analyse even if the analyse content is big.
     */
    get<ImageStream> {
        val analyse = database.analyseById(it.id)

        if (analyse == null) {
            call.respond(HttpStatusCode.NotFound)
        } else {
            val imgFile = File(uploadDir,"${analyse.idx}.${analyse.extension}")
            val ct = ContentType.fromFilePath(imgFile.path)
            val type = ct.first { it.contentType == "image" }
            println("analyse.fileName: ${analyse.fileName} contentType = $type")
            call.respond(LocalFileContent(imgFile, contentType = type))
        }
    }
}

fun Route.upload(database: Database, uploadDir: File) {
    post<Upload> {
        // retrieve all multipart data (suspending)
        val multipart = call.receiveMultipart()
        val imageDir = uploadDir
        var analyse: Analyse? = null
        multipart.forEachPart { part ->
            // if part is a file (could be form item)
            if (part is PartData.FileItem) {
                // retrieve file name of upload
                val imageName = part.originalFileName!!
                val extension = imageName.substringAfterLast('.', "")
                println("/upload: $imageName")
                val toAnalyse = database.addAnalyse(extension, imageName)
                val imageFile = File(imageDir, "${toAnalyse.idx}.${extension}")
                // use InputStream from part to save file
                part.streamProvider().use { its ->
                    // copy the stream to the file with buffering
                    imageFile.outputStream().buffered().use {
                        // note that this is blocking
                        its.copyTo(it)
                    }
                }
                DermoAnalyser.analyse(database,toAnalyse, uploadDir)
                analyse = toAnalyse
            }
            // make sure to dispose of the part after use to prevent leaks
            part.dispose()
        }

        analyse?.let { call.respond(it) } ?: run {
            call.respond(HttpStatusCode.InternalServerError)
        }
    }
}
