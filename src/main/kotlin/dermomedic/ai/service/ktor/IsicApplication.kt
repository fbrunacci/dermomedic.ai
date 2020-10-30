@file:UseExperimental(KtorExperimentalLocationsAPI::class)

package dermomedic.ai.service.ktor

import io.ktor.application.*
import io.ktor.auth.*
import io.ktor.features.*
import io.ktor.gson.*
import io.ktor.http.*
import io.ktor.locations.*
import io.ktor.response.*
import io.ktor.routing.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.sessions.*
import io.ktor.util.*
import dermomedic.ai.Config
import dermomedic.ai.service.Database
import dermomedic.ai.service.DermoAnalyser
import java.io.*
import java.util.*

/*
 * Typed routes using the [Locations] feature.
 */

/**
 * Location for a specific video stream by [id].
 */
@Location("/analyse/{id}")
data class ImageStream(val id: Long)

/**
 * Location for a specific video page by [id].
 */
@Location("/analyse/page/{id}")
data class AnalysePage(val id: Long)

@Location("/analyse/json/{id}")
data class AnalyseJson(val id: Long)

/**
 * Location for uploading videos.
 */
@Location("/upload")
class Upload()

/**
 * The index root page with a summary of the site.
 */
@Location("/")
class Index()

/**
 * Session of this site, that just contains the [userId].
 */
data class AnalyseSession(val userId: String)

fun main(args: Array<String>) {
    embeddedServer(Netty, port = 8080) { main()}.start(wait = true)
}

fun Application.main() {
    DermoAnalyser.initPreTrainedModel() // preload preTrainedModel

    // This adds automatically Date and Server headers to each response, and would allow you to configure
    // additional headers served to each response.
    install(DefaultHeaders)
    // This uses use the logger to log every call (request/response)
    install(CallLogging)
    // Allows to use classes annotated with @Location to represent URLs.
    // They are typed, can be constructed to generate URLs, and can be used to register routes.
    install(Locations)
//    // Automatic '304 Not Modified' Responses
//    install(ConditionalHeaders)
    // Supports for Range, Accept-Range and Content-Range headers
    install(PartialContent)
    // This feature enables compression automatically when accepted by the client.
    install(Compression) {
        default()
        excludeContentType(ContentType.Video.Any)
    }

    val sessionkey = hex("03e156f6058a13813816065")

    // We create the folder and a [Database] in that folder for the configuration [upload.dir].
    val uploadDirPath: String = Config.dataFolder + "/analyser"
    val uploadDir = File(uploadDirPath)
    if (!uploadDir.mkdirs() && !uploadDir.exists()) {
        throw IOException("Failed to create directory ${uploadDir.absolutePath}")
    }
    val database = Database(uploadDir)

    install(Sessions) {
        cookie<AnalyseSession>("SESSION") {
            transform(SessionTransportTransformerMessageAuthentication(sessionkey))
        }
    }
    install(ContentNegotiation) {
        gson {
            setPrettyPrinting()
        }
    }

    // Register all the routes available to this application.
    // To allow better scaling for large applications,
    // we have moved those route registrations into several extension methods and files.
    routing {
//        login(users)
        upload(database, uploadDir)
        analyses(database, uploadDir)
        styles()
    }
}

/**
 * Utility for performing non-permanent redirections using a typed [location] whose class is annotated with [Location].
 */
suspend fun ApplicationCall.respondRedirect(location: Any) = respondRedirect(url(location), permanent = false)
