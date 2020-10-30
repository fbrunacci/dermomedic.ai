package dermomedic.ai.service

import dermomedic.ai.Config
import kotlinx.coroutines.*
import dermomedic.ai.service.ktor.Analyse
import org.datavec.image.loader.NativeImageLoader
import org.deeplearning4j.nn.graph.ComputationGraph
import org.deeplearning4j.util.ModelSerializer
import org.nd4j.linalg.api.ndarray.INDArray
import org.nd4j.linalg.dataset.api.preprocessor.VGG16ImagePreProcessor
import java.io.File

object DermoAnalyser {

    val height = 224L
    val width = 224L
    val channels = 3L
    val imageLoader = NativeImageLoader(height, width, channels)
    val modelContext = newSingleThreadContext("ModelContext")
    val preTrainedModel: ComputationGraph

    fun initPreTrainedModel() {
    }

    init {
        preTrainedModel = ModelSerializer.restoreComputationGraph("${Config.preTrainedModel}")
    }

    fun analyse(database: Database, analyse: Analyse, uploadDir: File): Job {
        val file = File(uploadDir, analyse.storedFileName())
        val job = GlobalScope.launch {
            var image = imageLoader.asMatrix(file)
//            println("image:$image")
            VGG16ImagePreProcessor().transform(image)
            withContext(modelContext) {
                val output: Array<INDArray> = preTrainedModel.output(false, image)
                println("output: $output")
                analyse.malingantEvaluation = output[0].getFloat(0)
                // analyse.benignEvaluation = output[0].getFloat(1)
                database.saveAnalyse(analyse)
            }
        }
        return job
    }
}