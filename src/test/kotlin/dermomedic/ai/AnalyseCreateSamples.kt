package dermomedic.ai

import dermomedic.ai.service.Database
import dermomedic.ai.service.DermoAnalyser
import kotlinx.coroutines.runBlocking
import java.io.File
import java.io.IOException

object AnalyseCreateSamples {

    @JvmStatic
    fun main(args: Array<String>) {
        val uploadDirPath: String = Config.dataFolder + "/analyser"
        val uploadDir = File(uploadDirPath)
        if (!uploadDir.mkdirs() && !uploadDir.exists()) {
            throw IOException("Failed to create directory ${uploadDir.absolutePath}")
        }
        val database = Database(uploadDir)

        val imageDir = File("/run/media/fabien/Data/Datasets/ISIC/Deotte/1024/train/")

        for( i in 1..1) {
            val imageName = imageDir.list().toList().shuffled()[0]
            val imageFile = File(imageDir,imageName)
            val toAnalyse = database.addAnalyse(imageFile.extension, imageName)
            imageFile.copyTo(File(uploadDir, toAnalyse.storedFileName()))
//            val job = DermoAnalyser.analyse(database, toAnalyse, uploadDir)
//            runBlocking { job.join() }
//            println("after analyse malingantEvaluation: ${database.analyseById(toAnalyse.id)?.malingantEvaluation}")
        }

    }

}