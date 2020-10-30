package dermomedic.ai.service

import com.google.gson.*
import dermomedic.ai.service.ktor.Analyse
import org.ehcache.config.builders.CacheConfigurationBuilder
import org.ehcache.config.builders.CacheManagerBuilder
import org.ehcache.config.builders.ResourcePoolsBuilder
import java.io.*
import java.util.*
import java.util.concurrent.atomic.*

/**
 * Class that represents [Database] of the application.
 * It uses a folder instead of a real database to store videos an indexes,
 */
class Database(val uploadDir: File) {
    /**
     * A [GsonBuilder] used for storing the video information in a `.idx` file.
     */
    val gson = GsonBuilder()
        .disableHtmlEscaping()
        .serializeNulls()
        .setLongSerializationPolicy(LongSerializationPolicy.STRING)
        .create()

    /**
     * Creates a ehcache used for caching.
     */
    val cacheManager = CacheManagerBuilder.newCacheManagerBuilder().build(true)

    /**
     * Ehcache used for caching the metadata of the videos.
     */
    @Suppress("UNCHECKED_CAST")
    val analysesCache = cacheManager.createCache<Long, Analyse>("analyses",
            CacheConfigurationBuilder.newCacheConfigurationBuilder(Class.forName("java.lang.Long") as Class<Long>, Analyse::class.java, ResourcePoolsBuilder.heap(10)))

    private val digitsOnlyRegex = "\\d+".toRegex()
    private val allIds by lazy {
        uploadDir.listFiles { f -> f.extension == "idx" && f.nameWithoutExtension.matches(digitsOnlyRegex) }.mapTo(ArrayList()) { it.nameWithoutExtension.toLong() }
    }

    val biggestId by lazy { AtomicLong(allIds.max() ?: 0) }

    fun listAll(): Sequence<Analyse> = allIds.asSequence().mapNotNull { analyseById(it) }

    fun top() = listAll().sortedBy { -1*it.idx }.take(10).toList()

    fun analyseById(id: Long): Analyse? {
        val video = analysesCache.get(id)
        if (video != null) {
            return video
        }

        try {
            val json = gson.fromJson(File(uploadDir, "$id.idx").readText(), Analyse::class.java)
            analysesCache.put(id, json)

            return json
        } catch (e: Throwable) {
            return null
        }
    }

    /**
     * Computes a unique incremental numeric ID for representing a new video.
     */
    fun nextId() = biggestId.incrementAndGet()

    /**
     * Creates a [Video] metadata information with a new unique id, and stores it in disk and the cache.
     */
    fun addAnalyse(extension: String, fileName: String): Analyse {
        val id = nextId()
        val analyse = Analyse(id, extension, fileName)
        File(uploadDir, "$id.idx").writeText(gson.toJson(analyse))
        allIds.add(id)
        analysesCache.put(id, analyse)
        return analyse
    }

    fun saveAnalyse(analyse: Analyse) {
        analysesCache.put(analyse.idx, analyse)
        File(uploadDir, "${analyse.idx}.idx").writeText(gson.toJson(analyse))
    }

}