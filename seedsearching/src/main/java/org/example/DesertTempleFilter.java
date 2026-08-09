package org.example;

import com.seedfinding.mcbiome.source.BiomeSource;
import com.seedfinding.mcbiome.source.OverworldBiomeSource;
import com.seedfinding.mccore.rand.ChunkRand;
import com.seedfinding.mccore.rand.seed.WorldSeed;
import com.seedfinding.mccore.state.Dimension;
import com.seedfinding.mccore.util.math.DistanceMetric;
import com.seedfinding.mccore.util.pos.CPos;
import com.seedfinding.mccore.version.MCVersion;
import com.seedfinding.mcfeature.loot.item.Item;
import com.seedfinding.mcfeature.loot.item.Items;
import com.seedfinding.mcfeature.misc.SpawnPoint;
import com.seedfinding.mcfeature.structure.DesertPyramid;
import com.seedfinding.mcfeature.structure.generator.structure.DesertPyramidGenerator;
import com.seedfinding.mcterrain.TerrainGenerator;

import java.util.LinkedList;

public class DesertTempleFilter {
    private LinkedList<Long> seeds = new LinkedList<Long>();

    private final int CHUNK_DIST = 5;
    private final MCVersion version = MCVersion.v1_16_1;
    private final ChunkRand rand = new ChunkRand();
    private final DesertPyramid dt = new DesertPyramid(version);
    private final DesertPyramidGenerator dtg = new DesertPyramidGenerator(version);

    public DesertTempleFilter() {}

    public LinkedList<Long> checkSeed(long structureSeed) {
        CPos dtPos = dt.getInRegion(structureSeed, 0, 0, rand);
        BiomeSource obs = BiomeSource.of(Dimension.OVERWORLD, version, structureSeed);

        if (dtPos.distanceTo(CPos.ZERO, DistanceMetric.CHEBYSHEV) > CHUNK_DIST){
            return seeds;
        }

        TerrainGenerator otg = TerrainGenerator.of(obs);
        dtg.generate(otg, dtPos);

        boolean hasIron = checkChest(structureSeed, Items.IRON_INGOT, 7);
        boolean hasSufficient = checkChest(structureSeed, Items.IRON_INGOT, 4) && checkChest(structureSeed, Items.DIAMOND, 3);
        boolean hadFood = checkChest(structureSeed, Items.ROTTEN_FLESH, 14);

        if (!((hasIron || hasSufficient) && hadFood)){
            return seeds;
        }
        IO.println(String.format("Found a hit %s", structureSeed));
        WorldSeed.getSisterSeeds(structureSeed).asStream().boxed().limit(100).forEach(fullWorldSeed ->
        {
            BiomeSource sobs = BiomeSource.of(Dimension.OVERWORLD, version, fullWorldSeed);
            CPos spawnPoint = SpawnPoint.getApproximateSpawn((OverworldBiomeSource) sobs).toChunkPos();
            if (!(dt.canSpawn(dtPos, sobs))){
                return;
            }

            if (spawnPoint.distanceTo(dtPos, DistanceMetric.CHEBYSHEV) > CHUNK_DIST) {
                return;
            }
            seeds.add(fullWorldSeed);
        });

        return seeds;
    }

    private boolean checkChest(long structureSeed, Item item, int count){
        var loot = dt.getLoot(structureSeed, dtg, rand, false);

        boolean itemCheck = false;
        for (var chest: loot) {
            if (chest.containsAtLeast(item, count)) {
                itemCheck = true;
                break;
            }
        }
        return itemCheck;
    }
}

