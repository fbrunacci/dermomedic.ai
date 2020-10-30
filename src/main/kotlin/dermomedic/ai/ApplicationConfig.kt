package dermomedic.ai

import com.sksamuel.hoplite.ConfigLoader

data class Folder(val data : String, val model: String)
data class Model(val preTrainedModel: String)
data class ApplicationConfig(val work_folder: String, val folder: Folder, val model: Model)

object Config {

    val config = ConfigLoader().loadConfigOrThrow<ApplicationConfig>("/application.yaml")
    var dataFolder = config.folder.data
    var modelFolder = config.folder.model
    var preTrainedModel = config.model.preTrainedModel

    @JvmStatic
    fun main(args: Array<String>) {
        println(config)
    }


}