package dermomedic.ai.service.ktor

import java.io.*
import kotlinx.serialization.Serializable

@Serializable
data class Analyse(val idx: Long, val extension: String, val fileName: String) {

    var malingantEvaluation: Float? = null

    fun analysed(): Boolean {
        return malingantEvaluation != null
    }

    fun storedFileName(): String {
        return "$idx.$extension"
    }

}
