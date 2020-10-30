package dermomedic.ai

import kotlinx.coroutines.runBlocking
import dermomedic.ai.service.Database
import dermomedic.ai.service.DermoAnalyser
import java.io.File
import java.io.IOException

object AnalyseAllTest {

    @JvmStatic

    fun main(args: Array<String>) {
        val uploadDirPath: String = Config.dataFolder + "/analyser"
        val uploadDir = File(uploadDirPath)
        if (!uploadDir.mkdirs() && !uploadDir.exists()) {
            throw IOException("Failed to create directory ${uploadDir.absolutePath}")
        }
        val database = Database(uploadDir)

        database.listAll().forEach {analyse ->
            if( analyse.analysed() ) {
                println("analyse $analyse, malingantEvaluation: ${analyse.malingantEvaluation}")
            } else {
                println("before analyse $analyse")
                val job = DermoAnalyser.analyse(database,analyse, uploadDir)
                runBlocking { job.join() }
                println("after analyse malingantEvaluation: ${database.analyseById(analyse.idx)?.malingantEvaluation}")
            }
        }

    }

}